from app.db import SessionLocal
from app.models.category import Category
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.admin import Admin
from passlib.context import CryptContext


def seed_data():
    db = SessionLocal()

    try:
            pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto"
    )

    admin = db.query(Admin).filter(
        Admin.phone == "998901234569"
    ).first()

    if not admin:
        admin = Admin(
            full_name="Axsikent Admin",
            phone="998901234569",
            password_hash=pwd_context.hash("Admin12345"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        if db.query(Category).count() > 0:
            return

        it = Category(
            name="IT",
            icon="💻",
            sort_order=1
        )

        mental = Category(
            name="Mental arifmetika",
            icon="🧮",
            sort_order=2
        )

        english = Category(
            name="Ingliz tili",
            icon="🇬🇧",
            sort_order=3
        )

        db.add_all([
            it,
            mental,
            english
        ])

        db.flush()

        courses = [
            Course(
                category_id=it.id,
                name="Kompyuter savodxonligi",
                age_min=11,
                age_max=18,
                lesson_minutes=90,
                lessons_per_week=2,
                price_min=200000,
                price_max=250000,
                sort_order=1
            ),
            Course(
                category_id=it.id,
                name="Scratch",
                age_min=6,
                age_max=10,
                sort_order=2
            ),
            Course(
                category_id=it.id,
                name="Python",
                age_min=11,
                age_max=18,
                lesson_minutes=90,
                lessons_per_week=2,
                price_min=250000,
                price_max=350000,
                sort_order=3
            ),
            Course(
                category_id=it.id,
                name="Web — HTML/CSS/JS",
                age_min=11,
                age_max=18,
                sort_order=4
            ),
            Course(
                category_id=it.id,
                name="Grafik dizayn",
                age_min=11,
                age_max=18,
                sort_order=5
            ),
            Course(
                category_id=it.id,
                name="Sun’iy intellekt",
                age_min=11,
                age_max=18,
                sort_order=6
            ),
            Course(
                category_id=it.id,
                name="Kattalar IT — Robototexnika + Arduino",
                age_min=11,
                age_max=18,
                lesson_minutes=90,
                lessons_per_week=2,
                price_min=350000,
                price_max=450000,
                sort_order=7
            ),
            Course(
                category_id=it.id,
                name="Bolalar IT — Robototexnika + Arduino",
                age_min=6,
                age_max=10,
                lesson_minutes=90,
                lessons_per_week=2,
                price_min=300000,
                price_max=400000,
                sort_order=8
            ),
            Course(
                category_id=it.id,
                name="3D Print",
                age_min=11,
                lesson_minutes=120,
                lessons_per_week=3,
                sort_order=9
            ),
            Course(
                category_id=mental.id,
                name="Mental arifmetika",
                age_min=6,
                age_max=12,
                lesson_minutes=60,
                lessons_per_week=2,
                price_min=200000,
                price_max=250000,
                sort_order=1
            ),
            Course(
                category_id=english.id,
                name="Ingliz tili — 6–10 yosh",
                age_min=6,
                age_max=10,
                lesson_minutes=60,
                lessons_per_week=3,
                price_min=150000,
                price_max=200000,
                sort_order=1
            ),
            Course(
                category_id=english.id,
                name="Ingliz tili — 11–18 yosh",
                age_min=11,
                age_max=18,
                lesson_minutes=90,
                lessons_per_week=2,
                price_min=180000,
                price_max=250000,
                sort_order=2
            ),
            Course(
                category_id=english.id,
                name="IELTS",
                age_min=16,
                lesson_minutes=120,
                lessons_per_week=3,
                price_min=300000,
                price_max=400000,
                sort_order=3
            )
        ]

        db.add_all(courses)
        db.flush()

        modules = [
            # Scratch
            CourseModule(
                course_id=courses[1].id,
                title="O'yin yasash",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[1].id,
                title="Multiplikatsiya",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[1].id,
                title="Drag & Drop kodlari",
                sort_order=3
            ),

            # Python
            CourseModule(
                course_id=courses[2].id,
                title="O'zgaruvchilar va ma'lumot turlari",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[2].id,
                title="Tsikllar",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[2].id,
                title="Toshbaqa grafikasi",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[2].id,
                title="Mini o'yinlar",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[2].id,
                title="Oddiy AI loyihalari",
                sort_order=5
            ),

            # Web
            CourseModule(
                course_id=courses[3].id,
                title="HTML asoslari",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[3].id,
                title="CSS va web dizayn",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[3].id,
                title="Landing page yaratish",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[3].id,
                title="JavaScript asoslari",
                sort_order=4
            ),

            # Grafik dizayn
            CourseModule(
                course_id=courses[4].id,
                title="Grafik dizayn asoslari",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[4].id,
                title="Kompozitsiya va ranglar",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[4].id,
                title="Amaliy dizayn loyihalari",
                sort_order=3
            ),

            # Robototexnika 6-10
            CourseModule(
                course_id=courses[7].id,
                title="Lego robotlar",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[7].id,
                title="Sensorlar asoslari",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[7].id,
                title="Mini mashinalar",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[7].id,
                title="Arduino asoslari",
                sort_order=4
            ),

            # Robototexnika 11-18
            CourseModule(
                course_id=courses[6].id,
                title="Arduino platalari",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[6].id,
                title="LED, signal va sensorlar",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[6].id,
                title="Servo motorlar",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[6].id,
                title="Aqlli uy loyihasi",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[6].id,
                title="Aqlli mashina yasash",
                sort_order=5
            ),
            CourseModule(
                course_id=courses[6].id,
                title="Robot musobaqalari",
                sort_order=6
            ),

            # 3D Print
            CourseModule(
                course_id=courses[8].id,
                title="Tinkercad — boshlang'ich 3D modellashtirish",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Fusion 360 — professional modellashtirish",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[8].id,
                title="STL tayyorlash",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Modelni slicing qilish",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Ender 5 Pro qurilishi",
                sort_order=5
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Ekstruder, Hotend va Bed leveling",
                sort_order=6
            ),
            CourseModule(
                course_id=courses[8].id,
                title="PLA va PETG materiallari",
                sort_order=7
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Cura bilan ishlash",
                sort_order=8
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Bosma sifatini yaxshilash",
                sort_order=9
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Printer muammolarini tuzatish",
                sort_order=10
            ),
            CourseModule(
                course_id=courses[8].id,
                title="Real buyumlar chop etish",
                sort_order=11
            ),

            # Mental arifmetika
            CourseModule(
                course_id=courses[9].id,
                title="Abakus bilan amallar",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[9].id,
                title="Miya bilan tez hisoblash",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[9].id,
                title="Diqqat va tez fikrlash",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[9].id,
                title="Har oygi musobaqalar",
                sort_order=4
            ),

            # English 6-10
            CourseModule(
                course_id=courses[10].id,
                title="Alifbo va fonika",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[10].id,
                title="Asosiy lug'at",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[10].id,
                title="Oddiy jumlalar",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[10].id,
                title="Tinglash o'yinlari",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[10].id,
                title="Kartochkalar",
                sort_order=5
            ),
            CourseModule(
                course_id=courses[10].id,
                title="Har oylik progress testi",
                sort_order=6
            ),

            # English 11-18
            CourseModule(
                course_id=courses[11].id,
                title="Beginner → Elementary → Pre-Intermediate → Intermediate",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[11].id,
                title="Grammatika: zamonlar",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[11].id,
                title="Modal fe'llar, passiv va shart gaplar",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[11].id,
                title="Nutq klubi",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[11].id,
                title="Har oylik test",
                sort_order=5
            ),
            CourseModule(
                course_id=courses[11].id,
                title="Har 3 oyda sertifikat",
                sort_order=6
            ),

            # IELTS
            CourseModule(
                course_id=courses[12].id,
                title="Listening — 4 bo'lim",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[12].id,
                title="Reading — 3 qism",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[12].id,
                title="Writing — Task 1 va Task 2",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[12].id,
                title="Speaking — Part 1, 2, 3",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[12].id,
                title="Har haftalik sinov testi",
                sort_order=5
            ),

            # IT savodxonlik
            CourseModule(
                course_id=courses[0].id,
                title="Klaviatura, papkalar va fayllar",
                sort_order=1
            ),
            CourseModule(
                course_id=courses[0].id,
                title="Word — matn tayyorlash",
                sort_order=2
            ),
            CourseModule(
                course_id=courses[0].id,
                title="Excel — formulalar",
                sort_order=3
            ),
            CourseModule(
                course_id=courses[0].id,
                title="PowerPoint",
                sort_order=4
            ),
            CourseModule(
                course_id=courses[0].id,
                title="Internetdan foydalanish",
                sort_order=5
            )
        ]

        db.add_all(modules)
        db.commit()

    finally:
        db.close()
