# ai-labor-law-assistant
This MVP is designed to help users get quick, AI-generated responses to labor law inquiries based on a controlled database of past cases and legal documents. It integrates NLP, BM25 search, GPT-powered responses, and automation via n8n to optimize decision-making and streamline legal guidance.


\ Key Features:
🏛 Labor Law Expertise: Answers common legal questions about contracts, dismissals, benefits, social security, and more.
🔎 BM25-based Search: Retrieves relevant legal precedents from a curated database.
🤖 AI-Powered Responses: Uses GPTs and n8n automation to classify inquiries and determine if professional review is required.
🔗 WhatsApp & Web Chatbot: Users can access legal assistance via a Web App chatbot or WhatsApp (Twilio integration).
📊 Semi-Automated System: If no exact match is found, a basic response is generated, and users are guided towards professional consultation if needed.
🛠 Tech Stack:
Backend: FastAPI (Python)
Database: PostgreSQL (controlled dataset of legal cases)
Search Engine: BM25 + GPT Semantic Matching
Automation: n8n (workflow orchestration & decision-making)
Frontend: Next.js (Landing Page + Chatbot)
Messaging: Twilio API for WhatsApp integration
Deployment: Vercel (Frontend), Render (Backend)
📌 Next Steps:
🚀 Set up the database and retrieval system.
🤖 Train GPTs for improved question classification.
📡 Deploy n8n workflows for automation.
🌐 Optimize chatbot UX for WhatsApp and Web users.
📌 Interested? Feel free to contribute or provide feedback!
