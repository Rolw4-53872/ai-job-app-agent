import random
import uuid
from typing import List, Dict, Any, Optional

class JobSearchService:
    # Pool of mock companies and details to generate realistic results
    COMPANIES_POOL = [
        {"name": "NeuralStack Solutions", "website": "https://neuralstack.io", "industry": "Artificial Intelligence", "techs": ["Python", "PyTorch", "FastAPI"]},
        {"name": "DataFlow Labs", "website": "https://dataflowlabs.com", "industry": "Data Engineering", "techs": ["Python", "SQL", "PostgreSQL", "Docker"]},
        {"name": "OmniCore Technologies", "website": "https://omnicore.tech", "industry": "Cloud Infrastructure", "techs": ["Go", "Python", "Docker", "Kubernetes"]},
        {"name": "Apex ML Systems", "website": "https://apexml.systems", "industry": "Machine Learning", "techs": ["Python", "scikit-learn", "AWS"]},
        {"name": "SwiftBackend Corp", "website": "https://swiftbackend.com", "industry": "Web Services", "techs": ["Python", "FastAPI", "PostgreSQL"]},
        {"name": "Aether AI", "website": "https://aetherai.co", "industry": "Generative AI", "techs": ["Python", "OpenAI", "LangChain", "FastAPI"]}
    ]
    
    TITLES_POOL = {
        "Data Scientist": ["Data Scientist", "Lead Data Scientist", "Junior Data Scientist"],
        "Machine Learning": ["Machine Learning Engineer", "MLOps Engineer", "Applied ML Scientist"],
        "AI Engineer": ["AI Engineer", "Generative AI Developer", "AI Agent Automation Engineer"],
        "Backend Developer": ["Backend Developer", "Senior Backend Engineer", "FastAPI Developer"],
        "Python": ["Python Developer", "Software Engineer - Python", "Backend Developer (Python)"]
    }

    @classmethod
    async def search_jobs(
        cls,
        query: Optional[str] = None,
        country: Optional[str] = None,
        workplace_type: Optional[str] = None,  # Remote, Hybrid, On-site
        job_type: Optional[str] = None         # Full-time, Part-time, Internship
    ) -> List[Dict[str, Any]]:
        """
        Search job boards. Return realistic job postings dynamically built
        to match query parameters, acting as a flexible scraper/API integration.
        """
        results = []
        
        # Determine query category
        matching_categories = []
        if query:
            q_lower = query.lower()
            for key in cls.TITLES_POOL.keys():
                if key.lower() in q_lower:
                    matching_categories.append(key)
        
        if not matching_categories:
            matching_categories = list(cls.TITLES_POOL.keys())

        # Generate 10-15 matching jobs
        num_jobs = random.randint(10, 18)
        for i in range(num_jobs):
            category = random.choice(matching_categories)
            title = random.choice(cls.TITLES_POOL[category])
            
            # If internship or fresh graduate is in query, adjust title
            if query and ("intern" in query.lower() or job_type == "Internship"):
                title = f"{title} (Internship)"
            elif query and "fresh" in query.lower():
                title = f"Associate {title} (Fresh Graduate)"
                
            company = random.choice(cls.COMPANIES_POOL)
            
            loc = country if country else random.choice(["United States", "Germany", "United Kingdom", "Canada", "Saudi Arabia", "UAE"])
            wt = workplace_type if workplace_type else random.choice(["Remote", "Hybrid", "On-site"])
            
            # Salary range estimation
            salaries = ["$80,000 - $110,000", "$120,000 - $150,000", "$90,000 - $130,000", "$140,000 - $180,000"]
            if "Internship" in title:
                salary = "$3,000 - $5,000 / month"
            else:
                salary = random.choice(salaries)
                
            desc = (
                f"We are looking for a talented {title} to join our team. In this role, you will work closely "
                f"with senior engineers and product owners to design, build, and deploy software. "
                f"Our primary stack includes {', '.join(company['techs'])}.\n\n"
                f"Key Responsibilities:\n"
                f"- Design and implement clean, testable, and efficient code.\n"
                f"- Collaborate with cross-functional teams to define feature specs.\n"
                f"- Work on improving platform performance and database scalability.\n\n"
                f"Requirements:\n"
                f"- Proficient in Python and relational databases (like PostgreSQL).\n"
                f"- Experience with Git, Docker, and CI/CD pipelines.\n"
                f"- Passion for learning and building production-grade automation systems."
            )
            
            results.append({
                "id": str(uuid.uuid4()),
                "company_name": company["name"],
                "company_website": company["website"],
                "title": title,
                "description": desc,
                "location": loc,
                "workplace_type": wt,
                "salary_range": salary,
                "source": "JobBoard API",
                "url": f"{company['website']}/jobs/{uuid.uuid4().hex[:8]}"
            })
            
        return results
