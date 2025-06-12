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
  </head>
  <body
    style="
      margin: 0;
      padding: 0;
      background-color: #f8f9fa;
      font-family: Helvetica, Arial, sans-serif;
    "
  >
    <!-- Wrapper table -->
    <table
      width="100%"
      cellpadding="0"
      cellspacing="0"
      border="0"
      style="padding: 40px 20px"
    >
      <tr>
        <td align="center">
          <!-- Email container -->
          <table
            width="600"
            cellpadding="0"
            cellspacing="0"
            border="0"
            style="
              width: 100%;
              max-width: 600px;
              background-color: #ffffff;
              border-radius: 8px;
              box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
              overflow: hidden;
            "
          >
            <!-- Header -->
            <tr>
              <td style="background-color: #4b99ff; padding: 20px 35px">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td align="left" style="color: #ffffff">
                      <h1
                        style="
                          margin: 0;
                          font-size: 2.4em;
                          font-weight: 300;
                          letter-spacing: -0.5px;
                          line-height: 1.2;
                        "
                      >
                        MediaMind
                      </h1>
                      <p
                        style="
                          margin: 12px 0 0;
                          font-size: 0.9em;
                          text-transform: uppercase;
                          letter-spacing: 0.5px;
                          color: rgba(255, 255, 255, 0.85);
                        "
                      >
                        June 13, 2025
                      </p>
                    </td>
                    <td align="right" style="vertical-align: top">
                      <img
                        src="https://mediamind.csee.tech/EUTOP_Logo.png"
                        alt="Logo"
                        width="200"
                        style="display: block"
                      />
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Divider line (simulating ::after) -->
            <tr>
              <td
                style="
                  height: 4px;
                  background: linear-gradient(90deg, #1e5091 0%, #ffd700 100%);
                "
              ></td>
            </tr>

            <!-- Content -->
            <tr>
              <td style="padding: 50px 40px; color: #2c3e50">
                <!-- Profile section -->
                <div
                  style="
                    margin-bottom: 40px;
                    padding-bottom: 25px;
                    border-bottom: 1px solid #e9ecef;
                  "
                >
                  <p
                    style="
                      color: #6c757d;
                      font-size: 0.85em;
                      text-transform: uppercase;
                      letter-spacing: 1px;
                      margin-bottom: 8px;
                      font-weight: 500;
                    "
                  >
                    Search Profile
                  </p>
                  <p
                    style="
                      color: #1e5091;
                      font-size: 1.3em;
                      font-weight: 600;
                      margin: 0;
                    "
                  >
                    BMW EX
                  </p>
                </div>

                <!-- Message -->
                <div
                  style="
                    font-size: 1.05em;
                    line-height: 1.65;
                    color: #495057;
                    font-weight: 400;
                  "
                >
                  Good morning,<br /><br />
                  This is your
                  <span style="color: #1e5091; font-weight: 600"
                    >daily news report</span
                  >, carefully curated to match your specific interests and
                  search criteria. Our monitoring system has identified the most
                  relevant developments in your field, ensuring you stay
                  informed with
                  <span style="color: #1e5091; font-weight: 600"
                    >actionable insights</span
                  >
                  that matter to your business.<br /><br />
                  Each story has been selected based on its relevance to your
                  profile, providing you with a comprehensive overview of
                  today's key developments.
                </div>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td
                style="
                  background-color: #f8f9fa;
                  padding: 30px 40px;
                  text-align: center;
                  border-top: 1px solid #e9ecef;
                "
              >
                <div
                  style="
                    width: 60px;
                    height: 2px;
                    background-color: #ffd700;
                    margin: 0 auto 20px;
                  "
                ></div>
                <p
                  style="
                    color: #6c757d;
                    font-size: 0.9em;
                    font-weight: 400;
                    margin: 0;
                  "
                >
                  Delivered by MediaMind
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
