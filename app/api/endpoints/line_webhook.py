from datetime import datetime, timedelta
import re
import json
import os
import tempfile
from pathlib import Path
import requests
from typing import List, Optional, Dict, Any

import google.generativeai as genai
from google.generativeai.protos import Content, Part

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

from app.api.endpoints.carbon_credit import estimate_methane_emission
from app.core.config import get_settings
from app.core.dummy import generate_dummy_field_stats, generate_dummy_field_water_levels, generate_weather_mock_data
from app.core.model import image_prediction

from tavily import TavilyClient

from app.enum.province import Province
from app.models import FieldStats

router = APIRouter()

PROJECT_DIR = Path(__file__).parent.parent.parent.parent

settings = get_settings()
configuration = Configuration(access_token=settings.line.channel_access_token)
handler = WebhookHandler(settings.line.channel_secret)

tavily_client = TavilyClient(api_key=settings.llm.tavily_api_key)

chat_sessions = {}
chat_states = {}
genai.configure(api_key=settings.llm.gemini_access_key)

GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


# https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load?basin_code=10,11,12,13,15
# https://api-v3.thaiwater.net/api/v1/thaiwater30/public/rain_24h?basin_code=10,11,12,13,15
# https://api-v3.thaiwater.net/api/v1/thaiwater30/public/watergate_load?basin_code=10,11,12,13,15


def fetch_water_resources_data(
    resource_type: str,
    interval: str,
    latest: bool,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    province_code: Optional[str] = None,
    amphoe_code: Optional[str] = None,
    tambon_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch water resource data from the specified API (Medium or Small).

    Args:
        resource_type (str): The resource type ('Medium' or 'Small').
        interval (str): The data interval (e.g., 'P-Daily' or 'Daily').
        latest (bool): Whether to fetch the latest data.
        start_datetime (str, optional): Start datetime (required if latest is False). Format: yyyy-MM-ddTHH:mm:ss.
        end_datetime (str, optional): End datetime (required if latest is False). Format: yyyy-MM-ddTHH:mm:ss.
        province_code (str, optional): Province code filter.
        amphoe_code (str, optional): Amphoe (district) code filter.
        tambon_code (str, optional): Tambon (sub-district) code filter.

    Returns:
        Dict[str, Any]: The API response as a dictionary.

    Raises:
        ValueError: If required parameters are missing or invalid.
        RuntimeError: For issues during the API call.
    """
    base_urls = {
        "Medium": "https://api.dwr.go.th/twsapi/v1.0/MediumsizedWaterResources",
        "Small": "https://api.dwr.go.th/twsapi/v1.0/SmallsizedWaterResources",
    }

    if resource_type not in base_urls:
        raise ValueError("Invalid resource_type. Must be 'Medium' or 'Small'.")

    if not latest and (not start_datetime or not end_datetime):
        raise ValueError("start_datetime and end_datetime are required when 'latest' is False.")

    url = base_urls[resource_type]
    headers = {"Authorization": f"Bearer {settings.external.wstd_api_key}"}

    params: dict[str, str] = {"interval": interval, "latest": str(latest).lower()}
    if start_datetime:
        params["startDatetime"] = start_datetime
    if end_datetime:
        params["endDatetime"] = end_datetime
    if province_code:
        params["provinceCode"] = province_code
    if amphoe_code:
        params["amphoeCode"] = amphoe_code
    if tambon_code:
        params["tambonCode"] = tambon_code

    try:
        response = requests.get(url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching {resource_type} water resource data: {e}")


def get_farm_news():
    try:
        response = tavily_client.search("ข่าววันนี้สำหรับชาวนาไทย", search_depth="simple")
        results = response.get("results", [])

        if not results:
            return "ไม่พบข่าวสารใหม่สำหรับวันนี้ ลองอีกครั้งในภายหลัง"

        news = "ข่าวสำหรับชาวนาไทยวันนี้:\n"
        for i, item in enumerate(results[:3], 1):
            title = item.get("title", "ไม่มีหัวข้อ")
            url = item.get("url", "ไม่มีลิงก์")
            news += f"{i}. {title}\n{url}\n"

        return news.strip()
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {str(e)}"


def get_or_create_chat_session(user_id: str) -> genai.ChatSession:
    """Get existing chat session or create new one for user"""
    if user_id not in chat_sessions:
        context = [
            Content(
                role='user',
                parts=[
                    Part(text="คูณคือผู้ช่วยชาวนาไทยสำหรับการวิเคราะห์และตอบคำถามเกี่ยวกับการเกษตร"),
                    Part(text="และหลีกเลี่ยงการใช้ Markdown หรือรูปแบบการเขียนที่ซับซ้อน"),
                    Part(text="คุณมีความรู้อย่างลึกซึ้่งในการทำนาแบบเปียกสลับแห้งและเกี่ยวกับคาร์บอนเครดิต"),
                    Part(text="คุณสามารถวิเคราะห์ข้อมูลและสรุปออกมาเป็นข้อมูลทางสถิติที่เขาใจง่าย"),
                    Part(text="แม้ข้อมูลไม่เพียงพอคุณก็จะต้องตอบคำถามด้วยข้อมูลที่ผู้ใช้ป้อนให้"),
                    Part(text="ผู้ใช้ปลูกแค่ข้าวเท่านั้น"),
                    Part(text="คุณจะไม่ขอข้อมูลเพิ่มเติม"),
                    Part(text="ห้ามบอกว่าข้อมูลที่ให้มาน้อยไป"),
                ],
            )
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=GENERATION_CONFIG,
        )
        chat_sessions[user_id] = model.start_chat(history=context)
    return chat_sessions[user_id]


def set_chat_state(user_id: str, state: Optional[str] = None):
    chat_states[user_id] = state


def get_chat_state(user_id: str) -> Optional[str]:
    return chat_states.get(user_id)


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
        with ApiClient(configuration) as api_client:
            api_instance_loading = MessagingApi(api_client)
            show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
            api_instance_loading.show_loading_animation(show_loading_animation_request)

        state = get_chat_state(user_id)

        if "คำนวณคาร์บอนเครดิต" in received_text or "calculate carbon credit" in received_text:
            response_text = (
                "กรุณาตอบคำถามเพื่อคำนวณคาร์บอนเครดิต:\n"
                "1. จำนวนที่ดินกี่ไร่?\n"
                "2. อายุเก็บเกี่ยวข้าวในฤดูเพาะปลูก?\nตัวอย่าง\n5 ไร่, 120 วัน"
            )
            set_chat_state(user_id, "awaiting_carbon_credit_data")

        elif "ข่าววันนี้" in received_text or "news" in received_text:
            response_text = get_farm_news()

        elif "ภาพรวมนา" in received_text or "rice field overview" in received_text:
            water_levels = generate_dummy_field_water_levels(20)
            field_stats: List[FieldStats] = generate_dummy_field_stats(20)
            weather_data = genai.generate_weather_mock_data(datetime.now(), 7)

            water_level_data = [w.water_level for w in water_levels]
            soil_moisture_data = [s.soil_moisture for s in field_stats]
            weather_conditions = [w.condition for w in weather_data]
            weather_temperatures_min = [w.temperature_min for w in weather_data]
            weather_temperatures_max = [w.temperature_max for w in weather_data]
            weather_humidity = [w.humidity for w in weather_data]
            weather_wind_speed = [w.wind_speed for w in weather_data]

            additional_info = {
                "water_levels": water_level_data,
                "soil_moisture": soil_moisture_data,
                "weather_conditions": weather_conditions,
                "weather_temperatures_min": weather_temperatures_min,
                "weather_temperatures_max": weather_temperatures_max,
                "weather_humidity": weather_humidity,
                "weather_wind_speed": weather_wind_speed,
            }

            response_text = "ข้อมูลรายงานสถานการณ์นาและสิ่งแวดล้อม:\n" f"{additional_info}"

        elif "คำแนะนำ" in received_text or "recommendation" in received_text:
            response_text = (
                "ผมมีข้อมูลเรื่องนาและสภาพอากาศบริเวณของคุณอยู่แล้ว\nมีข้อมูลอะไรที่ต้องการเพิ่มเติมให้ผมไหมครับ "
                "เช่น ข้อมูลเรื่องปุ๋ยที่คุณใช้ในวันนี้หรือข้อมูลอื่นๆในช่วงเวลาที่ผ่านมาหรือขนาดพื้นที่"
            )
            set_chat_state(user_id, "waiting_recommendation")

        elif user_id in chat_sessions and state == "waiting_recommendation":
            # combine all possible data sources
            user_suggestion = received_text
            water_levels = generate_dummy_field_water_levels(20)
            field_stats: List[FieldStats] = generate_dummy_field_stats(20)
            weather_data = generate_weather_mock_data(datetime.now(), 7)

            water_level_data = [w.water_level for w in water_levels]
            soil_moisture_data = [s.soil_moisture for s in field_stats]
            weather_conditions = [w.condition for w in weather_data]
            weather_temperatures_min = [w.temperature_min for w in weather_data]
            weather_temperatures_max = [w.temperature_max for w in weather_data]
            weather_humidity = [w.humidity for w in weather_data]
            weather_wind_speed = [w.wind_speed for w in weather_data]

            additional_info = {
                "water_levels": water_level_data,
                "soil_moisture": soil_moisture_data,
                "weather_conditions": weather_conditions,
                "weather_temperatures_min": weather_temperatures_min,
                "weather_temperatures_max": weather_temperatures_max,
                "weather_humidity": weather_humidity,
                "weather_wind_speed": weather_wind_speed,
            }

            news_text = get_farm_news()
            environment_text = "ข้อมูลรายงานสถานการณ์นาและสิ่งแวดล้อม:\n" f"{additional_info}"

            combined_text = f"ให้เริ่มตอบด้วย 1 คำแนะนำ! นี่คือข้อมูลทั้งหมด ข่าว: {news_text}\n สภาพแวดล้อมและอากาศ: {environment_text}\nและข้อมูลเพิ่มเติมจากชาวไร่: {user_suggestion}\n แม้ข้อมูลไม่เพียงพอก็ต้องให้คำแนะนำ"
            chat_session = get_or_create_chat_session(user_id)
            response = chat_session.send_message(combined_text)
            response_text = response.text
            set_chat_state(user_id, None)

        elif "ข้อมูลน้ำ" in received_text or "water data" in received_text:
            response_text = "กรุณาพิมพ์ชื่อจังหวัดเพื่อรับข่าวน้ำวันนี้\n" "ตัวอย่าง: สุพรรณบุรี, นครราชสีมา"
            set_chat_state(user_id, "awaiting_province")

        elif user_id in chat_sessions and state == "awaiting_province":
            province_name = received_text
            province = next(
                (
                    prov
                    for prov in Province
                    if prov.value.name_th == province_name or prov.value.name_en == province_name
                ),
                None,
            )

            if province:
                province_code = province.value.code
                start_datetime = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
                end_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                smalL_data = fetch_water_resources_data(
                    resource_type="Small",
                    interval="P-Daily",
                    latest=False,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    province_code=str(province_code),
                )

                medium_data = fetch_water_resources_data(
                    resource_type="Medium",
                    interval="P-Daily",
                    latest=False,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    province_code=str(province_code),
                )

                chat_session = get_or_create_chat_session(user_id)
                medium_fetched_data_str = json.dumps(medium_data, ensure_ascii=False)
                small_fetched_data_str = json.dumps(smalL_data, ensure_ascii=False)
                summary_prompt = f"""
                    "สรุปข้อมูลเกี่ยวกับสถานการณ์น้ำในจังหวัดนี้ในช่วง 30 วันที่ผ่านมา:\n"
                    f"อ่างเก็บน้ำขนาดกลาง: {medium_fetched_data_str}"
                    f"อ่างเก็บน้ำขนาดเล็ก: {small_fetched_data_str}"
                    "\nให้สรุปข้อมูลด้านบนออกมาเป็นรายงานปริมาณน้ำและวิเคราะห์สถานการณ์น้ำในจังหวัดนี้"
                """
                response = chat_session.send_message(summary_prompt)
                response_text = response.text
                response_text = summary_prompt

                set_chat_state(user_id, None)
            else:
                response_text = "ไม่พบข้อมูลจังหวัด กรุณาลองใหม่อีกครั้งและระบุชื่อจังหวัดให้ถูกต้อง"
                set_chat_state(user_id, None)

        elif user_id in chat_sessions and state == "awaiting_carbon_credit_data":
            match = re.match(r"(\d+)\s*ไร่,\s*(\d+)\s*วัน", received_text)
            if match:
                area = float(match.group(1))
                harvest_age = int(match.group(2))

                methane_emission = estimate_methane_emission(area_rice_field=area, harvest_age=harvest_age)

                response_text = (
                    f"การคำนวณคาร์บอนเครดิต:\n"
                    f"พื้นที่: {area} ไร่\n"
                    f"อายุเก็บเกี่ยว: {harvest_age} วัน\n"
                    f"การปล่อยมีเทน: {methane_emission:.2f} กิโลกรัม CO2eq\n"
                    f"คาร์บอนเครดิตที่ได้: {methane_emission*1000:.2f} หน่วย"
                )
                chat_sessions[user_id] = None

            else:
                response_text = (
                    "ข้อมูลไม่ถูกต้อง\nโปรดถามอีกครั้ง\nกรุณาตอบตามรูปแบบนี้:\n"
                    "จำนวนที่ดิน (ไร่), อายุเก็บเกี่ยวข้าว (วัน)\n"
                    "ตัวอย่าง: 5 ไร่, 120 วัน"
                )
                set_chat_state(user_id, None)

        else:
            chat_session = get_or_create_chat_session(user_id)
            response = chat_session.send_message(received_text)
            response_text = str(response.text)

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=response_text)])
            )

    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message_with_http_info(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=error_message)])
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
