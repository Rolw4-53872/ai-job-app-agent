from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import ReplyResponse, ReplyWebhookInput
from app.models.models import User, Application, Reply, Notification, Company, ActivityLog
from app.api.deps import get_current_user
from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService

router = APIRouter()

@router.get("/", response_model=List[ReplyResponse])
def list_replies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all analyzed recruiter replies."""
    return db.query(Reply).join(Application).filter(
        Application.user_id == current_user.id
    ).order_by(Reply.processed_at.desc()).all()

@router.get("/{id}", response_model=ReplyResponse)
def get_reply(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single reply."""
    reply = db.query(Reply).join(Application).filter(
        Reply.id == id,
        Application.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    return reply

@router.post("/webhook", response_model=ReplyResponse)
async def process_incoming_reply(
    input_data: ReplyWebhookInput,
    db: Session = Depends(get_db)
):
    """
    Webhook for n8n or Gmail watch event to push a new incoming recruiter message.
    Performs AI reply classification, updates application status, 
    and sends WhatsApp alerts for high priority matches.
    """
    # 1. Match reply to an active application
    # We match by searching if the sender email matches or contains the company name, 
    # or matches the recipient email of a sent email, or matches the company domain.
    sender_email = input_data.sender.lower()
    
    # Try to find email sent to this sender address first
    application_id = None
    matched_app = None
    
    # Search via exact email match first
    matched_email = db.query(Application).join(Company).filter(
        Company.hiring_email.ilike(f"%{sender_email}%") | 
        Company.website.ilike(f"%{sender_email.split('@')[-1]}%")
    ).order_by(Application.updated_at.desc()).first()
    
    if matched_email:
        matched_app = matched_email
    else:
        # Fallback: get the most recently updated application that is 'Sent' or 'Delivered'
        matched_app = db.query(Application).filter(
            Application.status.in_(["Sent", "Delivered"])
        ).order_by(Application.updated_at.desc()).first()
        
    if not matched_app:
        # If absolutely no sent application, match first application overall, or fail gracefully
        matched_app = db.query(Application).order_by(Application.updated_at.desc()).first()
        if not matched_app:
            raise HTTPException(status_code=404, detail="No active application found to match this reply.")

    # 2. Extract Application details for LLM context
    app_context = {
        "company_name": matched_app.company.name,
        "company_industry": matched_app.company.industry,
        "job_title": matched_app.job.title if matched_app.job else "Developer",
        "current_status": matched_app.status
    }
    
    # 3. Analyze reply using AI
    analysis = await AIService.analyze_reply(input_data.body, app_context)
    classification = analysis.get("classification", "General inquiry")
    priority = analysis.get("priority", "Low")
    summary = analysis.get("summary", "New reply received.")
    suggested_reply = analysis.get("suggested_reply", "")
    
    # 4. Save Reply to DB
    # Check if reply message id already processed
    existing_reply = db.query(Reply).filter(Reply.gmail_message_id == input_data.gmail_message_id).first()
    if existing_reply:
         return existing_reply
         
    reply = Reply(
        application_id=matched_app.id,
        gmail_message_id=input_data.gmail_message_id,
        sender=input_data.sender,
        subject=input_data.subject,
        body=input_data.body,
        classification=classification,
        summary=summary,
        priority=priority,
        suggested_reply=suggested_reply
    )
    db.add(reply)
    
    # 5. Update Application Status based on classification
    old_status = matched_app.status
    new_status = "Replied"
    if classification == "Interview invitation":
        new_status = "Interview"
    elif classification == "Assessment":
        new_status = "Assessment"
    elif classification == "Rejection":
        new_status = "Rejected"
    elif classification == "Acceptance" or classification == "Offer":
        new_status = "Offer"
        
    matched_app.status = new_status
    
    # Log status update activity
    log = ActivityLog(
        user_id=matched_app.user_id,
        action="reply_processed",
        details={
            "application_id": str(matched_app.id),
            "company": matched_app.company.name,
            "classification": classification,
            "old_status": old_status,
            "new_status": new_status
        }
    )
    db.add(log)
    
    # 6. Send WhatsApp Notification if priority is High/Urgent or classification is critical
    important_classes = ["Interview invitation", "Assessment", "Offer", "Acceptance"]
    is_important = (priority in ["High", "Urgent"]) or (classification in important_classes)
    
    if is_important:
        user_profile = matched_app.user.profile
        recipient_phone = user_profile.phone_number if user_profile and user_profile.phone_number else settings.WHATSAPP_RECIPIENT_PHONE
        
        if recipient_phone:
            # Set target phone for runtime
            settings.WHATSAPP_RECIPIENT_PHONE = recipient_phone
            
        recommended_action = "Schedule time using link / Check dashboard to review reply."
        if classification == "Interview invitation":
            recommended_action = "Urgent: Book interview time slot & review prep material."
        elif classification == "Assessment":
            recommended_action = "Schedule 2-3 hours for coding assessment."
        elif classification == "Offer":
            recommended_action = "Review offer contract details and salary."
            
        # Dispatch WhatsApp SMS
        whatsapp_sent = await WhatsAppService.send_notification(
            company_name=matched_app.company.name,
            subject=input_data.subject,
            summary=summary,
            priority=priority,
            recommended_action=recommended_action
        )
        
        # Save notification history in DB
        notif = Notification(
            user_id=matched_app.user_id,
            application_id=matched_app.id,
            type="WhatsApp",
            recipient=recipient_phone or "Default Phone",
            content=summary,
            sent_status="Sent" if whatsapp_sent else "Failed"
        )
        db.add(notif)
        
    db.commit()
    db.refresh(reply)
    return reply
