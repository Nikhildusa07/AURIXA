from __future__ import annotations

import os
from typing import Any

import requests


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_email_notification(
    recipient_email: str,
    subject: str,
    message: str,
) -> dict[str, Any]:
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL")

    if not api_key:
        return {
            "success": False,
            "error": "BREVO_API_KEY is not configured.",
        }

    if not sender_email:
        return {
            "success": False,
            "error": "BREVO_SENDER_EMAIL is not configured.",
        }

    if not recipient_email.strip():
        return {
            "success": False,
            "error": "Recipient email cannot be empty.",
        }

    payload = {
        "sender": {
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient_email,
            }
        ],
        "subject": subject,
        "textContent": message,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            BREVO_API_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )

        if response.status_code in (200, 201, 202):
            data = response.json()

            return {
                "success": True,
                "message": "Email sent successfully.",
                "message_id": data.get("messageId"),
            }

        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code,
        }

    except requests.RequestException as exc:
        return {
            "success": False,
            "error": str(exc),
        }