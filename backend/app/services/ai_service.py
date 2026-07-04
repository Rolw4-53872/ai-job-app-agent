import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    async def _call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Helper to call OpenAI or compatible API. Falls back to mock data if key not set or mock mode is enabled."""
        if settings.MOCK_MODE or not settings.OPENAI_API_KEY:
            logger.info("AI Service in Mock Mode. Returning mock response.")
            return ""

        url = settings.OPENAI_API_BASE or "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise e

    @classmethod
    async def parse_resume(cls, resume_text: str) -> Dict[str, Any]:
        """Extract skills, experience, projects, backend/AI/ML experience from resume text."""
        system_prompt = (
            "You are an expert recruiter and CV parser. Output a JSON object summarizing the candidate's details. "
            "The JSON must have the following keys:\n"
            "- skills: List of technical skills\n"
            "- programming_languages: List of programming languages\n"
            "- experience: List of jobs, each with company, title, duration, and bullet points\n"
            "- projects: List of projects, each with name, description, technologies used\n"
            "- ai_experience: Detailed summary of Artificial Intelligence, LLMs, Prompt Engineering, Agentic systems experience\n"
            "- ml_experience: Summary of Machine Learning models, libraries, and frameworks experience\n"
            "- ds_experience: Summary of Data Science, data analysis, visualization, statistics experience\n"
            "- backend_experience: Summary of Backend architecture, APIs (FastAPI, Flask, etc.), databases, system design experience\n"
            "Format the output strictly as JSON."
        )
        
        user_prompt = f"Parse the following resume text:\n\n{resume_text}"
        
        response_text = await cls._call_llm(system_prompt, user_prompt, json_mode=True)
        
        if not response_text:
            # Return Mock Data
            return {
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "PyTorch", "scikit-learn", "LangChain"],
                "programming_languages": ["Python", "SQL", "JavaScript"],
                "experience": [
                    {
                        "company": "DeepTech Innovations",
                        "title": "Machine Learning Engineer",
                        "duration": "2024 - Present",
                        "description": "Developed and deployed LLM-powered agents and RAG pipelines using FastAPI and LangChain."
                    },
                    {
                        "company": "Enterprise Software Corp",
                        "title": "Software Engineer (Backend)",
                        "duration": "2022 - 2024",
                        "description": "Built scalable RESTful microservices in Python and PostgreSQL. Optimized query execution."
                    }
                ],
                "projects": [
                    {
                        "name": "DocuMind Chatbot",
                        "description": "A RAG system for chatting with complex corporate documentation.",
                        "technologies": ["Python", "LangChain", "OpenAI", "Pinecone"]
                    }
                ],
                "ai_experience": "2+ years building agentic workflows, langchain applications, custom fine-tuning, prompt engineering.",
                "ml_experience": "Strong knowledge of machine learning classification models, gradient boosting (XGBoost), and neural networks.",
                "ds_experience": "Proficient in Pandas, NumPy, Jupyter, data profiling, and statistical analysis.",
                "backend_experience": "4 years developing scalable REST APIs, FastAPI apps, relational database models, Docker containers."
            }
        
        return json.loads(response_text)

    @classmethod
    async def research_company(cls, company_name: str, website: Optional[str] = None) -> Dict[str, Any]:
        """Perform research on a company. In production, this can perform web queries."""
        # Note: A real implementation would run web searches (e.g. via Tavily or Serper) and feed that to LLM.
        # Since we want to make it robust, we'll use LLM knowledge with a search mockup description.
        system_prompt = (
            "You are a business intelligence researcher. Analyze the target company. Output a JSON object containing:\n"
            "- description: Summary of company mission, target audience, business model\n"
            "- industry: Primary industry classification\n"
            "- products: Major products or service categories\n"
            "- technologies: Apparent/likely tech stack (e.g. React, Python, AWS, GCP, etc.)\n"
            "- career_page: Likely careers page URL or general domain carrier page\n"
            "- hiring_email: Public hiring/contact email if known or likely format (e.g. jobs@company.com)\n"
            "- hr_contact: Public HR contact info or general LinkedIn hiring pattern if known\n"
            "Format the output strictly as JSON."
        )
        
        website_part = f" (Website: {website})" if website else ""
        user_prompt = f"Research and summarize the company named: {company_name}{website_part}"
        
        response_text = await cls._call_llm(system_prompt, user_prompt, json_mode=True)
        
        if not response_text:
            # Return Mock Data
            return {
                "description": f"{company_name} is a leading tech innovator focused on building advanced data intelligence platforms for enterprise clients.",
                "industry": "Software / Artificial Intelligence",
                "products": ["DataCore AI Platform", "Predictive Analytics Suite"],
                "technologies": ["Python", "FastAPI", "React", "AWS", "Docker", "PostgreSQL"],
                "career_page": f"https://www.{company_name.lower().replace(' ', '')}.com/careers",
                "hiring_email": f"careers@{company_name.lower().replace(' ', '')}.com",
                "hr_contact": "Talent Acquisition Team"
            }
            
        return json.loads(response_text)

    @classmethod
    async def generate_email(
        cls, 
        profile_data: Dict[str, Any], 
        company_data: Dict[str, Any], 
        job_data: Dict[str, Any], 
        style: str = "professional", 
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a personalized application email."""
        system_prompt = (
            "You are an expert copywriter and professional career coach. Generate a highly personalized, compelling, "
            "non-generic application email for a candidate applying to a company. "
            "Output a JSON object with the following fields:\n"
            "- subject: Attention-grabbing professional subject line\n"
            "- body: Complete email body with standard placeholders filled. Address the company/contact nicely.\n"
            "- rationale: Paragraph explaining why this email was written this way, citing how it connects the candidate's "
            "specific experience to the company's tech/products.\n"
            "Make sure the email does not look like a template. Fit it to the requested style: Professional, Warm, Bold, Concise, or Technical."
        )
        
        user_prompt = (
            f"Candidate Info:\n{json.dumps(profile_data, indent=2)}\n\n"
            f"Company Info:\n{json.dumps(company_data, indent=2)}\n\n"
            f"Job Details:\n{json.dumps(job_data, indent=2)}\n\n"
            f"Writing Style: {style}\n"
            f"Additional Instructions: {additional_instructions or 'None'}"
        )
        
        response_text = await cls._call_llm(system_prompt, user_prompt, json_mode=True)
        
        if not response_text:
            # Return Mock Data
            subject = f"AI / Backend Engineer Role - {profile_data.get('full_name', 'Applicant')}"
            body = (
                f"Dear {company_data.get('hr_contact', 'Hiring Team')} at {company_data.get('name', 'Company')},\n\n"
                f"I am writing to express my strong interest in the {job_data.get('title', 'Developer')} position. "
                f"I've been following {company_data.get('name')}'s work in the {company_data.get('industry')} sector, "
                f"particularly your flagship product: {', '.join(company_data.get('products', ['products']))}. "
                f"I believe my background as an AI and Backend Engineer makes me a great fit.\n\n"
                f"With {profile_data.get('years_of_experience', 3)} years of experience building scalable APIs in FastAPI and deploying ML models, "
                f"I am excited by the prospect of contributing to your tech stack, which matches my expertise in "
                f"{', '.join(company_data.get('technologies', ['Python', 'Docker', 'PostgreSQL'])[:4])}.\n\n"
                f"Thank you for your time and consideration. I would love to connect and share more about how my background aligns with your vision.\n\n"
                f"Best regards,\n"
                f"{profile_data.get('full_name', 'Applicant')}\n"
                f"{profile_data.get('phone_number', '')} | {profile_data.get('email', '')}\n"
                f"{profile_data.get('linkedin_url', '')}"
            )
            rationale = (
                f"This email directly targets {company_data.get('name')}'s industry and highlights the candidate's core "
                f"skills matching their tech stack ({', '.join(company_data.get('technologies', [])[:3])}). "
                f"It mentions their product '{company_data.get('products', [''])[0]}' to show genuine interest and research."
            )
            return {
                "subject": subject,
                "body": body,
                "rationale": rationale
            }
            
        return json.loads(response_text)

    @classmethod
    async def analyze_reply(cls, reply_body: str, application_context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a reply email from a recruiter or company, draft a suggested response."""
        system_prompt = (
            "You are an AI Job application assistant. Analyze the incoming reply from a company. "
            "Output a JSON object with the following fields:\n"
            "- classification: One of: 'Interview invitation', 'Assessment', 'Need more info', 'Acceptance', 'Rejection', 'General inquiry', 'Automatic response'\n"
            "- summary: A concise 1-2 sentence summary of what the email is about and what they want\n"
            "- priority: One of: 'Low', 'Medium', 'High', 'Urgent' (e.g. interview invitations are Urgent/High)\n"
            "- suggested_reply: A professional suggested reply for the candidate to send back if action is needed. Keep placeholders clear.\n"
            "Format the output strictly as JSON."
        )
        
        user_prompt = (
            f"Application Context:\n{json.dumps(application_context, indent=2)}\n\n"
            f"Incoming Email Body:\n{reply_body}"
        )
        
        response_text = await cls._call_llm(system_prompt, user_prompt, json_mode=True)
        
        if not response_text:
            # Return Mock Data
            return {
                "classification": "Interview invitation",
                "summary": "The recruiter has requested a 30-minute introductory call and shared a Calendly link.",
                "priority": "High",
                "suggested_reply": (
                    "Hi [Sender Name],\n\n"
                    "Thank you for the update! I would be thrilled to jump on an introductory call. "
                    "I will schedule a slot using your Calendly link right away. "
                    "Looking forward to speaking with you!\n\n"
                    "Best regards,\n"
                    "[Candidate Name]"
                )
            }
            
        return json.loads(response_text)

    @classmethod
    async def assistant_chat(cls, user_message: str, application_stats_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assistant chatbot responding to user status queries."""
        system_prompt = (
            "You are the AI Job Application Assistant. You help the user manage their job search, "
            "analyze stats, recommend email updates, and list statuses. "
            "You are given context about their applications:\n"
            f"{json.dumps(application_stats_context, indent=2)}\n\n"
            "Answer the user's questions clearly, concisely, and with a friendly, professional tone. "
            "Identify if they want to take an action (like generating an email or showing rejected companies) "
            "and suggest interactive actions. Output a JSON object with keys:\n"
            "- response: Your conversational reply\n"
            "- suggested_actions: A list of dicts like [{'label': 'View Approvals', 'action': 'redirect_approvals'}, "
            "{'label': 'See Applications', 'action': 'redirect_applications'}]"
        )
        
        response_text = await cls._call_llm(system_prompt, user_message, json_mode=True)
        
        if not response_text:
            # Return Mock Data based on standard queries
            msg_lower = user_message.lower()
            if "interview" in msg_lower:
                response = f"You currently have {application_stats_context.get('interviews_count', 0)} active interview invitation(s). You can view them in the applications dashboard."
                actions = [{"label": "View Applications", "action": "redirect_applications"}]
            elif "reject" in msg_lower:
                response = f"You have {application_stats_context.get('rejected_count', 0)} rejected application(s). Keep your head up, let's keep searching for new opportunities!"
                actions = [{"label": "Search Jobs", "action": "redirect_jobs"}]
            elif "not replied" in msg_lower:
                response = f"You have {application_stats_context.get('pending_replies', 0)} application(s) awaiting replies."
                actions = [{"label": "View Applications", "action": "redirect_applications"}]
            else:
                response = "Hello! I am your AI Job Application Assistant. I can help you search for jobs, analyze recruiter replies, draft emails, and track application stats. What would you like to do today?"
                actions = [
                    {"label": "View Approvals", "action": "redirect_approvals"},
                    {"label": "Search Jobs", "action": "redirect_jobs"}
                ]
            return {
                "response": response,
                "suggested_actions": actions
            }
            
        return json.loads(response_text)
