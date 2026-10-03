import uuid
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from apps.products.models import Product, Category, ProductModule, ProductResource, ProductFAQ
from apps.content.models import YouTubeVideo, EducationalResource
from apps.orders.models import Customer, Order, OrderItem, Payment, WebhookEvent
from apps.core.models import WaitlistLead, ContactMessage

class Command(BaseCommand):
    help = "Seeds demo database with realistic products, orders, customers, YouTube videos, and creator credentials."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding VitalPath Education demo data..."))

        # 1. Create or Update Creator Account
        creator_user, created = User.objects.get_or_create(
            username="creator@vitalpath.edu",
            defaults={
                "email": "creator@vitalpath.edu",
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        creator_user.set_password("VitalPath2026!")
        creator_user.is_staff = True
        creator_user.is_superuser = True
        creator_user.save()
        self.stdout.write(self.style.SUCCESS(f"Creator account ready: {creator_user.username} / VitalPath2026!"))

        # 2. Categories
        cat_foundations, _ = Category.objects.get_or_create(
            slug="foundations",
            defaults={"name": "Health Foundations", "description": "Core physiological principles and evidence-based health fundamentals.", "order": 1}
        )
        cat_nutrition, _ = Category.objects.get_or_create(
            slug="nutrition",
            defaults={"name": "Everyday Nutrition", "description": "Practical nutrition literacy without fads, extremes, or dogma.", "order": 2}
        )
        cat_habits, _ = Category.objects.get_or_create(
            slug="habit-systems",
            defaults={"name": "Habit Systems", "description": "Behavioral architecture for long-term health adherence and clarity.", "order": 3}
        )

        # 3. Products
        # Product 1
        p1, _ = Product.objects.get_or_create(
            slug="health-education-fundamentals",
            defaults={
                "title": "Health Education Fundamentals",
                "category": cat_foundations,
                "short_description": "A grounded, evidence-informed foundation covering the core biological and lifestyle concepts that govern daily wellbeing.",
                "description": """Health Education Fundamentals is a structured, jargon-free curriculum designed to replace confusing online health headlines with dependable scientific literacy.

Across 8 focused modules and a companion reference handbook, you will master the foundational pillars of energy metabolism, inflammation, stress response, and lifestyle markers. 

This curriculum does not prescribe extreme regimens; instead, it equips you with the fundamental knowledge necessary to make informed health decisions for life.""",
                "price": Decimal("19.00"),
                "currency": "USD",
                "status": "published",
                "featured": True,
                "format_type": "Digital Guide & 8 Structured Modules",
                "estimated_duration": "Self-paced (approx. 3.5 hours)",
                "level": "All Levels / Essential Foundation",
                "what_is_included": "8 structured educational video modules\n48-page comprehensive digital PDF curriculum\nInteractive knowledge check quizzes\nPrintable physiological summary sheet\nLifetime digital access & future updates",
                "who_it_is_for": "Individuals tired of conflicting health trends and sensationalist headlines\nCurious learners who want an objective, science-first foundation\nAnyone seeking a clear conceptual map of how the human body stays resilient",
                "target_outcomes": "Understand how sleep, movement, and nutrition interact at a cellular level\nDevelop the confidence to evaluate health claims and media articles critically\nFormulate a personalized, low-friction wellness baseline",
                "cover_image_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&auto=format&fit=crop&q=80",
            }
        )
        # Modules for P1
        p1.modules.all().delete()
        ProductModule.objects.create(product=p1, title="Module 1: The Human Operating System", description="An overview of energy homeostasis, circadian rhythms, and basic physiological balance.", duration="22 mins", order=0)
        ProductModule.objects.create(product=p1, title="Module 2: Decoding Health Metrics & Labs", description="How standard blood markers, resting heart rate, and metabolic indicators reflect everyday state.", duration="28 mins", order=1)
        ProductModule.objects.create(product=p1, title="Module 3: Stress Physiology & Nervous System", description="The autonomic nervous system, acute vs chronic stress response, and recovery windows.", duration="25 mins", order=2)
        ProductModule.objects.create(product=p1, title="Module 4: Everyday Movement & Cellular Energy", description="Why daily ambient movement and mitochondrial health underpin long-term vitality.", duration="30 mins", order=3)
        ProductModule.objects.create(product=p1, title="Module 5: Sleep Architecture Demystified", description="REM, deep sleep cycles, and the neurochemical mechanisms of nighttime restoration.", duration="26 mins", order=4)
        ProductModule.objects.create(product=p1, title="Module 6: Nutrition Fundamentals Without Fads", description="Macronutrients, micronutrient density, and gut barrier integrity explained plainly.", duration="34 mins", order=5)
        ProductModule.objects.create(product=p1, title="Module 7: Environmental & Lifestyle Modulators", description="Light exposure, hydration dynamics, and thermal regulation principles.", duration="20 mins", order=6)
        ProductModule.objects.create(product=p1, title="Module 8: Building Your Sustainable Roadmap", description="Synthesizing knowledge into a personal, non-extreme health architecture.", duration="35 mins", order=7)

        # Resources for P1
        p1.resources.all().delete()
        ProductResource.objects.create(product=p1, title="Complete Health Fundamentals Handbook (PDF)", resource_type="pdf", file_size="4.8 MB PDF", order=0)
        ProductResource.objects.create(product=p1, title="Baseline Health Metric Tracking Sheet", resource_type="checklist", file_size="1.2 MB PDF", order=1)
        ProductResource.objects.create(product=p1, title="Health Media Evaluation Checklist", resource_type="template", file_size="850 KB PDF", order=2)

        # FAQs for P1
        p1.faqs.all().delete()
        ProductFAQ.objects.create(product=p1, question="Is this a medical treatment plan or consultation?", answer="No. VitalPath Education provides purely educational resources designed to build scientific literacy. It is not clinical medical advice or treatment.", order=0)
        ProductFAQ.objects.create(product=p1, question="How do I access the digital guide after purchase?", answer="Immediately upon checkout confirmation, you will receive immediate access on screen, and an access link will be delivered directly to your email address.", order=1)
        ProductFAQ.objects.create(product=p1, question="Can I read the materials on mobile devices and e-readers?", answer="Yes, all PDF companion guides and modules are optimized for desktop, tablet, and smartphone viewing.", order=2)

        # Product 2
        p2, _ = Product.objects.get_or_create(
            slug="understanding-everyday-nutrition",
            defaults={
                "title": "Understanding Everyday Nutrition",
                "category": cat_nutrition,
                "short_description": "A calm, comprehensive breakdown of human nutrition, food energy, protein targets, and balanced meal composition.",
                "description": """Understanding Everyday Nutrition strips away diet tribalism to present the factual mechanics of human nourishment.

Learn how carbohydrates, fats, proteins, and dietary fiber function in the human digestive system, how blood sugar regulation actually works, and how to construct balanced, enjoyable meals without restrictive counting.

Includes comprehensive grocery frameworks, nutrient density cheat sheets, and practical timing insights.""",
                "price": Decimal("29.00"),
                "currency": "USD",
                "status": "published",
                "featured": True,
                "format_type": "Digital Masterclass & Toolkit",
                "estimated_duration": "Self-paced (approx. 4.5 hours)",
                "level": "Beginner to Intermediate",
                "what_is_included": "10 in-depth educational nutrition modules\n60-page illustrated nutrition field manual\nWhole-food grocery matrix & pantry blueprint\nVisual meal composition worksheets\nMicronutrient bioavailability guide",
                "who_it_is_for": "Anyone seeking freedom from diet culture and conflicting nutrition fads\nBusy individuals who want simple, reliable principles for daily eating\nHealth enthusiasts looking for clear, non-dogmatic nutritional physiology",
                "target_outcomes": "Confidently assemble nutritionally complete meals in under 15 minutes\nUnderstand hunger cues, satiety mechanisms, and glucose balance\nNavigate restaurant menus and grocery aisles with effortless clarity",
                "cover_image_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&auto=format&fit=crop&q=80",
            }
        )
        p2.modules.all().delete()
        ProductModule.objects.create(product=p2, title="Module 1: Macronutrient Biology & Digestive Transit", description="How your body breaks down proteins, complex carbohydrates, and essential fats.", duration="28 mins", order=0)
        ProductModule.objects.create(product=p2, title="Module 2: Blood Sugar & Energy Stability", description="The physiological role of insulin, glycogen storage, and steady afternoon energy.", duration="32 mins", order=1)
        ProductModule.objects.create(product=p2, title="Module 3: Protein Targets & Muscle Preservation", description="Evidence-based amino acid requirements across different age and activity groups.", duration="27 mins", order=2)
        ProductModule.objects.create(product=p2, title="Module 4: Dietary Fats & Cellular Membranes", description="Understanding Omega-3s, saturated fats, and smoke points for home cooking.", duration="24 mins", order=3)
        ProductModule.objects.create(product=p2, title="Module 5: Fiber & Microbiome Ecosystem", description="Soluble vs insoluble fiber and supporting gut microbial diversity.", duration="30 mins", order=4)

        # Product 3
        p3, _ = Product.objects.get_or_create(
            slug="building-better-health-habits",
            defaults={
                "title": "Building Better Health Habits",
                "category": cat_habits,
                "short_description": "A systematic, psychology-backed blueprint for making healthy routines effortless, consistent, and resilient to life's chaos.",
                "description": """Why do most health resolutions collapse within 3 weeks? Because willpower is a finite resource.

Building Better Health Habits teaches behavioral architecture: environmental design, friction reduction, habit pairing, and identity-based reinforcement.

Transform lofty aspirations into automatic, low-effort daily behaviors that stick even during your busiest weeks.""",
                "price": Decimal("24.00"),
                "currency": "USD",
                "status": "published",
                "featured": True,
                "format_type": "Practical Habit System & Workbook",
                "estimated_duration": "Self-paced (approx. 2.5 hours)",
                "level": "All Levels",
                "what_is_included": "6 step-by-step habit design modules\n30-Day implementation workbook & habit planner\nTrigger-Action-Reward audit worksheets\nLow-willpower emergency reset protocol\nPrintable weekly review templates",
                "who_it_is_for": "People struggling with the 'all-or-nothing' consistency trap\nProfessionals looking to integrate health into demanding work schedules\nAnyone who has abandoned previous wellness routines and wants a fresh start",
                "target_outcomes": "Design an environment where good choices require zero willpower\nRecover from disruptions and missed days without self-criticism or guilt\nEstablish three unbreakable core health anchors in 30 days",
                "cover_image_url": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=800&auto=format&fit=crop&q=80",
            }
        )

        # Product 4 (Unfeatured / additional catalog item)
        p4, _ = Product.objects.get_or_create(
            slug="sleep-circadian-physiology-guide",
            defaults={
                "title": "Sleep & Circadian Physiology Guide",
                "category": cat_foundations,
                "short_description": "Master the science of deep restorative sleep, morning alertness, and natural melatonin optimization.",
                "description": """An evidence-based masterguide into sleep stages, light timing, and bedroom environment optimization.

Learn how morning photon exposure, caffeine half-life, temperature regulation, and evening wind-down rituals govern restorative sleep quality.""",
                "price": Decimal("22.00"),
                "currency": "USD",
                "status": "published",
                "featured": False,
                "format_type": "Specialized Field Guide",
                "estimated_duration": "2 hours self-paced",
                "level": "All Levels",
                "what_is_included": "5 specialized circadian modules\n35-page sleep optimization field guide\nCaffeine cutoff calculator & guide\nBedroom environmental audit checklist",
                "who_it_is_for": "Anyone waking up sluggish, tired, or experiencing afternoon energy crashes",
                "target_outcomes": "Fall asleep faster and achieve deeper, more restorative non-REM and REM cycles",
                "cover_image_url": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800&auto=format&fit=crop&q=80",
            }
        )

        self.stdout.write(self.style.SUCCESS("Products and curriculum seeded successfully."))

        # 4. YouTube Videos
        videos_data = [
            {
                "title": "How to Read Nutrition Labels Without Confusion",
                "video_id": "y9x72V8cM7Q",
                "description": "A 12-minute breakdown on what food ingredient lists and % Daily Values really mean for your health.",
                "duration": "12:45",
                "category": "Nutrition Principles",
                "featured": True,
                "order": 1,
                "published_at": timezone.now().date() - timedelta(days=5),
            },
            {
                "title": "The Truth About Morning Cortisol & Natural Energy Cycles",
                "video_id": "dQw4w9WgXcQ",
                "description": "Why natural sunlight exposure in the first 30 minutes sets your circadian timer for the day.",
                "duration": "16:20",
                "category": "Sleep & Circadian",
                "featured": True,
                "order": 2,
                "published_at": timezone.now().date() - timedelta(days=12),
            },
            {
                "title": "Why Habit Consistency Always Outperforms Extreme Diets",
                "video_id": "3JZ_D3ELwOQ",
                "description": "The behavioral psychology of micro-adjustments and why sustainable changes win over 12 months.",
                "duration": "10:15",
                "category": "Habit Systems",
                "featured": True,
                "order": 3,
                "published_at": timezone.now().date() - timedelta(days=20),
            },
            {
                "title": "Simple Hydration & Electrolyte Dynamics Explained",
                "video_id": "fJ9rUzIMcZQ",
                "description": "Understanding sodium, potassium, magnesium, and cellular water absorption beyond just drinking water.",
                "duration": "14:30",
                "category": "Physiology Basics",
                "featured": True,
                "order": 4,
                "published_at": timezone.now().date() - timedelta(days=28),
            },
            {
                "title": "How Sleep Architecture Affects Daily Physical Recovery",
                "video_id": "kXYiU_JCYtU",
                "description": "The roles of slow-wave sleep in tissue repair and REM sleep in cognitive clarity.",
                "duration": "18:05",
                "category": "Recovery Science",
                "featured": False,
                "order": 5,
                "published_at": timezone.now().date() - timedelta(days=35),
            },
        ]
        for v in videos_data:
            YouTubeVideo.objects.update_or_create(
                title=v["title"],
                defaults=v
            )

        # 5. Free Educational Resources
        resources_data = [
            {
                "title": "The Daily Health Foundations Checklist",
                "summary": "A high-leverage 1-page printable checklist to track light exposure, hydration, movement, and sleep routine daily.",
                "resource_type": "checklist",
                "read_time": "3 min read",
                "format_label": "Printable PDF",
                "is_featured": True,
                "order": 1,
            },
            {
                "title": "Whole-Food Nutrient Density Reference Chart",
                "summary": "Visual comparison of bioavailable vitamins, minerals, and polyphenols across common pantry staples.",
                "resource_type": "reference",
                "read_time": "5 min read",
                "format_label": "High-Res Chart",
                "is_featured": True,
                "order": 2,
            },
            {
                "title": "Evaluating Online Health Claims: A Decision Matrix",
                "summary": "A 5-step critical thinking framework to quickly detect pseudoscience, marketing hype, and biased health studies.",
                "resource_type": "guide",
                "read_time": "7 min read",
                "format_label": "PDF Guide",
                "is_featured": True,
                "order": 3,
            },
        ]
        for r in resources_data:
            EducationalResource.objects.update_or_create(
                title=r["title"],
                defaults=r
            )

        # 6. Realistic Customers and Orders
        customers_seed = [
            {"name": "Maya Lin", "email": "maya.lin@example.com", "notes": "Completed Fundamentals course, requested advanced nutrition materials."},
            {"name": "David Cooper", "email": "david.cooper@example.com", "notes": "Active learner, purchased multiple guides."},
            {"name": "Elena Rostova", "email": "elena.r@example.com", "notes": "Found via YouTube channel. Left glowing feedback on Habit guide."},
            {"name": "Marcus Thorne", "email": "marcus.thorne@example.com", "notes": "Interested in private Telegram community."},
            {"name": "Jessica Hayes", "email": "j.hayes@example.com", "notes": "Purchased nutrition guide."},
            {"name": "Brian Miller", "email": "bmiller@example.com", "notes": "Early student."},
            {"name": "Priya Patel", "email": "priya.p@example.com", "notes": "Enrolled in Fundamentals and Nutrition."},
            {"name": "Alexander Wright", "email": "alex.wright@example.com", "notes": "Subscribed to waitlist and purchased habit guide."},
        ]

        # Seed Orders with varying dates
        now = timezone.now()
        orders_seed = [
            {"customer_idx": 0, "product": p1, "days_ago": 1, "order_num": "VP-78219"},
            {"customer_idx": 1, "product": p2, "days_ago": 2, "order_num": "VP-65431"},
            {"customer_idx": 1, "product": p3, "days_ago": 4, "order_num": "VP-65489"},
            {"customer_idx": 2, "product": p3, "days_ago": 5, "order_num": "VP-43210"},
            {"customer_idx": 3, "product": p1, "days_ago": 8, "order_num": "VP-99812"},
            {"customer_idx": 4, "product": p2, "days_ago": 11, "order_num": "VP-12345"},
            {"customer_idx": 5, "product": p1, "days_ago": 14, "order_num": "VP-87654"},
            {"customer_idx": 6, "product": p1, "days_ago": 16, "order_num": "VP-34567"},
            {"customer_idx": 6, "product": p2, "days_ago": 18, "order_num": "VP-34599"},
            {"customer_idx": 7, "product": p3, "days_ago": 22, "order_num": "VP-56789"},
        ]

        created_customers = []
        for c_data in customers_seed:
            customer, _ = Customer.objects.get_or_create(
                email=c_data["email"],
                defaults={
                    "name": c_data["name"],
                    "notes": c_data["notes"],
                    "stripe_customer_id": f"cus_demo_{uuid.uuid4().hex[:8]}",
                }
            )
            created_customers.append(customer)

        for o_data in orders_seed:
            cust = created_customers[o_data["customer_idx"]]
            prod = o_data["product"]
            order_date = now - timedelta(days=o_data["days_ago"])

            order, o_created = Order.objects.get_or_create(
                order_number=o_data["order_num"],
                defaults={
                    "customer": cust,
                    "customer_name": cust.name,
                    "customer_email": cust.email,
                    "status": "completed",
                    "payment_status": "paid",
                    "total": prod.price,
                    "currency": "USD",
                    "stripe_checkout_session_id": f"cs_test_{uuid.uuid4().hex[:16]}",
                    "stripe_payment_intent_id": f"pi_{uuid.uuid4().hex[:16]}",
                    "email_sent": True,
                    "created_at": order_date,
                }
            )
            if o_created:
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_title=prod.title,
                    price=prod.price,
                    quantity=1
                )
                Payment.objects.create(
                    order=order,
                    provider="stripe",
                    provider_reference=order.stripe_payment_intent_id,
                    status="succeeded",
                    amount=prod.price,
                    currency="USD",
                    created_at=order_date,
                )
                # Set created_at correctly
                Order.objects.filter(id=order.id).update(created_at=order_date)

        # Recalculate stats for all customers
        for cust in Customer.objects.all():
            cust.recalculate_stats()

        # 7. Waitlist Leads (Phases 2/3)
        waitlist_entries = [
            {"email": "carol.white@example.com", "name": "Carol White", "interest_area": "telegram"},
            {"email": "sam.morrison@example.com", "name": "Sam Morrison", "interest_area": "membership"},
            {"email": "lisa.turner@example.com", "name": "Lisa Turner", "interest_area": "all"},
            {"email": "franklin.z@example.com", "name": "Franklin Zhang", "interest_area": "nutrition"},
        ]
        for w in waitlist_entries:
            WaitlistLead.objects.get_or_create(
                email=w["email"],
                defaults=w
            )

        # 8. Sample Contact Messages
        ContactMessage.objects.get_or_create(
            email="marcus.thorne@example.com",
            defaults={
                "name": "Marcus Thorne",
                "subject": "Community launch question",
                "message": "Hi Sarah! Really enjoying your YouTube lectures on circadian biology. When is the Telegram community launching? Would love to join the first cohort.",
                "is_read": False,
                "created_at": now - timedelta(hours=6),
            }
        )

        self.stdout.write(self.style.SUCCESS("All demo data seeded successfully!"))
