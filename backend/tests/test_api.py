import pytest
from app.models.models import Company, Application, Email

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "supersecretpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"

def test_login_access_token(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={"username": test_user.email, "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_get_profile(client, auth_headers):
    response = client.get("/api/profile/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Test Applicant"

def test_update_profile(client, auth_headers):
    response = client.put(
        "/api/profile/",
        headers=auth_headers,
        json={"full_name": "Updated Name", "country": "Saudi Arabia", "years_of_experience": 5.0}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["years_of_experience"] == 5.0

def test_research_company(client, auth_headers):
    response = client.post(
        "/api/companies/research",
        headers=auth_headers,
        json={"name": "NeuralStack Solutions", "website": "https://neuralstack.io"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "NeuralStack Solutions"
    assert "industry" in response.json()

def test_create_and_update_application(client, db_session, auth_headers):
    # Add seed company
    company = Company(name="DataFlow Labs", website="https://dataflowlabs.com")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Create application
    response = client.post(
        "/api/applications/",
        headers=auth_headers,
        json={"company_id": str(company.id), "status": "Draft"}
    )
    assert response.status_code == 200
    app_id = response.json()["id"]
    assert response.json()["status"] == "Draft"
    
    # Update status
    response = client.put(
        f"/api/applications/{app_id}",
        headers=auth_headers,
        json={"status": "Interview", "notes": "Got call today"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Interview"
    assert response.json()["notes"] == "Got call today"

def test_email_approval_flow(client, db_session, auth_headers):
    # Setup company and application
    company = Company(name="Apex ML Systems")
    db_session.add(company)
    db_session.commit()
    
    app_inst = Application(user_id=db_session.query(Company).first().id, company_id=company.id, status="Draft")
    # Wait, the user_id in Application must match test_user's ID, which is why we query it or resolve from database
    from app.models.models import User
    test_user_id = db_session.query(User).first().id
    app_inst.user_id = test_user_id
    db_session.add(app_inst)
    db_session.commit()
    db_session.refresh(app_inst)
    
    # 1. Generate Email
    response = client.post(
        "/api/emails/generate",
        headers=auth_headers,
        json={"application_id": str(app_inst.id)}
    )
    assert response.status_code == 200
    email_id = response.json()["id"]
    assert response.json()["status"] == "Draft"
    
    # 2. Try sending before approval (Should fail)
    response = client.post(f"/api/emails/{email_id}/send", headers=auth_headers)
    assert response.status_code == 400
    assert "must Approve it first" in response.json()["detail"]
    
    # 3. Approve email
    response = client.post(f"/api/emails/{email_id}/approve", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Approved"
    
    # 4. Send email (Should succeed in mock mode)
    response = client.post(f"/api/emails/{email_id}/send", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Sent"
    assert response.json()["gmail_message_id"] is not None
