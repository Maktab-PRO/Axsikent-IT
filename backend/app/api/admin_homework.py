@router.get("/")
def get_admin_homeworks(
    search: str | None = Query(
        default=None,
        max_length=150
    ),
    status: str | None = Query(
        default=None,
        max_length=20
    ),
    group_id: int | None = None,
    teacher_id: int | None = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    query = db.query(Homework)

    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            Homework.title.ilike(search_value) |
            Homework.description.ilike(search_value)
        )

    if status:
        query = query.filter(
            Homework.status == status.strip().lower()
        )

    if group_id:
        query = query.filter(
            Homework.group_id == group_id
        )

    if teacher_id:
        query = query.filter(
            Homework.teacher_id == teacher_id
        )

    homeworks = query.order_by(
        Homework.created_at.desc()
    ).all()

    return {
        "total": len(homeworks),
        "homeworks": [
            homework_to_dict(
                homework,
                db
            )
            for homework in homeworks
        ]
    }


# =========================================================
# 2. HOMEWORK STATISTICS
# =========================================================

@router.get("/stats/summary")
def get_homework_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    total = db.query(Homework).count()

    active = db.query(Homework).filter(
        Homework.status == "active"
    ).count()

    inactive = db.query(Homework).filter(
        Homework.status == "inactive"
    ).count()

    submissions = db.query(
        HomeworkSubmission
    ).count()

    checked = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.status == "checked"
    ).count()

    pending = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.status == "submitted"
    ).count()

    return {
        "total_homework": total,
        "active_homework": active,
        "inactive_homework": inactive,
        "total_submissions": submissions,
        "checked_submissions": checked,
        "pending_submissions": pending
    }

    # =========================================================
# 3. GET ALL SUBMISSIONS
# =========================================================

@router.get("/ai-submissions")
def get_all_ai_submissions(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    items = db.query(AITelegramSubmission).order_by(AITelegramSubmission.id.desc()).all()
    result = []
    for item in items:
        student = db.query(Student).filter(Student.id == item.student_id).first()
        result.append({
            "id": item.id,
            "source": "telegram_ai",
            "student_id": item.student_id,
            "student_name": student.full_name if student else None,
            "homework_id": None,
            "homework_title": "🤖 AKHSIKENT AI / Telegram",
            "task": item.task,
            "answer": item.answer,
            "status": item.status,
            "score": item.score,
            "passed": item.passed == "true",
            "mistakes": json.loads(item.mistakes) if item.mistakes else [],
            "explanation": item.explanation,
            "recommendation": item.recommendation,
            "submitted_at": item.submitted_at,
            "checked_at": item.checked_at
        })
    return {"total": len(result), "submissions": result}


@router.get("/submissions")
def get_all_admin_submissions(
    status: str | None = Query(
        default=None,
        max_length=30
    ),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    query = db.query(
        HomeworkSubmission
    )

    if status:
        query = query.filter(
            HomeworkSubmission.status ==
            status.strip().lower()
        )

    submissions = query.order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "total": len(submissions),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }
# =========================================================
# 3. GET SINGLE HOMEWORK
# =========================================================

@router.get("/ai-submissions/{submission_id}")
def get_admin_ai_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    item = db.query(AITelegramSubmission).filter(AITelegramSubmission.id == submission_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="AI topshiriq topilmadi.")
    student = db.query(Student).filter(Student.id == item.student_id).first()
    return {
        "id": item.id,
        "source": "telegram_ai",
        "student_id": item.student_id,
        "student_name": student.full_name if student else None,
        "homework_title": "🤖 AKHSIKENT AI / Telegram",
        "task": item.task,
        "answer": item.answer,
        "score": item.score,
        "passed": item.passed == "true",
        "mistakes": json.loads(item.mistakes) if item.mistakes else [],
        "explanation": item.explanation,
        "recommendation": item.recommendation,
        "status": item.status,
        "submitted_at": item.submitted_at,
        "checked_at": item.checked_at
    }

@router.get("/submissions/{submission_id}")
def get_admin_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = get_submission_or_404(
        submission_id,
        db
    )

    return submission_to_dict(
        submission,
        db
    )


# =========================================================
# 10. GRADE SUBMISSION
# =========================================================
@router.get("/{homework_id}")
def get_admin_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    submissions = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    ).order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "homework": homework_to_dict(
            homework,
            db
        ),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }


# =========================================================
# 4. CREATE HOMEWORK
# =========================================================

@router.post("/")
def create_admin_homework(
    data: HomeworkCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    group = db.query(Group).filter(
        Group.id == data.group_id,
        Group.is_active == True
    ).first()

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Faol guruh topilmadi."
        )

    teacher = db.query(Teacher).filter(
        Teacher.id == data.teacher_id,
        Teacher.is_active == True
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Faol o‘qituvchi topilmadi."
        )

    homework = Homework(
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        title=data.title.strip(),
        description=data.description.strip(),
        deadline=data.deadline,
        status="active"
    )

    db.add(homework)
    db.commit()
    db.refresh(homework)

    notify_group_students(
        db,
        group_id=homework.group_id,
        title="📚 Yangi uy vazifasi",
        message=f"{homework.title} uy vazifasi sizga biriktirildi.",
        notification_type="homework",
    )

    return {
        "message": "Uy vazifasi yaratildi.",
        "homework": homework_to_dict(
            homework,
            db
        )
    }


# =========================================================
# 5. UPDATE HOMEWORK
# =========================================================

@router.put("/{homework_id}")
def update_admin_homework(
    homework_id: int,
    data: HomeworkUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    if data.group_id is not None:

        group = db.query(Group).filter(
            Group.id == data.group_id,
            Group.is_active == True
        ).first()

        if not group:
            raise HTTPException(
                status_code=404,
                detail="Faol guruh topilmadi."
            )

        homework.group_id = data.group_id

    if data.teacher_id is not None:

        teacher = db.query(Teacher).filter(
            Teacher.id == data.teacher_id,
            Teacher.is_active == True
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Faol o‘qituvchi topilmadi."
            )

        homework.teacher_id = data.teacher_id

    if data.title is not None:
        homework.title = data.title.strip()

    if data.description is not None:
        homework.description = data.description.strip()

    if data.deadline is not None:
        homework.deadline = data.deadline

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi yangilandi.",
        "homework": homework_to_dict(
            homework,
            db
        )
    }


# =========================================================
# 6. DEACTIVATE HOMEWORK
# =========================================================

@router.put("/{homework_id}/deactivate")
def deactivate_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    homework.status = "inactive"

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi deaktivatsiya qilindi.",
        "homework_id": homework.id,
        "status": homework.status
    }


# =========================================================
# 7. ACTIVATE HOMEWORK
# =========================================================

@router.put("/{homework_id}/activate")
def activate_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    homework.status = "active"

    db.commit()
    db.refresh(homework)

    return {
        "message": "Uy vazifasi faollashtirildi.",
        "homework_id": homework.id,
        "status": homework.status
    }


# =========================================================
# 8. GET SUBMISSIONS
# =========================================================

@router.get("/{homework_id}/submissions")
def get_admin_submissions(
    homework_id: int,
    status: str | None = Query(
        default=None,
        max_length=30
    ),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    get_homework_or_404(
        homework_id,
        db
    )

    query = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    )

    if status:
        query = query.filter(
            HomeworkSubmission.status ==
            status.strip().lower()
        )

    submissions = query.order_by(
        HomeworkSubmission.id.desc()
    ).all()

    return {
        "total": len(submissions),
        "submissions": [
            submission_to_dict(
                submission,
                db
            )
            for submission in submissions
        ]
    }


# =========================================================
# 9. GET SINGLE SUBMISSION
# =========================================================

@router.put("/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    data: SubmissionGrade,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = get_submission_or_404(
        submission_id,
        db
    )

    submission.score = data.score
    submission.teacher_comment = data.teacher_comment
    submission.status = "checked"
    submission.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    homework = db.query(Homework).filter(
        Homework.id == submission.homework_id
    ).first()
    if homework:
        notify_student(
            db,
            student_id=submission.student_id,
            title="📝 Uy vazifasi baholandi",
            message=f"{homework.title}: {submission.score}/100" + (
                f" — {submission.teacher_comment}"
                if submission.teacher_comment else ""
            ),
            notification_type="homework_result",
        )

    return {
        "message": "Topshiriq baholandi.",
        "submission": submission_to_dict(
            submission,
            db
        )
    }


# =========================================================
# 11. UPDATE SUBMISSION STATUS
# =========================================================

@router.put("/submissions/{submission_id}/status")
def update_submission_status(
    submission_id: int,
    data: SubmissionStatusUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    submission = get_submission_or_404(
        submission_id,
        db
    )

    new_status = data.status.strip().lower()

    if new_status not in ALLOWED_SUBMISSION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Noto‘g‘ri submission status. "
                "Ruxsat etilganlar: "
                "submitted, checked, late, rejected."
            )
        )

    submission.status = new_status

    if new_status == "checked":
        submission.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    return {
        "message": "Topshiriq statusi yangilandi.",
        "submission": submission_to_dict(
            submission,
            db
        )
    }


# =========================================================
# 12. DELETE HOMEWORK
# =========================================================

@router.delete("/{homework_id}")
def delete_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):

    homework = get_homework_or_404(
        homework_id,
        db
    )

    submission_count = db.query(
        HomeworkSubmission
    ).filter(
        HomeworkSubmission.homework_id == homework_id
    ).count()

    if submission_count > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                "Bu uy vazifasiga topshiriqlar mavjud. "
                "O‘chirish o‘rniga deaktivatsiya qiling."
            )
        )

    db.delete(homework)
    db.commit()

    return {
        "message": "Uy vazifasi o‘chirildi.",
        "homework_id": homework_id
  }
