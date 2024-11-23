import os
import tempfile
from fastapi import APIRouter, HTTPException, Request, status
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage
from app.core.config import get_settings
from app.core.model import image_prediction

router = APIRouter()

settings = get_settings()
line_bot_api = LineBotApi(settings.line.channel_access_token)
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


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent) -> None:
    """
    Handle incoming text messages from the LINE chat bot.
    Responds with a simple echo of the received text.
    """
    received_text: str = event.message.text
    user_id: str = event.source.user_id

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Received: {received_text}"))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event: MessageEvent) -> None:
    """
    Handle incoming image messages from the LINE chat bot.
    Processes the image and responds with the prediction.
    """
    user_id: str = event.source.user_id

    message_content = line_bot_api.get_message_content(event.message.id)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in message_content.iter_content():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    try:
        weights_path = "../assets/weight/effb3_300.h5"
        predicted_label, probability = image_prediction.predict_image(
            image_path=temp_file_path,
            weights_path=weights_path,
            im_height=300,
            im_width=300,
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"Prediction with probability {probability:.2f}"),
        )
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"Error processing the image: {str(e)}"),
        )

    os.remove(temp_file_path)
