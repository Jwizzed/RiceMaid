import json
import os
from pathlib import Path
import tempfile
from fastapi import APIRouter, HTTPException, Request, status
from linebot.v3 import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    TextMessage,
    ReplyMessageRequest,
    MessagingApiBlob,
    ShowLoadingAnimationRequest,
    FlexMessage,
    FlexContainer,
)

from app.core.config import get_settings
from app.core.model import image_prediction

router = APIRouter()

PROJECT_DIR = Path(__file__).parent.parent.parent.parent

settings = get_settings()
configuration = Configuration(access_token=settings.line.channel_access_token)
handler = WebhookHandler(settings.line.channel_secret)


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
    Handle incoming text messages from the LINE chat bot.
    Responds with a simple echo of the received text using the ApiClient and MessagingApi.
    """
    received_text: str = event.message.text
    user_id: str = event.source.user_id

    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=f"Received: {received_text}")]
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

            bubble_content = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
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
                            "text": predicted_label,
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
