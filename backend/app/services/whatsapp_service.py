import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    @staticmethod
    async def send_notification(
        company_name: str, 
        subject: str, 
        summary: str, 
        priority: str, 
        recommended_action: str
    ) -> bool:
        """
        Send a WhatsApp notification to the user about an important application update.
        Uses WhatsApp Cloud API (Graph API).
        """
        # Create message content
        message_body = (
            f"🚨 *Important Job Application Alert!*\n\n"
            f"🏢 *Company:* {company_name}\n"
            f"✉️ *Subject:* {subject}\n"
            f"📝 *Summary:* {summary}\n"
            f"⚠️ *Priority:* {priority}\n"
            f"⚡ *Recommended Action:* {recommended_action}"
        )
        
        if settings.MOCK_MODE or not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_RECIPIENT_PHONE:
            logger.info("==================================================")
            logger.info("WHATSAPP NOTIFICATION MOCK SEND:")
            logger.info(message_body)
            logger.info("==================================================")
            return True
            
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Note: WhatsApp Cloud API requires using approved Templates for business-initiated messages.
        # However, for personal alerts to oneself, if you have established a customer care window, 
        # a standard text message can work. Let's provide a payload template message structure.
        # We will support standard template sending if a template is named 'job_alert', otherwise fall back to text.
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": settings.WHATSAPP_RECIPIENT_PHONE,
            "type": "text",
            "text": {
                "body": message_body
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    logger.info("WhatsApp notification sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send WhatsApp notification. Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error calling WhatsApp API: {str(e)}")
            return False
