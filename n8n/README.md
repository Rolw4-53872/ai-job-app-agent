# n8n Automation Workflows

This folder contains the visual automation pipelines for the **AI Job Application Agent**. These workflows run inside n8n to coordinate the end-to-end process: researching, draft generation, approval holding, email dispatch, reply monitoring, and WhatsApp notifications.

## Workflow 1: Outbound Pipeline (`workflow_outbound.json`)

Manages the flow when a new company/job is imported:
1. **Webhook Trigger**: Receives a POST containing `application_id`, `company_name`, and `website`.
2. **HTTP Request - Research Company**: Hits `/api/companies/research` to build company context.
3. **HTTP Request - Generate Email**: Hits `/api/emails/generate` to create a tailored email draft.
4. **Wait Node (Webhook)**: Pauses execution until the user manually triggers approvals in the dashboard.
5. **HTTP Request - Send Email**: Dispatches the email via Gmail API once approved.

## Workflow 2: Inbound Pipeline (`workflow_inbound.json`)

Monages reply monitoring:
1. **Gmail Trigger (Inbox Poller)**: Listens for incoming unread emails.
2. **HTTP Request - Analyze Reply**: Sends reply text to `/api/replies/webhook` for classification (e.g. Interview invitation, Assessment).
3. **IF Switch Node**: Checks if classification is critical (e.g., Interview/Assessment/Offer) or has High priority.
4. **WhatsApp Cloud Node**: Dispatches SMS notification template to the user's phone if important.

---

### How to Import Workflows into n8n

1. Open your n8n dashboard (typically `http://localhost:5678`).
2. Click **Add Workflow** on the top right.
3. Select **Import from File** from the workflow menu (three dots in top right).
4. Upload `workflow_outbound.json` or `workflow_inbound.json`.
5. Update your credentials for **Gmail** and **WhatsApp Cloud API** nodes, and set the webhook URLs to point to your FastAPI backend server.
