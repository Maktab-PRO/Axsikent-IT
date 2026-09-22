from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.core.security import require_admin

from app.models.admin import Admin
from app.models.category import Category
from app.models.course import Course
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.lesson_quiz import LessonQuiz
from app.models.lesson_progress import LessonProgress


router = APIRouter(
    prefix="/admin/courses",
    tags=["Admin Courses"]
)


# =========================================================
# SCHEMAS
# =========================================================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    icon: str | None = Field(default=None, max_length=20)
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    icon: str | None = Field(default=None, max_length=20)
    sort_order: int | None = Field(default=None, ge=0)


class CourseCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=1000)

    age_min: int | None = Field(default=None, ge=0, le=100)
    age_max: int | None = Field(default=None, ge=0, le=100)

    lesson_minutes: int | None = Field(default=None, ge=1, le=300)
    lessons_per_week: int | None = Field(default=None, ge=1, le=14)

    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)

    sort_order: int = Field(default=0, ge=0)


class CourseUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=1000)

    age_min: int | None = Field(default=None, ge=0, le=100)
    age_max: int | None = Field(default=None, ge=0, le=100)

    lesson_minutes: int | None = Field(default=None, ge=1, le=300)
    lessons_per_week: int | None = Field(default=None, ge=1, le=14)

    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)

    sort_order: int | None = Field(default=None, ge=0)


class ModuleCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    sort_order: int = Field(default=0, ge=0)


class ModuleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    sort_order: int | None = Field(default=None, ge=0)


class LessonCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    content: str | None = None
    video_url: str | None = Field(default=None, max_length=500)
    sort_order: int = Field(default=0, ge=0)


class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    content: str | None = None
    video_url: str | None = Field(default=None, max_length=500)
    sort_order: int | None = Field(default=None, ge=0)


# =========================================================
# HELPERS
# =========================================================

def get_category_or_404(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return category


def get_course_or_404(course_id: int, db: Session):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    return course


def get_module_or_404(course_id: int, module_id: int, db: Session):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Modul topilmadi yoki ushbu kursga tegishli emas")
    return module


def get_lesson_or_404(module_id: int, lesson_id: int, db: Session):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.module_id == module_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi yoki ushbu modulga tegishli emas")
    return lesson


# =========================================================
# CATEGORY MANAGEMENT
# =========================================================

@router.get("/categories")
def get_admin_categories(
    active_only: bool = False,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Category)

    if active_only:
        query = query.filter(
            Category.is_active == True
        )

    categories = query.order_by(
        Category.sort_order,
        Category.id
    ).all()

    return {
        "total": len(categories),
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "icon": category.icon,
                "sort_order": category.sort_order,
                "is_active": category.is_active
            }
            for category in categories
        ]
    }


@router.post("/categories")
def create_category(
    data: CategoryCreate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(
        Category.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Bu kategoriya allaqachon mavjud"
        )

    category = Category(
        name=course_name,
        icon=data.icon,
        sort_order=data.sort_order,
        is_active=True
    )

    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Bu kategoriya allaqachon mavjud")
    db.refresh(category)

    return {
        "success": True,
        "message": "Kategoriya yaratildi",
        "category": {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "sort_order": category.sort_order,
            "is_active": category.is_active
        }
    }


@router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = get_category_or_404(
        category_id,
        db
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        duplicate = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != category_id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Bu nomdagi kategoriya allaqachon mavjud"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return {
        "success": True,
        "message": "Kategoriya yangilandi",
        "category": {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "sort_order": category.sort_order,
            "is_active": category.is_active
        }
    }


@router.put("/categories/{category_id}/deactivate")
def deactivate_category(
    category_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = get_category_or_404(
        category_id,
        db
    )

    category.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Kategoriya deaktiv qilindi",
        "category_id": category.id
    }


@router.put("/categories/{category_id}/activate")
def activate_category(
    category_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = get_category_or_404(
        category_id,
        db
    )

    category.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "Kategoriya faollashtirildi",
        "category_id": category.id
    }


# =========================================================
# COURSE LIST
# =========================================================

@router.get("/")
def get_admin_courses(
    search: str | None = None,
    category_id: int | None = None,
    active_only: bool = False,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Course)

    if search:
        query = query.filter(
            Course.name.ilike(f"%{search}%")
        )

    if category_id:
        query = query.filter(
            Course.category_id == category_id
        )

    if active_only:
        query = query.filter(
            Course.is_active == True
        )

    courses = query.order_by(
        Course.sort_order,
        Course.id
    ).all()

    result = []

    for course in courses:
        category = db.query(Category).filter(
            Category.id == course.category_id
        ).first()

        modules_count = db.query(CourseModule).filter(
            CourseModule.course_id == course.id,
            CourseModule.is_active == True
        ).count()

        students_count = db.query(StudentCourse).filter(
            StudentCourse.course_id == course.id,
            StudentCourse.is_active == True
        ).count()

        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,

            "category": {
                "id": category.id if category else None,
                "name": category.name if category else None,
                "icon": category.icon if category else None
            },

            "age_min": course.age_min,
            "age_max": course.age_max,
            "lesson_minutes": course.lesson_minutes,
            "lessons_per_week": course.lessons_per_week,
            "price_min": course.price_min,
            "price_max": course.price_max,

            "sort_order": course.sort_order,
            "is_active": course.is_active,

            "modules_count": modules_count,
            "students_count": students_count
        })

    return {
        "total": len(result),
        "courses": result
    }


@router.post("/assign")
def assign_course_to_student(
    student_id: int,
    course_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Faol o'quvchi topilmadi"
        )

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Faol kurs topilmadi"
        )

    # Bir o'quvchiga bir xil kursni parallel biriktirishda duplicate
    # StudentCourse qatori yaratilmasligi uchun student qatorini qulflaymiz.
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.is_active == True
    ).with_for_update().first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Faol o'quvchi topilmadi"
        )

    existing = db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id
    ).first()

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=409,
                detail="Bu kurs o'quvchiga allaqachon biriktirilgan"
            )

        existing.is_active = True

        db.commit()

        return {
            "success": True,
            "message": "Kurs qayta biriktirildi",
            "student_id": student_id,
            "course_id": course_id
        }

    student_course = StudentCourse(
        student_id=student_id,
        course_id=course_id,
        progress=0,
        is_active=True
    )

    db.add(student_course)
    db.commit()
    db.refresh(student_course)

    return {
        "success": True,
        "message": "Kurs o'quvchiga biriktirildi",
        "student_id": student_id,
        "course_id": course_id,
        "student_course_id": student_course.id
    }


# =========================================================
# COURSE DETAIL / COMMAND CENTER
# =========================================================

@router.get("/{course_id}")
def get_admin_course(
    course_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    category = db.query(Category).filter(
        Category.id == course.category_id
    ).first()

    modules = db.query(CourseModule).filter(
        CourseModule.course_id == course.id
    ).order_by(
        CourseModule.sort_order,
        CourseModule.id
    ).all()

    module_result = []

    total_lessons = 0

    for module in modules:
        lessons = db.query(Lesson).filter(
            Lesson.module_id == module.id
        ).order_by(
            Lesson.sort_order,
            Lesson.id
        ).all()

        lesson_result = []

        for lesson in lessons:
            lesson_result.append({
                "id": lesson.id,
                "title": lesson.title,
                "content": lesson.content,
                "video_url": lesson.video_url,
                "sort_order": lesson.sort_order,
                "is_active": lesson.is_active
            })

        total_lessons += len(lesson_result)

        module_result.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "sort_order": module.sort_order,
            "is_active": module.is_active,
            "lessons_count": len(lesson_result),
            "lessons": lesson_result
        })

    students_count = db.query(StudentCourse).filter(
        StudentCourse.course_id == course.id,
        StudentCourse.is_active == True
    ).count()

    return {
        "course": {
            "id": course.id,
            "name": course.name,
            "description": course.description,

            "category": {
                "id": category.id if category else None,
                "name": category.name if category else None,
                "icon": category.icon if category else None
            },

            "age_min": course.age_min,
            "age_max": course.age_max,
            "lesson_minutes": course.lesson_minutes,
            "lessons_per_week": course.lessons_per_week,

            "price_min": course.price_min,
            "price_max": course.price_max,

            "sort_order": course.sort_order,
            "is_active": course.is_active
        },

        "statistics": {
            "students_count": students_count,
            "modules_count": len(module_result),
            "lessons_count": total_lessons
        },

        "modules": module_result
    }


# =========================================================
# CREATE COURSE
# =========================================================

@router.post("/")
def create_course(
    data: CourseCreate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.is_active == True
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Faol kategoriya topilmadi"
        )

    course_name = data.name.strip()
    if not course_name:
        raise HTTPException(status_code=400, detail="Kurs nomi bo'sh bo'lishi mumkin emas")

    existing = db.query(Course).filter(
        Course.name == course_name,
        Course.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Bu nomdagi faol kurs allaqachon mavjud"
        )
        raise HTTPException(status_code=400, detail="Kurs nomi bo'sh bo'lishi mumkin emas")

    if (
        data.age_min is not None
        and data.age_max is not None
        and data.age_min > data.age_max
    ):
        raise HTTPException(
            status_code=400,
            detail="age_min age_max dan katta bo'lishi mumkin emas"
        )

    if (
        data.price_min is not None
        and data.price_max is not None
        and data.price_min > data.price_max
    ):
        raise HTTPException(
            status_code=400,
            detail="price_min price_max dan katta bo'lishi mumkin emas"
        )

    course = Course(
        category_id=data.category_id,
        name=course_name,
        description=data.description,

        age_min=data.age_min,
        age_max=data.age_max,

        lesson_minutes=data.lesson_minutes,
        lessons_per_week=data.lessons_per_week,

        price_min=data.price_min,
        price_max=data.price_max,

        sort_order=data.sort_order,
        is_active=True
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "success": True,
        "message": "Kurs muvaffaqiyatli yaratildi",
        "course_id": course.id
    }


# =========================================================
# UPDATE COURSE
# =========================================================

@router.put("/{course_id}")
def update_course(
    course_id: int,
    data: CourseUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        update_data["name"] = update_data["name"].strip()
        if not update_data["name"]:
            raise HTTPException(status_code=400, detail="Kurs nomi bo'sh bo'lishi mumkin emas")

    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"],
            Category.is_active == True
        ).first()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Faol kategoriya topilmadi"
            )

    if "name" in update_data:
        duplicate = db.query(Course).filter(
            Course.name == update_data["name"],
            Course.id != course_id,
            Course.is_active == True
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Bu nomdagi faol kurs allaqachon mavjud"
            )

    new_age_min = update_data.get(
        "age_min",
        course.age_min
    )

    new_age_max = update_data.get(
        "age_max",
        course.age_max
    )

    if (
        new_age_min is not None
        and new_age_max is not None
        and new_age_min > new_age_max
    ):
        raise HTTPException(
            status_code=400,
            detail="age_min age_max dan katta bo'lishi mumkin emas"
        )

    new_price_min = update_data.get(
        "price_min",
        course.price_min
    )

    new_price_max = update_data.get(
        "price_max",
        course.price_max
    )

    if (
        new_price_min is not None
        and new_price_max is not None
        and new_price_min > new_price_max
    ):
        raise HTTPException(
            status_code=400,
            detail="price_min price_max dan katta bo'lishi mumkin emas"
        )

    for field, value in update_data.items():
        setattr(
            course,
            field,
            value
        )

    db.commit()
    db.refresh(course)

    return {
        "success": True,
        "message": "Kurs ma'lumotlari yangilandi",
        "course_id": course.id
    }


# =========================================================
# DEACTIVATE COURSE
# =========================================================

@router.put("/{course_id}/deactivate")
def deactivate_course(
    course_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    course.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Kurs deaktiv qilindi",
        "course_id": course.id
    }


# =========================================================
# ACTIVATE COURSE
# =========================================================

@router.put("/{course_id}/activate")
def activate_course(
    course_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    category = db.query(Category).filter(
        Category.id == course.category_id,
        Category.is_active == True
    ).first()
    if not category:
        raise HTTPException(
            status_code=400,
            detail="Kursni faollashtirish uchun uning kategoriyasi faol bo‘lishi kerak"
        )

    duplicate = db.query(Course).filter(
        Course.name == course.name,
        Course.id != course.id,
        Course.is_active == True
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Bu nomdagi faol kurs allaqachon mavjud"
        )

    course.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "Kurs qayta faollashtirildi",
        "course_id": course.id
    }


# =========================================================
# CREATE MODULE
# =========================================================

@router.post("/{course_id}/modules")
def create_module(
    course_id: int,
    data: ModuleCreate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    if not course.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv kursga modul qo'shib bo'lmaydi"
        )

    module_title = data.title.strip()
    if not module_title:
        raise HTTPException(status_code=400, detail="Modul nomi bo'sh bo'lishi mumkin emas")

    module = CourseModule(
        course_id=course_id,
        title=module_title,
        description=data.description,
        sort_order=data.sort_order,
        is_active=True
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return {
        "success": True,
        "message": "Modul yaratildi",
        "module_id": module.id,
        "course_id": course_id
    }


# =========================================================
# UPDATE MODULE
# =========================================================

@router.put("/{course_id}/modules/{module_id}")
def update_module(
    course_id: int,
    module_id: int,
    data: ModuleUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    course = get_course_or_404(course_id, db)
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Deaktiv kursdagi modulni yangilab bo'lmaydi")

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "title" in update_data:
        update_data["title"] = update_data["title"].strip()
        if not update_data["title"]:
            raise HTTPException(status_code=400, detail="Modul nomi bo'sh bo'lishi mumkin emas")

    for field, value in update_data.items():
        setattr(
            module,
            field,
            value
        )

    db.commit()
    db.refresh(module)

    return {
        "success": True,
        "message": "Modul yangilandi",
        "module_id": module.id
    }


# =========================================================
# DEACTIVATE MODULE
# =========================================================

@router.put("/{course_id}/modules/{module_id}/deactivate")
def deactivate_module(
    course_id: int,
    module_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    module.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Modul deaktiv qilindi",
        "module_id": module.id
    }


# =========================================================
# ACTIVATE MODULE
# =========================================================

@router.put("/{course_id}/modules/{module_id}/activate")
def activate_module(
    course_id: int,
    module_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    course = get_course_or_404(
        course_id,
        db
    )
    if not course.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv kursdagi modulni faollashtirib bo'lmaydi"
        )

    module.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "Modul faollashtirildi",
        "module_id": module.id
    }


# =========================================================
# DELETE MODULE
# =========================================================

@router.delete("/{course_id}/modules/{module_id}")
def delete_module(
    course_id: int,
    module_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    lessons_count = db.query(Lesson).filter(
        Lesson.module_id == module.id
    ).count()

    if lessons_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Bu modulda darslar mavjud. "
                "Avval darslarni o'chiring yoki modulni deaktiv qiling."
            )
        )

    db.delete(module)
    db.commit()

    return {
        "success": True,
        "message": "Modul o'chirildi",
        "module_id": module.id
    }


# =========================================================
# CREATE LESSON
# =========================================================

@router.post("/{course_id}/modules/{module_id}/lessons")
def create_lesson(
    course_id: int,
    module_id: int,
    data: LessonCreate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    if not course.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv kursga dars qo'shib bo'lmaydi"
        )

    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    if not module.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv modulga dars qo'shib bo'lmaydi"
        )

    lesson_title = data.title.strip()
    if not lesson_title:
        raise HTTPException(status_code=400, detail="Dars nomi bo'sh bo'lishi mumkin emas")

    lesson = Lesson(
        module_id=module.id,
        title=lesson_title,
        content=data.content,
        video_url=data.video_url,
        sort_order=data.sort_order,
        is_active=True
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {
        "success": True,
        "message": "Dars yaratildi",
        "lesson_id": lesson.id,
        "module_id": module.id,
        "course_id": course.id
    }


# =========================================================
# UPDATE LESSON
# =========================================================

@router.put("/{course_id}/modules/{module_id}/lessons/{lesson_id}")
def update_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
    data: LessonUpdate,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Deaktiv kursdagi darsni yangilab bo'lmaydi")

    module = get_module_or_404(
        course_id,
        module_id,
        db
    )
    if not module.is_active:
        raise HTTPException(status_code=400, detail="Deaktiv moduldagi darsni yangilab bo'lmaydi")

    lesson = get_lesson_or_404(
        module_id,
        lesson_id,
        db
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            lesson,
            field,
            value
        )

    db.commit()
    db.refresh(lesson)

    return {
        "success": True,
        "message": "Dars yangilandi",
        "lesson_id": lesson.id
    }


# =========================================================
# DEACTIVATE LESSON
# =========================================================

@router.put("/{course_id}/modules/{module_id}/lessons/{lesson_id}/deactivate")
def deactivate_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    get_course_or_404(
        course_id,
        db
    )

    lesson = get_lesson_or_404(
        module_id,
        lesson_id,
        db
    )

    lesson.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Dars deaktiv qilindi",
        "lesson_id": lesson.id
    }


# =========================================================
# ACTIVATE LESSON
# =========================================================

@router.put("/{course_id}/modules/{module_id}/lessons/{lesson_id}/activate")
def activate_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    course = get_course_or_404(
        course_id,
        db
    )

    if not course.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv kursdagi darsni faollashtirib bo'lmaydi"
        )

    module = get_module_or_404(
        course_id,
        module_id,
        db
    )

    if not module.is_active:
        raise HTTPException(
            status_code=400,
            detail="Deaktiv moduldagi darsni faollashtirib bo'lmaydi"
        )

    lesson = get_lesson_or_404(
        module_id,
        lesson_id,
        db
    )

    lesson.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "Dars faollashtirildi",
        "lesson_id": lesson.id
    }


# =========================================================
# DELETE LESSON
# =========================================================

@router.delete("/{course_id}/modules/{module_id}/lessons/{lesson_id}")
def delete_lesson(
    course_id: int,
    module_id: int,
    lesson_id: int,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    get_course_or_404(
        course_id,
        db
    )

    lesson = get_lesson_or_404(
        module_id,
        lesson_id,
        db
    )

    quiz_count = db.query(LessonQuiz).filter(
        LessonQuiz.lesson_id == lesson.id
    ).count()
    progress_count = db.query(LessonProgress).filter(
        LessonProgress.lesson_id == lesson.id
    ).count()

    if quiz_count or progress_count:
        raise HTTPException(
            status_code=400,
            detail="Bu darsda quiz yoki o'quvchi progressi mavjud. Avval ularni o'chiring yoki darsni deaktiv qiling."
        )

    db.delete(lesson)
    db.commit()

    return {
        "success": True,
        "message": "Dars o'chirildi",
        "lesson_id": lesson.id
    }


# =========================================================
# ASSIGN COURSE TO STUDENT
# =========================================================
