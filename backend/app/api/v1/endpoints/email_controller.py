"""
NOTE:
This is just a testing controller for sending emails and creating PDFs.
Once we have a proper scheduler, we can remove this controller.
"""

import base64

from fastapi import APIRouter

from app.services.email_service import EmailSchedule, EmailService
from app.services.pdf_service import PDFService

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
)


@router.get("/{recipient_email}")
async def trigger_email_sending(recipient_email: str):
    pdf_bytes = await PDFService.create_sample_pdf()

    email_schedule = EmailSchedule(
        recipient=recipient_email,
        subject="[MEDIAMIND] Your daily report",
        content_type="text/HTML",
        content=email_content, 
        attachment=base64.b64encode(pdf_bytes).decode("utf-8"),
    )

    await EmailService.schedule_email(email_schedule)
    await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}


@router.get("/pdf")
async def trigger_pdf_creation():
    pdf_bytes = await PDFService.create_sample_pdf()

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)

email_content = """
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Daily News Report</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: "Helvetica Neue", Arial, sans-serif;
        background-color: #f8f9fa;
        padding: 40px 20px;
        color: #2c3e50;
      }

      .email-container {
        background: #ffffff;
        max-width: 600px;
        width: 100%;
        margin: 0 auto;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        overflow: hidden;
      }

      .header {
        background: #1e5091;

        justify-content: space-between;
        align-items: center;
        padding: 20px 35px;
        display: flex;
      }

      .left-content {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
      }

      .organization-name {
        font-family: "Arial", sans-serif;
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin: 0;
      }

      .date {
        font-family: "Arial", sans-serif;
        font-size: 1rem;
        color: #666;
      }

      .logo {
        flex-shrink: 0;
      }

      .header::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1e5091 0%, #ffd700 100%);
      }

      .organization-name {
        color: #ffffff;
        font-size: 2.4em;
        font-weight: 300;
        letter-spacing: -0.5px;
        margin-bottom: 12px;
        line-height: 1.2;
      }

      .date {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1em;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9em;
      }

      .content {
        padding: 50px 40px;
      }

      .profile-section {
        margin-bottom: 40px;
        padding-bottom: 25px;
        border-bottom: 1px solid #e9ecef;
      }

      .profile-label {
        color: #6c757d;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-weight: 500;
      }

      .profile-name {
        color: #1e5091;
        font-size: 1.3em;
        font-weight: 600;
        line-height: 1.3;
      }

      .message {
        font-size: 1.05em;
        line-height: 1.65;
        color: #495057;
        font-weight: 400;
      }

      .highlight {
        color: #1e5091;
        font-weight: 600;
      }

      .accent {
        color: #ffd700;
        font-weight: 600;
      }

      .footer {
        background: #f8f9fa;
        padding: 30px 40px;
        text-align: center;
        border-top: 1px solid #e9ecef;
      }

      .footer-text {
        color: #6c757d;
        font-size: 0.9em;
        font-weight: 400;
      }

      .divider {
        width: 60px;
        height: 2px;
        background: #ffd700;
        margin: 0 auto 20px;
      }

      /* Subtle hover effects for interactive elements */
      .profile-name {
        transition: color 0.3s ease;
      }

      @media (max-width: 480px) {
        body {
          padding: 20px 10px;
        }

        .email-container {
          border-radius: 4px;
        }

        .header {
          padding: 35px 25px 25px;
        }

        .organization-name {
          font-size: 2em;
        }

        .content {
          padding: 35px 25px;
        }

        .footer {
          padding: 25px;
        }
      }
    </style>
  </head>
  <body>
    <div class="email-container">
      <div class="header">
        <div class="left-content">
          <h1 class="organization-name">MediaMind</h1>
          <div class="date">June 12, 2025</div>
        </div>
        <img
          width="200"
          class="logo"
          src="https://mediamind.csee.tech/EUTOP_Logo.png"
        />
      </div>

      <div class="content">
        <div class="profile-section">
          <div class="profile-label">Search Profile</div>
          <div class="profile-name">Technology & Innovation Trends</div>
        </div>

        <div class="message">
          Good morning,
          <br /><br />
          This is your <span class="highlight">daily news report</span>,
          carefully curated to match your specific interests and search
          criteria. Our monitoring system has identified the most relevant
          developments in your field, ensuring you stay informed with
          <span class="accent">actionable insights</span> that matter to your
          business. <br /><br />
          Each story has been selected based on its relevance to your profile,
          providing you with a comprehensive overview of today's key
          developments.
        </div>
      </div>

      <div class="footer">
        <div class="divider"></div>
        <div class="footer-text">Delivered by MediaMind</div>
      </div>
    </div>
  </body>
</html>
"""
