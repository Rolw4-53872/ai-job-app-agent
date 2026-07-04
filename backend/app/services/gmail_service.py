import os
import base64
import logging
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

class GmailService:
    @staticmethod
    def get_auth_url() -> str:
        """Get the URL to redirect the user to for Google OAuth consent."""
        if settings.MOCK_MODE or not settings.GMAIL_CLIENT_ID:
            logger.info("Gmail Service in Mock Mode. Returning mock OAuth URL.")
            return "http://localhost:8000/api/auth/google/mock-consent"
            
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = settings.GMAIL_REDIRECT_URI
        authorization_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return authorization_url

    @staticmethod
    def save_token_from_code(code: str) -> None:
        """Exchange the OAuth authorization code for credentials and save to token.json."""
        if settings.MOCK_MODE or not settings.GMAIL_CLIENT_ID:
            logger.info("Gmail Service in Mock Mode. Saving mock credentials.")
            with open(settings.GMAIL_TOKEN_PATH, 'w') as f:
                f.write('{"mock": true}')
            return
            
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = settings.GMAIL_REDIRECT_URI
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        with open(settings.GMAIL_TOKEN_PATH, 'w') as token_file:
            token_file.write(credentials.to_json())
        logger.info("Gmail credentials saved successfully.")

    @classmethod
    def _get_credentials(cls) -> Credentials:
        """Load credentials from token.json."""
        if not os.path.exists(settings.GMAIL_TOKEN_PATH):
            return None
        return Credentials.from_authorized_user_file(settings.GMAIL_TOKEN_PATH, SCOPES)

    @classmethod
    async def send_email(cls, to: str, subject: str, body: str) -> str:
        """Send an email using Gmail API. Returns the gmail message ID."""
        if settings.MOCK_MODE or not os.path.exists(settings.GMAIL_TOKEN_PATH):
            logger.info(f"[Mock Send Email] To: {to}, Subject: {subject}, Body Snippet: {body[:60]}...")
            import uuid
            return f"mock-msg-{uuid.uuid4().hex[:12]}"
            
        creds = cls._get_credentials()
        if not creds:
            raise Exception("Gmail API Credentials not authorized. Complete OAuth flow first.")
            
        # Build the message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        service = build('gmail', 'v1', credentials=creds)
        try:
            sent_message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
            logger.info(f"Email sent successfully. Message ID: {sent_message['id']}")
            return sent_message['id']
        except Exception as e:
            logger.error(f"Error sending email via Gmail: {str(e)}")
            raise e

    @classmethod
    async def poll_replies(cls, query: str = "is:unread") -> list:
        """Poll the Gmail inbox for unread responses. Returns list of messages."""
        if settings.MOCK_MODE or not os.path.exists(settings.GMAIL_TOKEN_PATH):
            logger.info("Gmail Service in Mock Mode. Skipping poll.")
            return []
            
        creds = cls._get_credentials()
        if not creds:
            logger.warning("Gmail credentials missing. Skipping poll.")
            return []
            
        service = build('gmail', 'v1', credentials=creds)
        try:
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            detailed_replies = []
            for msg in messages:
                msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                
                # Extract headers
                headers = msg_details.get('payload', {}).get('headers', [])
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown")
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                
                # Get body
                parts = msg_details.get('payload', {}).get('parts', [])
                body = ""
                if not parts:
                    body_data = msg_details.get('payload', {}).get('body', {}).get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                else:
                    for part in parts:
                        if part.get('mimeType') == 'text/plain':
                            part_data = part.get('body', {}).get('data', '')
                            if part_data:
                                body = base64.urlsafe_b64decode(part_data).decode('utf-8', errors='ignore')
                                break
                                
                detailed_replies.append({
                    "gmail_message_id": msg['id'],
                    "sender": sender,
                    "subject": subject,
                    "body": body
                })
                
                # Mark as read (optional, can be done after processing)
                service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': [msg['id']],
                        'removeLabelIds': ['UNREAD']
                    }
                ).execute()
                
            return detailed_replies
        except Exception as e:
            logger.error(f"Error polling Gmail: {str(e)}")
            return []
