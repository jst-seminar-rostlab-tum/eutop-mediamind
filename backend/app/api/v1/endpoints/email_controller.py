"""
This is a trigger for the email sending process.
This is a placeholder for the actual implementation.
"""
from fastapi import APIRouter

import base64
from app.services.email_service import EmailService, EmailSchedule
from app.services.pdf_service import PDFService

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
)

@router.get("/{recipient_email}")
async def trigger_email_sending(recipient_email: str):
    pdf_bytes = PDFService.create_pdf(dummies)

    email_schedule = EmailSchedule(
        recipient=recipient_email,
        subject="[MEDIAMIND] Your PDF Report",
        content_type="text/plain",
        content="Please find your PDF report attached.",
        attachment=base64.b64encode(pdf_bytes).decode('utf-8')
    )

    await EmailService.schedule_email(email_schedule)
    await EmailService.send_scheduled_emails()
    return {"message": "Email scheduled and sent successfully."}

# Dummy JSON data for testing
jsonstring = """
[
  {
    "title": "AI Revolution",
    "summary": "The rapid adoption of artificial intelligence is transforming industries worldwide, reshaping how we live and work.",
    "content": "Artificial Intelligence (AI) is at the forefront of innovation, enabling companies to automate processes, improve decision-making, and deliver more personalized customer experiences. From healthcare to finance, AI applications are endless and promise significant gains in efficiency and productivity. However, ethical concerns and data privacy remain critical challenges that must be addressed by policymakers and industry leaders alike.",
    "newspaper": "TechDaily",
    "keywords": ["AI", "automation", "innovation", "ethics", "data privacy"],
    "image_url": "https://picsum.photos/seed/ai-revolution/400/200",
    "date_time": "2024-06-01T08:30:00Z"
  },
  {
    "title": "Climate Change Effects",
    "summary": "Rising concerns around global warming and the urgent need for sustainable practices in all sectors.",
    "content": "Climate change is increasingly impacting communities across the globe, leading to more extreme weather events, rising sea levels, and biodiversity loss. In response, governments and organizations are investing in green technologies, renewable energy, and carbon reduction initiatives. Public awareness and consumer demand for environmentally friendly practices are also driving businesses to adopt more sustainable strategies to reduce their environmental footprint.",
    "newspaper": "EcoWorld",
    "keywords": ["climate change", "sustainability", "renewable energy", "biodiversity", "carbon reduction"],
    "image_url": "https://picsum.photos/seed/climate-change/400/200",
    "date_time": "2024-06-02T14:15:00Z"
  },
  {
    "title": "Tech Trends 2025",
    "summary": "Exploring emerging technologies and innovations that are set to shape our future in the coming years.",
    "content": "As we look ahead to 2025, technologies such as artificial intelligence, the Internet of Things (IoT), and 5G networks are expected to fuel the next wave of digital transformation. Startups and established companies are leveraging these trends to develop innovative solutions that address societal needs and create new market opportunities. From smart homes to connected vehicles, the future is becoming increasingly digital and interconnected.",
    "newspaper": "InnovationWeekly",
    "keywords": ["IoT", "5G", "smart homes", "connected vehicles", "digital transformation"],
    "image_url": "https://picsum.photos/seed/tech-trends/400/200",
    "date_time": "2024-06-03T10:00:00Z"
  },
  {
    "title": "Economic Outlook",
    "summary": "An in-depth look at economic recovery, growth prospects, and persistent challenges faced by global markets.",
    "content": "While the global economy shows signs of recovery from the disruptions of recent years, challenges such as inflation, supply chain bottlenecks, and geopolitical uncertainties continue to weigh on growth prospects. Financial experts advise businesses and policymakers to adopt flexible strategies, embrace innovation, and invest in workforce development to navigate these complex economic dynamics. Collaboration across industries and borders will be crucial for building resilient and inclusive economies.",
    "newspaper": "GlobalFinance",
    "keywords": ["economic recovery", "inflation", "supply chain", "innovation", "global trade"],
    "image_url": "https://www.sueddeutsche.de/2024/08/28/19f92c70-5006-447f-97cd-2f5739d5e682.jpeg?rect=0,0,4000,2249&width=556&fm=avif&q=60",
    "date_time": "2024-06-04T16:45:00Z"
  },
  {
    "title": "Space Exploration Milestones",
    "summary": "Celebrating recent achievements in space technology and future missions planned by international agencies.",
    "content": "The past year has seen remarkable progress in space exploration, with successful Mars rover missions, lunar landings, and advancements in satellite technology. Agencies like NASA, ESA, and private companies are collaborating to push the boundaries of human knowledge and prepare for manned missions to Mars. These endeavors not only expand our understanding of the cosmos but also drive innovation in materials science, robotics, and communications.",
    "newspaper": "CosmosToday",
    "keywords": ["space exploration", "Mars rover", "lunar landing", "satellite technology", "NASA"],
    "image_url": "https://picsum.photos/seed/space-exploration/400/200",
    "date_time": "2024-06-05T09:20:00Z"
  },
  {
    "title": "Healthcare Innovations",
    "summary": "New medical technologies and treatments are revolutionizing patient care and disease management.",
    "content": "Recent breakthroughs in biotechnology and medical devices have paved the way for personalized medicine, improved diagnostics, and minimally invasive procedures. Innovations such as CRISPR gene editing, AI-driven imaging, and wearable health monitors are enhancing the effectiveness of treatments and patient outcomes. The healthcare industry continues to evolve rapidly, driven by research, technology, and the growing demand for accessible and affordable care.",
    "newspaper": "MedTechNews",
    "keywords": ["healthcare", "biotechnology", "CRISPR", "AI diagnostics", "wearable technology"],
    "image_url": "https://picsum.photos/seed/healthcare-innovations/400/200",
    "date_time": "2024-06-06T11:10:00Z"
  },
  {
    "title": "Global Education Trends",
    "summary": "Analyzing shifts in education systems worldwide and the role of technology in learning.",
    "content": "Education is undergoing significant transformation as digital platforms, remote learning, and AI tutors become integral parts of the system. Countries are adopting hybrid models to increase accessibility and personalize learning experiences. Challenges remain in bridging the digital divide and ensuring quality education for all, but the potential for innovation to democratize knowledge is greater than ever.",
    "newspaper": "EduWorld",
    "keywords": ["education", "remote learning", "digital platforms", "AI tutors", "hybrid models"],
    "image_url": "https://picsum.photos/seed/education-trends/400/200",
    "date_time": "2024-06-07T13:50:00Z"
  },
  {
    "title": "Renewable Energy Breakthroughs",
    "summary": "Recent advancements in renewable energy technologies promise a cleaner and more sustainable future.",
    "content": "Innovations in solar panels, wind turbines, and energy storage systems have significantly increased efficiency and reduced costs. Governments and private sectors are investing heavily in green infrastructure to meet climate goals and reduce dependence on fossil fuels. These breakthroughs are crucial for combating climate change and fostering economic growth in emerging green industries.",
    "newspaper": "GreenEnergyToday",
    "keywords": ["renewable energy", "solar power", "wind energy", "energy storage", "sustainability"],
    "image_url": "https://picsum.photos/seed/renewable-energy/400/200",
    "date_time": "2024-06-08T15:30:00Z"
  }
]
"""
import json

dummies = json.loads(jsonstring)

