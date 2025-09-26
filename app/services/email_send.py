from typing import List

from typing import List
import httpx
from app.core.config import settings


class BrevoEmailSending:
    def __init__(self, to_emails: List[str], subject: str, html_content: str):
        self.to_emails = [email.strip() for email in to_emails.split(",") if email.strip()]  if type(to_emails) == str else to_emails
        self.subject = subject
        self.html_content = html_content
        self.api_url = "https://api.brevo.com/v3/smtp/email"
        self.api_key = settings.BREVO_API_KEY
        self.sender_email = settings.BREVO_SENDER_EMAIL
        self.sender_name = "API Monitoring" 
    async def send_email_handle_log(self, payload: dict) -> bool:
        """Handles sending email and logs response."""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "accept": "application/json",
                        "api-key": self.api_key,
                        "content-type": "application/json"
                    }
                )
                response.raise_for_status()
                res_json = response.json()
                return "messageId" in res_json
            except httpx.HTTPStatusError as e:
                print(f"brevo HTTP error {e.response.status_code}: {e.response.text}")
                return False
            except httpx.RequestError as e:
                print(f"brevo request error: {e}")
                return False

    async def send_email(self) -> bool:
        """Prepares payload and sends email."""
        payload = {
            "sender": {
                "email": self.sender_email,
                "name": self.sender_name
            },
            "to": [{"email": email} for email in self.to_emails],
            "subject": self.subject,
            "htmlContent": self.html_content
        }
        return await self.send_email_handle_log(payload)
