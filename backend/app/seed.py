from datetime import datetime, timedelta
from random import Random

from sqlalchemy.orm import Session

from app.models import Activity, Company, Contact, Deal, Lead, Message, Task

OWNERS = ["Alex Rivera", "Jordan Lee", "Sam Okonkwo", "Mia Chen", "Chris Navarro"]
STAGES = [
    ("qualification", 20),
    ("discovery", 35),
    ("proposal", 55),
    ("negotiation", 75),
    ("closed_won", 100),
    ("closed_lost", 0),
]


def seed_if_empty(db: Session) -> None:
    if db.query(Company).count() > 0:
        return

    rng = Random(42)
    now = datetime.utcnow()

    company_specs = [
        ("Harborline Logistics", "Logistics", "201-500", "Cebu", 18_400_000, 82),
        ("NovaGrid Energy", "Energy", "51-200", "Makati", 9_200_000, 74),
        ("Brightpath Clinics", "Healthcare", "501-1000", "Quezon City", 32_000_000, 88),
        ("Lattice Retail Co", "Retail", "201-500", "Pasig", 14_500_000, 61),
        ("Orbit Fintech", "Finance", "51-200", "Taguig", 22_100_000, 91),
        ("Coral Softworks", "Software", "11-50", "Davao", 3_800_000, 69),
        ("Summit Hotels PH", "Hospitality", "1001+", "Cebu", 48_000_000, 55),
        ("Aether Mobility", "Transport", "51-200", "Manila", 7_600_000, 77),
        ("Pinecrest Foods", "Food & Bev", "201-500", "Iloilo", 11_200_000, 64),
        ("Keystone Legal", "Professional", "11-50", "Makati", 4_100_000, 85),
        ("Bluefinch Media", "Media", "51-200", "Pasig", 6_400_000, 58),
        ("Nimbus Cloud PH", "Cloud", "51-200", "Taguig", 15_900_000, 93),
    ]

    companies: list[Company] = []
    for name, industry, size, city, revenue, health in company_specs:
        c = Company(
            name=name,
            industry=industry,
            size=size,
            website=f"https://{name.lower().replace(' ', '')}.example",
            city=city,
            country="Philippines",
            annual_revenue=revenue,
            health_score=health,
            created_at=now - timedelta(days=rng.randint(30, 400)),
        )
        db.add(c)
        companies.append(c)
    db.flush()

    people = [
        ("Elena", "Santos", "VP Sales", "active"),
        ("Marco", "Dela Cruz", "CTO", "active"),
        ("Priya", "Nair", "Procurement Lead", "active"),
        ("Jonah", "Reyes", "COO", "active"),
        ("Hana", "Lim", "Head of Growth", "active"),
        ("Luis", "Garcia", "IT Director", "nurture"),
        ("Amara", "Villanueva", "CFO", "active"),
        ("Noah", "Tan", "Founder", "active"),
        ("Sofia", "Cruz", "Ops Manager", "inactive"),
        ("Kenji", "Mori", "Partnerships", "active"),
        ("Isla", "Fernandez", "Marketing Director", "active"),
        ("Diego", "Ramos", "Product Lead", "active"),
        ("Yuki", "Park", "RevOps", "active"),
        ("Camille", "Ocampo", "Buyer", "nurture"),
        ("Theo", "Bautista", "GM", "active"),
        ("Lara", "Mendoza", "Account Manager", "active"),
        ("Owen", "Chua", "Security Lead", "active"),
        ("Nina", "Aguilar", "Clinic Admin", "active"),
        ("Rafa", "Sison", "Fleet Manager", "active"),
        ("Bea", "Uy", "Brand Manager", "active"),
        ("Vic", "Torres", "Controller", "active"),
        ("Jade", "Espino", "HRBP", "nurture"),
        ("Omar", "Hassan", "Solutions Architect", "active"),
        ("Kim", "Rosales", "Store Ops", "active"),
    ]

    contacts: list[Contact] = []
    for i, (fn, ln, title, status) in enumerate(people):
        company = companies[i % len(companies)]
        contact = Contact(
            first_name=fn,
            last_name=ln,
            email=f"{fn.lower()}.{ln.lower().replace(' ', '')}@{company.name.lower().replace(' ', '')}.example",
            phone=f"+63 917 {rng.randint(100, 999)} {rng.randint(1000, 9999)}",
            title=title,
            status=status,
            owner=OWNERS[i % len(OWNERS)],
            company_id=company.id,
            last_contacted_at=now - timedelta(days=rng.randint(0, 45)),
            created_at=now - timedelta(days=rng.randint(10, 300)),
        )
        db.add(contact)
        contacts.append(contact)
    db.flush()

    lead_specs = [
        ("Ana Villar", "Inbound demo", "Website", "new", 72, 42000),
        ("Rico Santos", "Partner referral", "Referral", "qualified", 84, 88000),
        ("Mei Huang", "Trade show booth", "Event", "contacted", 61, 35000),
        ("Ben Okada", "Content download", "Content", "new", 48, 18000),
        ("Carla Gomez", "Cold outreach reply", "Outbound", "qualified", 79, 65000),
        ("Farah Ali", "Marketplace listing", "Partner", "nurturing", 55, 27000),
        ("Tom Bradley", "Webinar attendee", "Event", "contacted", 66, 41000),
        ("Lia Ortega", "Pricing page visit", "Website", "new", 58, 22000),
        ("Hiro Sato", "Customer expansion", "Upsell", "qualified", 91, 120000),
        ("Eden Cruz", "Support ticket upsell", "Support", "nurturing", 44, 15000),
        ("Paolo Ruiz", "LinkedIn inbound", "Social", "new", 63, 39000),
        ("Grace Lim", "RFI response", "RFI", "qualified", 87, 150000),
    ]
    for i, (name, notes, source, status, score, value) in enumerate(lead_specs):
        db.add(
            Lead(
                name=name,
                email=f"{name.lower().replace(' ', '.')}@prospect.example",
                company_name=f"{name.split()[0]} Holdings",
                source=source,
                status=status,
                score=score,
                owner=OWNERS[i % len(OWNERS)],
                estimated_value=value,
                notes=notes,
                created_at=now - timedelta(days=rng.randint(1, 60)),
            )
        )

    deal_titles = [
        "Fleet telematics rollout",
        "Clinic EMR migration",
        "Retail POS upgrade",
        "Cloud cost optimization",
        "Hotel PMS integration",
        "Treasury automation suite",
        "Supply chain visibility",
        "Customer success platform",
        "Security posture review",
        "Marketing attribution stack",
        "Workforce scheduling",
        "API partner program",
        "Warehouse WMS pilot",
        "Finance close accelerator",
        "Omnichannel loyalty",
        "Data lakehouse kickoff",
        "Support desk consolidation",
        "Mobile field service",
    ]
    deals: list[Deal] = []
    for i, title in enumerate(deal_titles):
        stage, prob = STAGES[i % len(STAGES)]
        if i < 4:
            stage, prob = "negotiation", 75
        company = companies[i % len(companies)]
        contact = contacts[i % len(contacts)]
        amount = float(rng.choice([18000, 32000, 45000, 62000, 88000, 120000, 175000, 240000]))
        deal = Deal(
            title=title,
            stage=stage,
            amount=amount,
            probability=prob,
            close_date=now + timedelta(days=rng.randint(-20, 90)),
            owner=OWNERS[i % len(OWNERS)],
            company_id=company.id,
            contact_id=contact.id,
            created_at=now - timedelta(days=rng.randint(5, 120)),
            updated_at=now - timedelta(days=rng.randint(0, 14)),
        )
        db.add(deal)
        deals.append(deal)
    db.flush()

    task_titles = [
        ("Send revised proposal", "high", "todo"),
        ("Schedule discovery call", "medium", "todo"),
        ("Collect security questionnaire", "high", "in_progress"),
        ("Update forecast notes", "low", "todo"),
        ("Intro to procurement", "medium", "done"),
        ("Prepare ROI model", "high", "in_progress"),
        ("Confirm pilot scope", "medium", "todo"),
        ("Follow up on contract redlines", "high", "todo"),
        ("Share case study pack", "low", "done"),
        ("Book executive briefing", "medium", "todo"),
        ("Validate integration checklist", "high", "in_progress"),
        ("Renewal health check", "medium", "todo"),
    ]
    for i, (title, priority, status) in enumerate(task_titles):
        db.add(
            Task(
                title=title,
                description="Generated from pipeline hygiene sweep.",
                status=status,
                priority=priority,
                due_date=now + timedelta(days=rng.randint(-3, 21)),
                owner=OWNERS[i % len(OWNERS)],
                related_type="deal",
                related_id=deals[i % len(deals)].id,
                created_at=now - timedelta(days=rng.randint(0, 20)),
            )
        )

    activity_specs = [
        ("call", "Discovery call completed", "Covered timeline, budget owner, and success metrics."),
        ("email", "Sent proposal v2", "Attached pricing tiers and implementation plan."),
        ("meeting", "Stakeholder workshop", "Aligned on data migration windows."),
        ("note", "Champion identified", "Elena can unblock legal review."),
        ("call", "Objection handling", "Security questionnaire is the remaining gate."),
        ("email", "Case study follow-up", "Shared Harborline logistics win story."),
        ("meeting", "QBR prep", "Reviewed expansion opportunities."),
        ("note", "Risk flag", "Budget freeze rumor for Q4 - keep close."),
        ("call", "Demo feedback", "Liked forecasting views; asked for mobile."),
        ("email", "Contract draft", "Legal reviewing MSA terms."),
        ("meeting", "Pilot kickoff", "Success criteria locked for 30-day pilot."),
        ("note", "Competitor mention", "Evaluating against incumbent spreadsheet process."),
    ]
    for i, (kind, subject, body) in enumerate(activity_specs):
        db.add(
            Activity(
                kind=kind,
                subject=subject,
                body=body,
                contact_id=contacts[i % len(contacts)].id,
                deal_id=deals[i % len(deals)].id,
                owner=OWNERS[i % len(OWNERS)],
                occurred_at=now - timedelta(hours=rng.randint(2, 400)),
            )
        )

    messages = [
        ("Elena Santos", "Re: Fleet telematics rollout", "Can we move the pilot start to next Monday?", 1),
        ("Marco Dela Cruz", "Security questionnaire", "Attached answers for sections A through C.", 1),
        ("Priya Nair", "Pricing clarification", "Need volume discount language for 200 seats.", 0),
        ("Amara Villanueva", "Budget confirmation", "CFO signed off contingent on Q4 start.", 1),
        ("Noah Tan", "Integration timeline", "Our API freeze window is the first week of October.", 0),
        ("Hana Lim", "Marketing attribution stack", "Please send the ROI workbook again.", 1),
        ("Omar Hassan", "Architecture review", "Happy with the proposed event pipeline.", 0),
        ("Grace Lim", "RFI follow-up", "Committee meets Thursday - need one-pager.", 1),
    ]
    for i, (from_name, subject, preview, unread) in enumerate(messages):
        db.add(
            Message(
                thread=f"thread-{i+1}",
                direction="inbound",
                from_name=from_name,
                subject=subject,
                preview=preview,
                unread=unread,
                created_at=now - timedelta(hours=rng.randint(1, 72)),
            )
        )

    db.commit()
