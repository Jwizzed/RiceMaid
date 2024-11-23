import json
import os
import tempfile
from pathlib import Path

import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Request, status
from linebot.exceptions import InvalidSignatureError
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexContainer,
    FlexMessage,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    TextMessage,
)
from linebot.v3.webhooks import ImageMessageContent, MessageEvent, TextMessageContent

from app.core.config import get_settings
from app.core.model import image_prediction

router = APIRouter()

PROJECT_DIR = Path(__file__).parent.parent.parent.parent

settings = get_settings()
configuration = Configuration(access_token=settings.line.channel_access_token)
handler = WebhookHandler(settings.line.channel_secret)

chat_sessions = {}
genai.configure(api_key="AIzaSyCmqgD1yujkJRSYzeC9foqtzTnse1AmKAk")

GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def get_or_create_chat_session(user_id: str) -> genai.ChatSession:
    """Get existing chat session or create new one for user"""
    if user_id not in chat_sessions:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=GENERATION_CONFIG,
        )
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    description="Handle LINE webhook events",
)
async def line_webhook(request: Request) -> dict:
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature header.")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature.")

    return {"message": "Webhook processed successfully."}


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent) -> None:
    """
    Handle incoming text messages and respond using Gemini LLM.
    """
    received_text: str = event.message.text
    user_id: str = event.source.user_id

    try:
        chat_session = get_or_create_chat_session(user_id)

        response = chat_session.send_message(received_text)
        response_text = response.text

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)]
                )
            )

    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=error_message)]
                )
            )


@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event: MessageEvent) -> None:
    """
    Handle incoming image messages from the LINE chat bot.
    Processes the image and responds with the prediction.
    """
    user_id: str = event.source.user_id
    message_id = event.message.id

    with ApiClient(configuration) as api_client:
        api_instance = MessagingApiBlob(api_client)
        message_content = api_instance.get_message_content(message_id)
        api_instance_loading = MessagingApi(api_client)
        show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
        api_instance_loading.show_loading_animation(show_loading_animation_request)

        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(message_content)
            temp_file_path = temp_file.name

        try:
            weights_path = f"{PROJECT_DIR}/assets/weight/effb3_300.h5"
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"Weights file not found at: {weights_path}")

            predicted_label, probability = image_prediction.predict_image(
                image_path=temp_file_path,
                weights_path=weights_path,
                im_height=300,
                im_width=300,
            )

            label_mapping = {"BBCH11": "ระยะกล้า", "BBCH12": "ระยะยืดปล้อง", "BBCH13": "ระยะตั้งท้อง"}

            show_label = label_mapping.get(predicted_label, "Unknown stage")
            image_urls = {
                "BBCH11": "https://i.ibb.co/gR5bfDX/BBCH11.jpg",
                "BBCH12": "https://i.ibb.co/dbSjLg4/BBCH12.jpg",
                "BBCH13": "https://i.ibb.co/WDkVvYJ/BBCH13.jpg",
            }
            image_url = image_urls.get(predicted_label, "https://example.com/default_image.png")

            bubble_content = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": image_url,
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {"type": "uri", "uri": "https://line.me/"},
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": show_label,
                            "weight": "bold",
                            "size": "xl",
                        }
                    ],
                },
            }

            bubble_string = json.dumps(bubble_content)
            flex_message = FlexMessage(
                alt_text=f"{predicted_label} Prediction | Probability: {probability:.2f}",
                contents=FlexContainer.from_json(bubble_string),
            )

            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[flex_message],
                )
            )
        except Exception as e:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=f"Error processing the image: {str(e)}")],
                )
            )

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
