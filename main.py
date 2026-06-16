from fastapi import (
    FastAPI,
    Request,
    HTTPException
)

from fastapi.responses import (
    PlainTextResponse
)

from dotenv import load_dotenv

from brain import (
    generate_reply
)

import requests
import os
import json


load_dotenv()

app = FastAPI()


WHATSAPP_TOKEN = os.getenv(
    "WHATSAPP_TOKEN"
)

PHONE_NUMBER_ID = os.getenv(
    "PHONE_NUMBER_ID"
)

VERIFY_TOKEN = os.getenv(
    "VERIFY_TOKEN"
)



def send_whatsapp_message(
    phone_number,
    message
):

    url = (
        f"https://graph.facebook.com/"
        f"v22.0/"
        f"{PHONE_NUMBER_ID}"
        f"/messages"
    )

    headers = {
        "Authorization":
            f"Bearer {WHATSAPP_TOKEN}",

        "Content-Type":
            "application/json"
    }

    payload = {
        "messaging_product":
            "whatsapp",

        "to":
            phone_number,

        "type":
            "text",

        "text": {
            "body":
                message[:4096]
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(
        "WhatsApp:",
        response.status_code
    )


@app.get("/")
async def home():

    return {
        "status":
        "running"
    }


@app.get("/webhook")
async def verify_webhook(
    request: Request
):

    mode = (
        request.query_params
        .get("hub.mode")
    )

    token = (
        request.query_params
        .get("hub.verify_token")
    )

    challenge = (
        request.query_params
        .get("hub.challenge")
    )

    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
    ):

        return PlainTextResponse(
            challenge
        )

    raise HTTPException(
        status_code=403,
        detail="Verification failed"
    )


@app.post("/webhook")
async def receive_message(
    request: Request
):

    body = await request.json()

    print(
        json.dumps(
            body,
            indent=2
        )
    )

    try:
        value = (
            body["entry"][0]
            ["changes"][0]
            ["value"]
        )

        # Ignore statuses
        if (
            "messages"
            not in value
        ):
            return {
                "status":
                "ignored"
            }

        message = (
            value["messages"][0]
        )

        sender_phone = (
            message["from"]
        )

        user_message = (
            message
            .get("text", {})
            .get("body", "")
        )

        print(
            "User:",
            user_message
        )

        ai_reply = generate_reply(
             user_message=user_message,
            user_id=sender_phone
        )

        print(
            "AI:",
            ai_reply
        )

        send_whatsapp_message(
            sender_phone,
            ai_reply
        )

    except Exception as e:
        print(
            "Error:",
            str(e)
        )

    return {
        "status":
        "success"
    }