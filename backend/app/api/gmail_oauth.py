from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gmail_service import GmailService
from app.api.deps import get_current_user
from app.models.models import User, ActivityLog

router = APIRouter()

@router.get("/gmail/auth-url")
def get_gmail_auth_url(current_user: User = Depends(get_current_user)):
    """Retrieve Google OAuth Consent url to link Gmail account."""
    auth_url = GmailService.get_auth_url()
    return {"url": auth_url}

@router.get("/gmail/callback")
def gmail_oauth_callback(
    code: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Callback URL where Google redirects the user after authentication.
    Exchanges authorization code for tokens and saves credentials.
    """
    if error:
        return HTMLResponse(
            content=f"<h3>Authentication Failed</h3><p>Error: {error}</p>",
            status_code=400
        )
        
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
        
    try:
        # Save token
        GmailService.save_token_from_code(code)
        
        # Log event for first user (in production, map token to specific user id)
        user = db.query(User).first()
        if user:
            log = ActivityLog(
                user_id=user.id,
                action="gmail_authenticated",
                details={"status": "success"}
            )
            db.add(log)
            db.commit()
            
        # Return success screen with auto-close or redirect
        return HTMLResponse(content="""
            <html>
                <body style="font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #0f172a; color: #f8fafc;">
                    <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); text-align: center;">
                        <h2 style="color: #38bdf8; margin-bottom: 1rem;">Authentication Successful!</h2>
                        <p style="color: #94a3b8; margin-bottom: 2rem;">Your Gmail account is linked successfully to the Job Application Agent.</p>
                        <button onclick="window.close()" style="background-color: #0284c7; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 600; cursor: pointer;">Close Window</button>
                    </div>
                    <script>
                        setTimeout(function() { window.close(); }, 5000);
                    </script>
                </body>
            </html>
        """)
    except Exception as e:
        return HTMLResponse(
            content=f"<h3>Token Exchange Failed</h3><p>{str(e)}</p>",
            status_code=500
        )
