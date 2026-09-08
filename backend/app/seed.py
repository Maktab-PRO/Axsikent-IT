from app.db import SessionLocal
from app.models.category import Category
from app.models.course import Course


def seed_data():
    db = SessionLocal()

    try:
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
        db.commit()

    finally:
        db.close()
