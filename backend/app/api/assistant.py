from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import AssistantChatRequest, AssistantChatResponse
from app.models.models import User, Application
from app.api.deps import get_current_user
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    request: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chatbot endpoint. Collects application counts/metrics, feed details 
    as context to the AI assistant, and returns response with action cards.
    """
    # Build statistics context dynamically to feed the chatbot
    base_query = db.query(Application).filter(Application.user_id == current_user.id)
    
    total_apps = base_query.count()
    interviews = base_query.filter(Application.status == "Interview").count()
    pending_replies = base_query.filter(Application.status.in_(["Sent", "Delivered"])).count()
    rejections = base_query.filter(Application.status == "Rejected").count()
    offers = base_query.filter(Application.status == "Offer").count()
    
    # Retrieve a list of companies that haven't replied
    no_reply_companies = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.status.in_(["Sent", "Delivered"])
    ).all()
    
    no_reply_names = [app.company.name for app in no_reply_companies]
    
    # Retrieve a list of rejected applications
    rejected_companies = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.status == "Rejected"
    ).all()
    
    rejected_names = [app.company.name for app in rejected_companies]
    
    stats_context = {
        "total_applications": total_apps,
        "interviews_count": interviews,
        "pending_replies": pending_replies,
        "rejected_count": rejections,
        "offers_count": offers,
        "companies_with_no_reply": no_reply_names,
        "rejected_companies": rejected_names
    }
    
    # Process user prompt using context
    chat_result = await AIService.assistant_chat(request.message, stats_context)
    
    return AssistantChatResponse(
        response=chat_result.get("response", "I'm sorry, I encountered an issue processing your query."),
        suggested_actions=chat_result.get("suggested_actions", [])
    )
