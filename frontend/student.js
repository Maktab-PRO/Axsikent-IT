const API_URL = "https://axsikent-it-4.onrender.com";
    /* =========================
   LOAD STUDENT COURSES
========================= */

async function loadStudentCourses() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    const container = document.getElementById("studentCourses");

    try {

        const response = await fetch(
            `${API_URL}/students/courses`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.status === 401) {

            localStorage.removeItem("access_token");
            localStorage.removeItem("user_role");

            window.location.href = "index.html";
            return;
        }

        const courses = await response.json();

        if (!response.ok) {

            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:25px;
                    color:#dc2626;
                ">
                    Kurslarni yuklashda xatolik yuz berdi.
                </div>
            `;

            return;
        }

        if (!courses.length) {

            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:25px;
                    color:#7b8496;
                ">
                    <div class="student-modern-empty-icon student-homework-empty-icon" style="margin-bottom:14px;">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h10a2 2 0 0 1 2 2v16H5V5a2 2 0 0 1 2-2Z"/><path d="M9 3v3h6V3M9 11h6M9 15h4"/></svg>
                    </div>

                    <strong style="
                        display:block;
                        color:#172033;
                        margin-bottom:7px;
                    ">
                        Hozircha kurs biriktirilmagan
                    </strong>

                    <span style="font-size:13px;">
                        Administrator sizga kurs biriktirganda
                        shu yerda ko‘rinadi.
                    </span>
                </div>
            `;

            return;
        }

        container.innerHTML = courses.map(course => {

            const progress = Math.min(
                100,
                Math.max(0, Number(course.progress) || 0)
            );

            return `
                <div
                    class="course"
                    onclick="openStudentCourse(${course.id})"
                    style="cursor:pointer;"
                >

                    <div class="course-top">

                        <div class="course-icon student-modern-course-icon">
                            <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="11" rx="2"/><path d="M8 20h8M12 16v4"/></svg>
                        </div>

                        <div>
                            <div class="course-name">
                                ${course.name}
                            </div>
                            
                          <div class="course-info">
                            Kurs davom etmoqda
                            </div>
                        </div>

                    </div>

                    <div class="progress">

                        <div
                            class="progress-bar"
                            style="width:${progress}%"
                        ></div>

                    </div>

                    <div class="progress-text">

                        <span>
                            Jarayon
                        </span>

                        <span>
                            ${progress}%
                        </span>

                    </div>

                </div>
            `;

        }).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:25px;
                color:#dc2626;
            ">
                Server bilan bog‘lanishda xatolik.
            </div>
        `;
    }
}


    /* =========================
       LOAD STUDENT
    ========================= */
async function openStudentCourse(courseId) {

    const token = localStorage.getItem("access_token");
    const container = document.getElementById("studentCourses");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:40px 20px;
            color:#94a3b8;
        ">
            <div class="student-modern-loading-icon student-loading-modules"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5a2 2 0 0 1 2-2h11v18H7a2 2 0 0 1-2-2V5Z"/><path d="M5 7h10M9 11h5M9 15h5"/></svg></div>

            <div style="
                font-size:15px;
                font-weight:600;
            ">
                Modullar yuklanmoqda...
            </div>
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/students/courses/${courseId}/modules`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const modules = await response.json();

        if (!response.ok) {
            throw new Error("Modullarni yuklashda xatolik");
        }

        if (!modules.length) {
            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:40px 20px;
                    color:#94a3b8;
                    background:#111827;
                    border:1px solid #1f2937;
                    border-radius:18px;
                ">
                    <div style="font-size:35px;">📚</div>

                    <div style="
                        margin-top:10px;
                        font-size:16px;
                        font-weight:700;
                        color:#f8fafc;
                    ">
                        Modullar mavjud emas
                    </div>

                    <div style="
                        margin-top:6px;
                        font-size:13px;
                    ">
                        Bu kursga hali modullar qo‘shilmagan.
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div style="
                margin-bottom:18px;
            ">
                <button
                    onclick="loadStudentCourses()"
                    style="
                        border:1px solid #263244;
                        background:#111827;
                        color:#d1d5db;
                        padding:10px 15px;
                        border-radius:11px;
                        cursor:pointer;
                        font-weight:600;
                    "
                >
                    ← Kurslarga qaytish
                </button>
            </div>

            <div style="
                margin-bottom:18px;
            ">
                <div style="
                    color:#94a3b8;
                    font-size:13px;
                    margin-bottom:5px;
                ">
                    📖 Kurs tarkibi
                </div>

                <div style="
                    color:#ffffff;
                    font-size:22px;
                    font-weight:800;
                ">
                    Modullar
                </div>
            </div>

            ${modules.map((module, index) => {

                const progress = Number(module.progress || 0);
                const completed = Number(module.completed_lessons || 0);
                const total = Number(module.total_lessons || 0);

                let progressText = "";

                if (total > 0) {
                    progressText = `${completed} / ${total} dars`;
                } else {
                    progressText = "Darslar tez orada";
                }

                return `
                    <div
                        onclick="openStudentModule(${courseId}, ${module.id})"
                        style="
                            padding:18px;
                            margin-bottom:14px;
                            border:1px solid #1f2937;
                            border-radius:18px;
                            cursor:pointer;
                            background:
                                linear-gradient(
                                    145deg,
                                    #111827,
                                    #0b1220
                                );
                            box-shadow:
                                0 8px 25px rgba(0,0,0,0.20);
                            transition:all 0.2s ease;
                        "
                    >

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            gap:10px;
                        ">

                            <div style="
                                font-size:12px;
                                color:#64748b;
                                font-weight:700;
                                text-transform:uppercase;
                                letter-spacing:0.5px;
                            ">
                                Modul ${index + 1}
                            </div>

                            <div style="
                                font-size:13px;
                                font-weight:800;
                                color:${progress === 100 ? "#22c55e" : "#84cc16"};
                            ">
                                ${progress}%
                            </div>

                        </div>

                        <div style="
                            margin-top:9px;
                            display:flex;
                            align-items:center;
                            gap:11px;
                            font-size:17px;
                            font-weight:800;
                            color:#f8fafc;
                        ">
                            <span class="student-modern-module-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h13a1 1 0 0 1 1 1v15H7a2 2 0 0 0-2 2V4Z"/><path d="M7 20h12M9 8h7M9 12h7"/></svg></span>
                            <span>${module.title}</span>
                        </div>

                        <div style="
                            margin-top:7px;
                            font-size:13px;
                            line-height:1.5;
                            color:#94a3b8;
                        ">
                            ${module.description || "Modulni ochish va darslarni boshlash"}
                        </div>

                        <div style="
                            margin-top:16px;
                        ">

                            <div style="
                                height:7px;
                                background:#1f2937;
                                border-radius:10px;
                                overflow:hidden;
                            ">

                                <div style="
                                    width:${progress}%;
                                    height:100%;
                                    background:
                                        linear-gradient(
                                            90deg,
                                            #22c55e,
                                            #84cc16
                                        );
                                    border-radius:10px;
                                    transition:width 0.4s ease;
                                "></div>

                            </div>

                            <div style="
                                display:flex;
                                justify-content:space-between;
                                align-items:center;
                                margin-top:9px;
                            ">

                                <span style="
                                    font-size:12px;
                                    color:#64748b;
                                ">
                                    ${progressText}
                                </span>

                                <span style="
                                    font-size:12px;
                                    font-weight:700;
                                    color:${progress === 100 ? "#22c55e" : "#94a3b8"};
                                ">
                                    ${progress === 100 ? "✅ Tugatilgan" : "▶ Davom etish"}
                                </span>

                            </div>

                        </div>

                    </div>
                `;
            }).join("")}
        `;

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:35px 20px;
                color:#f87171;
                background:#111827;
                border:1px solid #3f1d1d;
                border-radius:18px;
            ">
                <div style="font-size:32px;">⚠️</div>

                <div style="
                    margin-top:10px;
                    font-weight:700;
                ">
                    Modullarni yuklashda xatolik yuz berdi.
                </div>
            </div>
        `;
    }
}

async function openStudentModule(courseId, moduleId) {

    const token = localStorage.getItem("access_token");
    const container = document.getElementById("studentCourses");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:25px;
            color:#7b8496;
        ">
            <span class="student-modern-loading-icon student-loading-lessons"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v16H6z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg></span> Darslar yuklanmoqda...
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const lessons = await response.json();

        if (!response.ok) {
            throw new Error("Darslarni yuklashda xatolik");
        }

        if (!lessons.length) {

            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:25px;
                    color:#7b8496;
                ">
                    📖 Bu modulda hozircha darslar mavjud emas.
                </div>
            `;

            return;
        }

        container.innerHTML = `
            <div style="margin-bottom:15px;">

                <button
                    onclick="openStudentCourse(${courseId})"
                    style="
                        border:none;
                        background:#eef2f7;
                        padding:9px 14px;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    ← Modullarga qaytish
                </button>

            </div>

            ${lessons.map((lesson, index) => `
    <div
        onclick="openStudentLesson(${courseId}, ${moduleId}, ${lesson.id})"
        style="
            padding:20px;
            margin-bottom:14px;
            border:1px solid #1f2937;
            border-radius:18px;
            background:
                linear-gradient(
                    145deg,
                    #111827,
                    #0b1220
                );
            cursor:pointer;
            box-shadow:0 8px 25px rgba(0,0,0,.20);
            transition:all .2s ease;
        "
    >

        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:12px;
        ">

            <div style="
                display:flex;
                align-items:center;
                gap:13px;
            ">

                <div class="student-modern-lesson-icon ${lesson.completed ? "completed" : ""}" style="
                    width:46px;
                    height:46px;
                    border-radius:14px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    background:
                        ${lesson.completed
                            ? "rgba(34,197,94,.12)"
                            : "rgba(59,130,246,.12)"
                        };
                    border:1px solid
                        ${lesson.completed
                            ? "rgba(34,197,94,.25)"
                            : "rgba(59,130,246,.25)"
                        };
                    font-size:21px;
                ">
                    ${lesson.completed ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 12 4 4 8-9"/></svg>' : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 6a2 2 0 0 1 2-2h5v16H7a2 2 0 0 0-2 2V6Z"/><path d="M12 4h5a2 2 0 0 1 2 2v16h-7V4Z"/><path d="m10 10 4 2-4 2v-4Z"/></svg>'}
                </div>

                <div>

                    <div style="
                        font-size:11px;
                        color:#64748b;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:.6px;
                    ">
                        Dars ${index + 1}
                    </div>

                    <div style="
                        margin-top:4px;
                        font-size:16px;
                        color:#f8fafc;
                        font-weight:800;
                    ">
                        ${lesson.title}
                    </div>

                </div>

            </div>

            <div style="
                color:#22c55e;
                font-size:20px;
            ">
                →
            </div>

        </div>

        <div style="
            margin-top:14px;
            color:#64748b;
            font-size:12px;
        ">
            ${lesson.completed
                ? "✅ Bu dars tugallangan"
                : "📖 Darsni ochish va o‘rganishni boshlash"
            }
        </div>

    </div>
`).join("")}
        `;

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:25px;
                color:#dc2626;
            ">
                Darslarni yuklashda xatolik yuz berdi.
            </div>
        `;
    }
}

        async function openStudentLesson(courseId, moduleId, lessonId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const container = document.getElementById("studentCourses");

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:40px;
            color:#94a3b8;
        ">
            📖 Dars yuklanmoqda...
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const lessons = await response.json();

        if (!response.ok) {
            throw new Error(
                "Dars ma'lumotlarini yuklashda xatolik"
            );
        }

        const lesson = lessons.find(
            item => Number(item.id) === Number(lessonId)
        );

        if (!lesson) {
            throw new Error("Dars topilmadi");
        }

        container.innerHTML = `

            <div style="
                max-width:850px;
                margin:0 auto;
            ">

                <button
                    onclick="openStudentModule(${courseId}, ${moduleId})"
                    style="
                        border:1px solid #263244;
                        background:#111827;
                        color:#d1d5db;
                        padding:10px 15px;
                        border-radius:11px;
                        cursor:pointer;
                        font-weight:600;
                        margin-bottom:20px;
                    "
                >
                    ← Darslar ro‘yxatiga qaytish
                </button>


                <div style="
                    background:
                        linear-gradient(
                            145deg,
                            #111827,
                            #0b1220
                        );
                    border:1px solid #1f2937;
                    border-radius:22px;
                    padding:25px;
                    box-shadow:
                        0 15px 40px rgba(0,0,0,.25);
                ">

                    <div style="
                        color:#4ade80;
                        font-size:12px;
                        font-weight:800;
                        letter-spacing:1px;
                        text-transform:uppercase;
                    ">
                        📖 DARS ${lessonId}
                    </div>


                    <h1 style="
                        margin-top:10px;
                        font-size:26px;
                        color:#f8fafc;
                    ">
                        ${lesson.title}
                    </h1>


                    <div style="
                        margin-top:25px;
                        padding:22px;
                        background:#080d16;
                        border:1px solid #1f2937;
                        border-radius:16px;
                        color:#cbd5e1;
                        font-size:15px;
                        line-height:1.8;
                    ">
                        ${
                            lesson.content
                            || `
                                <div style="
                                    color:#64748b;
                                    text-align:center;
                                    padding:25px;
                                ">
                                    📚 Bu dars uchun hozircha matn
                                    mavjud emas.
                                </div>
                            `
                        }
                    </div>


                    ${
                        lesson.video_url
                        ? `
                            <div style="
                                margin-top:20px;
                            ">
                                <a
                                    href="${lesson.video_url}"
                                    target="_blank"
                                    style="
                                        display:block;
                                        text-align:center;
                                        padding:13px;
                                        border-radius:12px;
                                        background:#1d4ed8;
                                        color:white;
                                        text-decoration:none;
                                        font-weight:700;
                                    "
                                >
                                    ▶️ Dars videosini ko‘rish
                                </a>
                            </div>
                        `
                        : ""
                    }


                    <div style="
                        margin-top:25px;
                    ">

                        ${
                            lesson.completed
                            ? `
                                <button
                                    disabled
                                    style="
                                        width:100%;
                                        border:none;
                                        background:#166534;
                                        color:white;
                                        padding:15px;
                                        border-radius:12px;
                                        font-weight:800;
                                    "
                                >
                                    ✅ Dars tugallangan
                                </button>
                            `
                            : `
                                <button
                                    onclick="
                                        markLessonRead(
                                            ${courseId},
                                            ${moduleId},
                                            ${lessonId}
                                        )
                                    "
                                    style="
                                        width:100%;
                                        border:none;
                                        background:
                                            linear-gradient(
                                                135deg,
                                                #16a34a,
                                                #22c55e
                                            );
                                        color:white;
                                        padding:15px;
                                        border-radius:12px;
                                        font-weight:800;
                                        cursor:pointer;
                                    "
                                >
                                    📖 Darsni o‘qidim
                                </button>
                            `
                        }

                    </div>

                </div>

            </div>
        `;

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:30px;
                color:#f87171;
            ">
                ❌ ${error.message}
            </div>
        `;
    }
}
        async function markLessonRead(courseId, moduleId, lessonId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const container = document.getElementById("studentCourses");

    try {

        const response = await fetch(
            `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/read`,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Darsni o‘qilgan deb belgilashda xatolik"
            );
        }

        container.innerHTML = `
            <div style="
                max-width:700px;
                margin:40px auto;
                text-align:center;
                background:#111827;
                border:1px solid #1f2937;
                border-radius:20px;
                padding:30px;
            ">

                <div style="
                    font-size:45px;
                    margin-bottom:15px;
                ">
                    ✅
                </div>

                <h2 style="
                    color:#f8fafc;
                    margin-bottom:10px;
                ">
                    Dars o‘qildi
                </h2>

                <p style="
                    color:#94a3b8;
                    line-height:1.6;
                ">
                    Endi dars bo‘yicha bilimingizni tekshiring.
                </p>

                <button
                    onclick="
                        startLessonQuiz(
                            ${courseId},
                            ${moduleId},
                            ${lessonId}
                        )
                    "
                    style="
                        width:100%;
                        margin-top:20px;
                        border:none;
                        background:
                            linear-gradient(
                            135deg,
                            #0f766e,
                            #34d399
                            );
                        color:white;
                        padding:15px;
                        border-radius:12px;
                        font-weight:800;
                        font-size:15px;
                        cursor:pointer;
                    "
                >
                    📝 Darsni tekshirish
                </button>

            </div>
        `;

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:30px;
                color:#f87171;
            ">
                ❌ ${error.message}
            </div>
        `;
    }
}

        async function startLessonQuiz(courseId, moduleId, lessonId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const container = document.getElementById("studentCourses");

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:40px 20px;
            color:#7b8496;
        ">
            <div class="student-modern-loading-icon student-loading-check"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v16H6z"/><path d="m9 12 2 2 4-4"/></svg></div>
            <div style="margin-top:10px;font-weight:600;">
                Tekshiruv yuklanmoqda...
            </div>
        </div>    `;
    try {

        const response = await fetch(
            `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/quiz`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const quizzes = await response.json();

        if (!response.ok) {
            throw new Error(
                quizzes.detail || "Tekshiruvni yuklashda xatolik"
            );
        }

        if (!quizzes.length) {
            throw new Error(
                "Bu dars uchun tekshiruv mavjud emas."
            );
        }

        container.innerHTML = `
            <div style="
                max-width:700px;
                margin:0 auto;
            ">

                <button
                    onclick="openStudentModule(${courseId}, ${moduleId})"
                    style="
                        border:none;
                        background:#eef2f7;
                        padding:9px 14px;
                        border-radius:10px;
                        cursor:pointer;
                        margin-bottom:18px;
                    "
                >
                    ← Darsga qaytish
                </button>

                <div style="
                    background:linear-gradient(145deg,#111827,#0b1220);
                    border:1px solid rgba(52,211,153,.25);
                    border-radius:22px;
                    padding:24px;
                    box-shadow:0 20px 50px rgba(0,0,0,.35);
                ">

                    <div style="
                        font-size:13px;
                        color:#34d399;
                        font-weight:700;
                        margin-bottom:8px;
                    ">
                        📝 DARS TEKSHIRUVI
                    </div>

                    <h2 style="
                        margin:0 0 20px;
                        color:#f8fafc;
                    ">
                        Bilimingizni tekshiring
                    </h2>

                    <form id="lessonQuizForm">

                        ${quizzes.map((quiz, index) => `
                            <div style="
                                margin-bottom:24px;
                                padding-bottom:20px;
                                border-bottom:1px solid #eef1f5;
                            ">

                                <div style="
                                    font-weight:700;
                                    color:#f1f5f9;
                                    margin-bottom:12px;
                                    line-height:1.5;
                                ">
                                    ${index + 1}. ${quiz.question}
                                </div>

                                ${[
                                    ["A", quiz.option_a],
                                    ["B", quiz.option_b],
                                    ["C", quiz.option_c],
                                    ["D", quiz.option_d]
                                ].map(([letter, option]) => `
                                    <label style="
                                        display:flex;
                                        align-items:center;
                                        gap:10px;
                                        padding:12px;
                                        margin-bottom:8px;
                                        border:1px solid rgba(148,163,184,.25);
                                        border-radius:14px;
                                        cursor:pointer;
                                        background:rgba(255,255,255,.06);
                                        color:#f8fafc;
                                    ">
                                        <input
                                            type="radio"
                                            name="quiz_${quiz.id}"
                                            value="${letter}"
                                        >
                                        <span>${letter}) ${option}</span>
                                    </label>
                                `).join("")}

                            </div>
                        `).join("")}

                        <button
                            type="submit"
                            style="
                                width:100%;
                                border:none;
                                background:linear-gradient(135deg,#16a34a,#22c55e);
                                color:white;
                                padding:14px;
                                border-radius:12px;
                                font-size:16px;
                                font-weight:700;
                                cursor:pointer;
                            "
                        >
                            ✅ Javoblarni tekshirish
                        </button>

                    </form>

                    <div
                        id="quizResult"
                        style="
                            margin-top:15px;
                        "
                    ></div>

                </div>
            </div>
        `;

        document.getElementById("lessonQuizForm").addEventListener(
            "submit",
            async function(event) {

                event.preventDefault();

                const answers = {};

                quizzes.forEach(quiz => {

                    const selected = document.querySelector(
                        `input[name="quiz_${quiz.id}"]:checked`
                    );

                    if (selected) {
                        answers[quiz.id] = selected.value;
                    }

                });

                const resultBox =
                    document.getElementById("quizResult");

                resultBox.innerHTML = `
                    <div class="student-modern-checking-state">
                        <span class="student-modern-loading-icon student-loading-check"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v16H6z"/><path d="m9 12 2 2 4-4"/></svg></span>
                        <span>Tekshirilmoqda...</span>
                    </div>
                `;

                try {

                    const submitResponse = await fetch(
                        `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/quiz`,
                        {
                            method: "POST",
                            headers: {
                                "Authorization": `Bearer ${token}`,
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify(answers)
                        }
                    );

                    const result =
                        await submitResponse.json();

                    if (!submitResponse.ok) {
                        throw new Error(
                            result.detail ||
                            "Javoblarni tekshirishda xatolik"
                        );
                    }

                    if (result.passed) {

                        resultBox.innerHTML = `
                            <div style="
                                padding:18px;
                                background:#ecfdf5;
                                border:1px solid #86efac;
                                border-radius:12px;
                                color:#166534;
                                text-align:center;
                                font-weight:600;
                            ">
                                🎉 ${result.message}
                                <br>
                                <span style="
                                    display:block;
                                    margin-top:6px;
                                    font-size:14px;
                                ">
                                    Natija: ${result.score}/${result.total}
                                </span>
                            </div>

                            <button
    type="button"
    id="finishLessonButton"
    style="
        width:100%;
        margin-top:12px;
        border:none;
        background:#166534;
        color:white;
        padding:14px;
        border-radius:12px;
        font-weight:700;
        cursor:pointer;
        position:relative;
        z-index:9999;
    "
>
    ✅ Darsni tugatdim
</button>
                        `;
const finishButton =
    document.getElementById("finishLessonButton");

if (finishButton) {
    finishButton.addEventListener("click", function () {

        console.log("Darsni tugatdim bosildi");

        completeStudentLesson(
            courseId,
            moduleId,
            lessonId,
            this
        );

    });
}

                    } else {

                        resultBox.innerHTML = `
                            <div style="
                                padding:18px;
                                background:#fef2f2;
                                border:1px solid #fecaca;
                                border-radius:12px;
                                color:#991b1b;
                                text-align:center;
                                font-weight:600;
                            ">
                                ❌ ${result.message}
                                <br>
                                <span style="
                                    display:block;
                                    margin-top:6px;
                                    font-size:14px;
                                ">
                                    Natija: ${result.score}/${result.total}
                                </span>
                            </div>
                        `;
                    }

                } catch (error) {

                    console.error(error);

                    resultBox.innerHTML = `
                        <div style="
                            padding:15px;
                            background:#fef2f2;
                            border-radius:10px;
                            color:#dc2626;
                        ">
                            ❌ ${error.message}
                        </div>
                    `;
                }
            }
        );

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:30px;
                color:#dc2626;
            ">
                ❌ ${error.message}
            </div>
        `;
    }
}
    
        async function completeStudentLesson(courseId, moduleId, lessonId, button) {
        let currentCourseId = courseId;
        let currentModuleId = moduleId;

        const token = localStorage.getItem("access_token");

        if (!token) {
            window.location.href = "index.html";
            return;
        }

        try {

            const response = await fetch(
                `${API_URL}/students/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/complete`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );

            const result = await response.json();

            if (!response.ok) {

                showLessonErrorModal(
                    result.detail || "Darsni yakunlashda xatolik"
                );

                return;
            }

            showLessonSuccessModal(result.progress);

           if (button) {

    button.textContent = "✅ Tugallandi";

    button.disabled = true;

    button.style.background = "#166534";

    button.style.cursor = "default";
}
        } catch (error) {

            console.error(error);

            showLessonErrorModal(
                "Server bilan bog‘lanishda xatolik."
            );
        }
    }

        function showLessonErrorModal(message) {

        const modal =
            document.getElementById("lessonErrorModal");

        const text =
            document.getElementById("lessonErrorText");

        if (!modal) return;

        if (text) {
            text.textContent =
                message || "Darsni yakunlashda xatolik";
        }

        modal.classList.add("show");

        modal.setAttribute(
            "aria-hidden",
            "false"
        );
    }


    function closeLessonErrorModal() {

        const modal =
            document.getElementById("lessonErrorModal");

        if (!modal) return;

        modal.classList.remove("show");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    function showLessonSuccessModal(progress) {

        const modal =
            document.getElementById("lessonSuccessModal");

        const percent =
            document.getElementById("lessonSuccessPercent");

        const fill =
            document.getElementById("lessonSuccessFill");

        if (!modal) return;

        if (percent) {
            percent.textContent =
                `${progress}%`;
        }

        if (fill) {
            fill.style.width =
                `${progress}%`;
        }

        modal.classList.add("show");

        modal.setAttribute(
            "aria-hidden",
            "false"
        );
    }


    function closeLessonSuccessModal() {

        const modal =
            document.getElementById("lessonSuccessModal");

        if (!modal) return;

        modal.classList.remove("show");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );
    }
    async function loadStudent() {

        const token = localStorage.getItem("access_token");

        if (!token) {

            window.location.href = "index.html";

            return;
        }


        try {

            const response = await fetch(
                `${API_URL}/students/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );


            if (response.status === 401) {

                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");

                window.location.href = "index.html";

                return;
            }


            const data = await response.json();


            if (!response.ok) {

                showMessage(
                    data.detail || "Ma'lumotlarni olishda xatolik."
                );

                return;
            }


            const fullName = data.full_name || "O‘quvchi";


            document.getElementById(
                "welcomeName"
            ).textContent =
                `Xush kelibsiz, ${fullName}! 👋`;


            document.getElementById(
                "topStudentName"
            ).textContent = fullName;


            const firstLetter =
                fullName.charAt(0).toUpperCase();


            document.getElementById(
                "avatarLetter"
            ).textContent = firstLetter;


        } catch (error) {

            console.error(error);

            showMessage(
                "Server bilan bog‘lanishda xatolik."
            );

        }

    }


    /* =========================
       LOGOUT
    ========================= */

    function openLogoutModal() {

    const modal = document.getElementById("logoutModal");

    if (!modal) return;

    modal.classList.add("show");
    modal.setAttribute("aria-hidden", "false");

}


function closeLogoutModal() {

    const modal = document.getElementById("logoutModal");

    if (!modal) return;

    modal.classList.remove("show");
    modal.setAttribute("aria-hidden", "true");

}


function confirmLogoutStudent() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");

    window.location.href = "index.html";

}


    function openStudentSupport() {
        const modal = document.getElementById("studentSupportModal");
        if (!modal) return;
        modal.classList.add("show");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("support-modal-open");
    }

    function closeStudentSupport() {
        const modal = document.getElementById("studentSupportModal");
        if (!modal) return;
        modal.classList.remove("show");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("support-modal-open");
    }

    /* =========================
       MENU
    ========================= */

    function selectMenu(element) {

        document
            .querySelectorAll(".menu-item")
            .forEach(item => {
                item.classList.remove("active");
            });


        element.classList.add("active");

    }

    async function openStudentRankingMenu(element) {

    selectMenu(element);

    const container = document.getElementById("studentRanking");

    if (!container) {
        return;
    }

    container.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    await loadStudentRanking();
}

    async function openStudentRewardsMenu(element) {
        selectMenu(element);
        const container = document.getElementById("studentRewards");
        if (!container) return;
        container.scrollIntoView({behavior:"smooth", block:"center"});
        await loadStudentRewards();
    }

    async function loadStudentRewards() {
        const container = document.getElementById("studentRewardsContent");
        if (!container) return;

        const token = localStorage.getItem("access_token");
        if (!token) {
            container.innerHTML = '<div style="text-align:center;padding:30px;color:#ef4444;">Avval tizimga kiring.</div>';
            return;
        }

        container.innerHTML = '<div style="text-align:center;padding:25px;color:#7b8496;">Mukofotlar yuklanmoqda...</div>';

        try {
            const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(API_URL + "/students/rewards?ts=" + Date.now(), {
                method: "GET",
                cache: "no-store",
                headers: {"Authorization":"Bearer " + token},
                signal: controller.signal
            }).finally(() => clearTimeout(timeout));

            let data = {};
            try { data = await response.json(); } catch (_) {}

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                window.location.href = "index.html";
                return;
            }

            if (!response.ok) {
                throw new Error(data.detail || ("Server xatosi: " + response.status));
            }

            const student = data.student || {};
            const rewards = Array.isArray(data.rewards) ? data.rewards : [];

            let rewardHtml = rewards.map(function(reward) {
                return '<div style="position:relative;overflow:hidden;border:1px solid rgba(139,92,246,.28);border-radius:20px;padding:22px;margin-bottom:16px;background:linear-gradient(145deg,rgba(20,18,30,.96),rgba(10,10,15,.98));box-shadow:0 12px 35px rgba(0,0,0,.28);">' +
                    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">' +
                        '<div style="width:52px;height:52px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:25px;background:linear-gradient(135deg,#8B5CF6,#6D28D9);">🎁</div>' +
                        '<h3 style="margin:0;color:#fff;font-size:18px;">' + escapeHtml(reward.name || "Mukofot") + '</h3>' +
                    '</div>' +
                    '<p style="color:#aaa5b8;margin:0 0 18px;line-height:1.6;font-size:14px;">' + escapeHtml(reward.description || "Mukofot tavsifi mavjud emas") + '</p>' +
                    '<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:15px;flex-wrap:wrap;">' +
                        '<div><div style="color:#817c8f;font-size:12px;margin-bottom:5px;">Mukofot narxi</div>' +
                        '<div style="color:#c4b5fd;font-size:16px;font-weight:800;">🪙 ' + Number(reward.coin_price || 0) + ' Coin</div>' +
                        (Number(reward.crystal_price || 0) > 0 ? '<div style="color:#c4b5fd;font-size:16px;font-weight:800;margin-top:7px;">💎 ' + Number(reward.crystal_price) + ' Crystal</div>' : '') +
                        '</div>' +
                        '<button onclick="buyStudentReward(' + Number(reward.id) + ')" style="border:none;border-radius:13px;padding:12px 20px;background:linear-gradient(135deg,#8B5CF6,#6D28D9);color:#fff;font-weight:800;cursor:pointer;">Sotib olish</button>' +
                    '</div>' +
                    '<div style="margin-top:16px;color:#777285;font-size:12px;">Mavjud: ' + Number(reward.stock || 0) + ' dona</div>' +
                '</div>';
            }).join("");

            if (!rewardHtml) {
                rewardHtml = '<div style="text-align:center;padding:35px;color:#7b8496;"><div style="font-size:42px;margin-bottom:10px;">🎁</div><strong style="display:block;color:#fff;margin-bottom:7px;">Hozircha mukofot mavjud emas</strong><span>Administrator mukofot qo‘shganda shu yerda ko‘rinadi.</span></div>';
            }

            container.innerHTML =
                '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:20px;">' +
                    '<div style="padding:16px;border-radius:16px;background:rgba(52,211,153,.10);"><div>🪙</div><div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' + Number(student.coins || 0) + '</div><div style="color:#9ca3af;font-size:12px;">Coin</div></div>' +
                    '<div style="padding:16px;border-radius:16px;background:rgba(168,85,247,.10);"><div>💎</div><div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' + Number(student.crystals || 0) + '</div><div style="color:#9ca3af;font-size:12px;">Crystal</div></div>' +
                    '<div style="padding:16px;border-radius:16px;background:rgba(59,130,246,.10);"><div>⭐</div><div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' + Number(student.xp || 0) + '</div><div style="color:#9ca3af;font-size:12px;">XP · Level ' + Number(student.level || 1) + '</div></div>' +
                '</div><h3 style="color:#fff;margin:0 0 14px;font-size:17px;">🎁 Mavjud mukofotlar</h3>' + rewardHtml;
        } catch (error) {
            console.error("Rewards load error:", error);
            container.innerHTML = '<div style="text-align:center;padding:30px;color:#ef4444;">' +
                '<strong>Mukofotlarni yuklashda xatolik yuz berdi.</strong><br><span style="display:block;margin-top:8px;color:#9ca3af;">' +
                escapeHtml(error.message || "Noma’lum xatolik") + '</span></div>';
        }
    }

    async function buyStudentReward(productId) {

const token = localStorage.getItem("access_token");

if (!token) {
    showPremiumModal(
        "Tizimga kirish kerak",
        "Mukofot sotib olish uchun avval tizimga kiring.",
        "Kirish"
    );
    return;
}

showPremiumModal(
    "Mukofotni sotib olish",
    "Bu mukofotni Coin va Crystal orqali sotib olishni tasdiqlaysizmi?",
    "Sotib olish",
    async () => {

        try {

            const response = await fetch(
                `${API_URL}/students/rewards/${productId}/buy`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Mukofotni sotib olishda xatolik"
                );
            }

            showPremiumModal(
                "Xarid muvaffaqiyatli!",
                `🎉 ${data.message}<br><br>` +
                `Buyurtma №${data.order_id}<br>` +
                `🪙 Coin: ${data.student.coins}<br>` +
                `💎 Crystal: ${data.student.crystals}`,
                "Ajoyib!"
            );

            await loadStudentRewards();

        } catch (error) {

            console.error(error);

            showPremiumModal(
                "Xatolik yuz berdi",
                error.message,
                "Yopish"
            );
        }
    }
);

}


    async function loadStudentRanking() {

    const container = document.getElementById("studentRankingList");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:25px;
            color:#7b8496;
        ">
            Reyting yuklanmoqda...
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/students/ranking`
        );

        if (!response.ok) {
            throw new Error("Reytingni yuklab bo'lmadi");
        }

        const ranking = await response.json();

        if (!ranking || ranking.length === 0) {
            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:30px;
                    color:#7b8496;
                ">
                    Hozircha reytingda o‘quvchilar yo‘q.
                </div>
            `;
            return;
        }

        container.innerHTML = ranking.map(student => `

            <div style="
                display:flex;
                align-items:center;
                gap:14px;
                padding:16px;
                margin-bottom:10px;
                background:linear-gradient(
                    145deg,
                    #111827,
                    #0b1220
                );
                border:1px solid rgba(52,211,153,.18);
                border-radius:16px;
            ">

                <div style="
                    min-width:42px;
                    height:42px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border-radius:12px;
                    background:rgba(52,211,153,.12);
                    color:#34d399;
                    font-weight:800;
                    font-size:17px;
                ">
                    ${student.rank}
                </div>

                <div style="flex:1;">

                    <div style="
                        color:#fff;
                        font-weight:700;
                        font-size:15px;
                    ">
                        ${student.full_name}
                    </div>

                    <div style="
                        margin-top:5px;
                        color:#9ca3af;
                        font-size:13px;
                    ">
                        Level ${student.level}
                        · ${student.xp} XP
                        · 🪙 ${student.coins}
                    </div>

                </div>

                <div style="
                    color:#34d399;
                    font-weight:800;
                    font-size:14px;
                ">
                    #${student.rank}
                </div>

            </div>

        `).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:30px;
                color:#ef4444;
            ">
                Reytingni yuklashda xatolik yuz berdi.
            </div>
        `;
    }
}

    async function openStudentCoursesMenu(element) {

    selectMenu(element);

    const container = document.getElementById("studentCourses");

    if (!container) {
        return;
    }

    await loadStudentCourses();

    container.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

    async function openStudentHomeworkMenu(element) {

    selectMenu(element);

    
    const container = document.getElementById("studentHomeworkList");
    if (!container) {
        return;
    }

    container.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    await loadStudentHomework();
}

    async function loadStudentHomework() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const container =
        document.getElementById("studentHomeworkResults");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:35px 20px;
            color:#94a3b8;
        ">
            <div style="font-size:35px;">📝</div>
            <div style="
                margin-top:10px;
                font-weight:700;
                color:#f8fafc;
            ">
                Uy vazifalari yuklanmoqda...
            </div>
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/homework/student`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const homeworks = await response.json();

        if (!response.ok) {
            throw new Error(
                homeworks.detail ||
                "Uy vazifalarini yuklashda xatolik"
            );
        }

        if (!homeworks.length) {

            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:40px 20px;
                    color:#94a3b8;
                ">
                    <div class="student-modern-empty-icon" style="margin-bottom:14px;">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v16H6z"/><path d="m9 12 2 2 4-4"/></svg>
                    </div>

                    <div style="
                        color:#f8fafc;
                        font-size:17px;
                        font-weight:800;
                    ">
                        Hozircha uy vazifasi yo‘q
                    </div>

                    <div style="
                        margin-top:7px;
                        font-size:13px;
                    ">
                        Yangi vazifalar shu yerda ko‘rinadi.
                    </div>

                </div>
            `;

            return;
        }

        const submissionsResponse = await fetch(
            `${API_URL}/homework/student/submissions`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const submissions =
            await submissionsResponse.json();

        container.innerHTML = homeworks.map(homework => {

            const submission =
                submissions.find(
                    item => item.homework_id === homework.id
                );

            const submitted =
                submission &&
                submission.status === "submitted";

            const checked =
                submission &&
                submission.status === "checked";

            return `
                <div style="
                    background:
                        linear-gradient(
                            145deg,
                            #111827,
                            #0b1220
                        );
                    border:1px solid #263244;
                    border-radius:18px;
                    padding:20px;
                    margin-bottom:14px;
                    box-shadow:
                        0 10px 30px rgba(0,0,0,.25);
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:flex-start;
                        gap:12px;
                    ">

                        <div>
                            <div style="
                                color:#4ade80;
                                font-size:11px;
                                font-weight:800;
                                letter-spacing:1px;
                            ">
                                📝 UY VAZIFASI
                            </div>

                            <div style="
                                margin-top:7px;
                                color:#f8fafc;
                                font-size:17px;
                                font-weight:800;
                            ">
                                ${homework.title}
                            </div>
                        </div>

                        <span style="
                            padding:6px 10px;
                            border-radius:20px;
                            background:${
                                checked
                                ? "rgba(34,197,94,.12)"
                                : submitted
                                ? "rgba(250,204,21,.12)"
                                : "rgba(59,130,246,.12)"
                            };
                            color:${
                                checked
                                ? "#4ade80"
                                : submitted
                                ? "#facc15"
                                : "#60a5fa"
                            };
                            font-size:11px;
                            font-weight:800;
                            white-space:nowrap;
                        ">
                            ${
                                checked
                                ? "✅ Tekshirildi"
                                : submitted
                                ? "⏳ Tekshirilmoqda"
                                : "🆕 Yangi"
                            }
                        </span>

                    </div>

                    <div style="
                        margin-top:15px;
                        color:#94a3b8;
                        font-size:13px;
                        line-height:1.6;
                    ">
                        ${homework.description || "Izoh mavjud emas."}
                    </div>

                    ${
                        homework.deadline
                        ? `
                            <div style="
                                margin-top:12px;
                                color:#64748b;
                                font-size:12px;
                            ">
                                ⏰ Muddat: ${homework.deadline}
                            </div>
                        `
                        : ""
                    }

                    ${
                        checked
                        ? `
                            <div style="
                                margin-top:15px;
                                padding:14px;
                                background:rgba(34,197,94,.07);
                                border:1px solid rgba(34,197,94,.15);
                                border-radius:12px;
                            ">
                                <div style="
                                    color:#64748b;
                                    font-size:11px;
                                ">
                                    Sizning bahoyingiz
                                </div>

                                <strong style="
                                    display:block;
                                    margin-top:4px;
                                    color:#4ade80;
                                    font-size:25px;
                                ">
                                    ${submission.score ?? 0}/100
                                </strong>

                                ${
                                    submission.teacher_comment
                                    ? `
                                        <div style="
                                            margin-top:8px;
                                            color:#cbd5e1;
                                            font-size:13px;
                                        ">
                                            💬 ${submission.teacher_comment}
                                        </div>
                                    `
                                    : ""
                                }
                            </div>
                        `
                        : `
                            <div style="
                                margin-top:16px;
                            ">

                                <textarea
                                    id="homeworkAnswer_${homework.id}"
                                    placeholder="Javobingizni shu yerga yozing..."
                                    style="
                                        width:100%;
                                        min-height:110px;
                                        padding:13px;
                                        border-radius:12px;
                                        resize:vertical;
                                    "
                                >${
                                    submission?.answer || ""
                                }</textarea>

                                <button
                                    onclick="submitStudentHomework(${homework.id})"
                                    style="
                                        width:100%;
                                        margin-top:10px;
                                        border:none;
                                        padding:13px;
                                        border-radius:12px;
                                        background:
                                            linear-gradient(
                                                135deg,
                                                #22c55e,
                                                #15803d
                                            );
                                        color:white;
                                        font-weight:800;
                                        cursor:pointer;
                                    "
                                >
                                    ${
                                        submitted
                                        ? "🔄 Javobni qayta topshirish"
                                        : "🚀 Javobni topshirish"
                                    }
                                </button>

                            </div>
                        `
                    }

                </div>
            `;

        }).join("");

    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                padding:20px;
                background:rgba(239,68,68,.08);
                border:1px solid rgba(239,68,68,.2);
                border-radius:14px;
                color:#f87171;
            ">
                ❌ ${error.message}
            </div>
        `;
    }
}

    async function submitStudentHomework(homeworkId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const textarea =
        document.getElementById(
            `homeworkAnswer_${homeworkId}`
        );

    if (!textarea) {
        return;
    }

    const answer = textarea.value.trim();

    if (!answer) {
        showPremiumModal(
            "Javob kerak",
            "Avval uy vazifasiga javob yozing.",
            "Tushundim"
        );
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/homework/${homeworkId}/submit?answer=${encodeURIComponent(answer)}`,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail ||
                "Uy vazifasini topshirishda xatolik"
            );
        }

        showPremiumModal(
            "Vazifa topshirildi",
            "✅ Uy vazifasi muvaffaqiyatli topshirildi.",
            "Ajoyib!"
        );

        await loadStudentHomework();
        await loadStudentHomeworkResults();

    } catch (error) {

        console.error(error);

        showPremiumModal(
            "Xatolik yuz berdi",
            "❌ " + escapeHtml(error.message || "Uy vazifasini topshirishda xatolik"),
            "Yopish"
        );
    }
}

    /* =========================
       STUDENT HOME QUICK ACTIONS
    ========================= */

    function getStudentMenuButton(id) {
        return document.getElementById(id);
    }

    function openStudentCoursesFromHome() {
        const button = getStudentMenuButton("studentCoursesMenu");
        if (button) {
            openStudentCoursesMenu(button);
        }
    }

    function openStudentHomeworkFromHome() {
        const button = getStudentMenuButton("studentHomeworkMenu");
        if (button) {
            openStudentHomeworkMenu(button);
        }
    }

    function openStudentRankingFromHome() {
        const button = getStudentMenuButton("studentRankingMenu");
        if (button) {
            openStudentRankingMenu(button);
        }
    }

    function openStudentRewardsFromHome() {
        const button = getStudentMenuButton("studentRewardsMenu");
        if (button) {
            openStudentRewardsMenu(button);
        }
    }

    function openStudentBooksFromHome() {
        const button = getStudentMenuButton("studentBooksMenu");
        if (button) {
            openStudentBooksMenu(button);
        }
    }

    function closeStudentFeatureModal() {
        const modal = document.getElementById("studentFeatureModal");
        if (modal) {
            modal.remove();
        }
    }

    function openStudentFeatureModal(title, icon, content) {
        closeStudentFeatureModal();

        const modal = document.createElement("div");
        modal.id = "studentFeatureModal";

        modal.innerHTML =
            '<div style="position:fixed;inset:0;z-index:99998;background:rgba(0,0,0,.78);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;padding:20px;">' +
                '<div style="position:relative;width:min(560px,100%);max-height:85vh;overflow:auto;background:linear-gradient(145deg,#111827,#080d16);border:1px solid rgba(52,211,153,.22);border-radius:24px;padding:26px;box-shadow:0 30px 90px rgba(0,0,0,.65);color:#f8fafc;">' +
                    '<button type="button" onclick="closeStudentFeatureModal()" aria-label="Yopish" style="position:absolute;top:14px;right:14px;width:36px;height:36px;border:1px solid rgba(255,255,255,.10);border-radius:11px;background:rgba(255,255,255,.05);color:#cbd5e1;font-size:18px;cursor:pointer;">×</button>' +
                    '<div style="width:58px;height:58px;border-radius:17px;display:flex;align-items:center;justify-content:center;font-size:28px;background:linear-gradient(135deg,#064e3b,#22c55e);box-shadow:0 10px 28px rgba(34,197,94,.18);margin-bottom:17px;">' +
                        icon +
                    '</div>' +
                    '<h2 style="margin:0 45px 10px 0;color:#fff;font-size:22px;">' +
                        escapeHtml(title) +
                    '</h2>' +
                    '<div style="color:#94a3b8;font-size:14px;line-height:1.7;">' +
                        content +
                    '</div>' +
                '</div>' +
            '</div>';

        modal.firstElementChild.addEventListener("click", function(event) {
            if (event.target === this) {
                closeStudentFeatureModal();
            }
        });

        document.body.appendChild(modal);
    }

    function openStudentProfile() {
        const token = localStorage.getItem("access_token");

        if (!token) {
            window.location.href = "index.html";
            return;
        }

        const old = document.getElementById("studentProfileModal");
        if (old) old.remove();

        const modal = document.createElement("div");
        modal.id = "studentProfileModal";
        modal.style.cssText = "position:fixed;inset:0;z-index:999999;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;";

        modal.innerHTML =
            '<div style="width:min(520px,100%);max-height:88vh;overflow:auto;background:linear-gradient(145deg,#111827,#070b12);border:1px solid rgba(52,211,153,.28);border-radius:24px;padding:24px;box-sizing:border-box;color:#fff;box-shadow:0 30px 90px rgba(0,0,0,.7);">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">' +
                    '<div><div style="font-size:11px;color:#34d399;font-weight:800;letter-spacing:.12em;">SHAXSIY KABINET</div><h2 style="margin:5px 0 0;font-size:23px;">Profilim</h2></div>' +
                    '<button type="button" id="studentProfileClose" style="width:38px;height:38px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:rgba(255,255,255,.05);color:#fff;font-size:22px;cursor:pointer;">×</button>' +
                '</div>' +
                '<div id="studentProfileBody" style="color:#cbd5e1;">' +
                    '<div style="padding:28px 10px;text-align:center;">⏳<div style="margin-top:10px;">Ma’lumotlar yuklanmoqda...</div></div>' +
                '</div>' +
            '</div>';

        document.body.appendChild(modal);

        document.getElementById("studentProfileClose").onclick = function() {
            modal.remove();
        };

        modal.onclick = function(event) {
            if (event.target === modal) modal.remove();
        };

        const body = document.getElementById("studentProfileBody");

        fetch(API_URL + "/students/me", {
            method: "GET",
            headers: { "Authorization": "Bearer " + token }
        })
        .then(async function(response) {
            let data = {};
            try { data = await response.json(); } catch (_) {}

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                window.location.href = "index.html";
                return;
            }

            if (!response.ok) {
                throw new Error(data.detail || "Profil ma’lumotlarini yuklashda xatolik");
            }

            const birthKey = "student_birth_date_" + data.id;
            const savedBirthDate = localStorage.getItem(birthKey) || "";

            body.innerHTML =
                '<div style="display:grid;gap:12px;">' +
                    '<div style="padding:16px;border:1px solid rgba(52,211,153,.14);border-radius:17px;background:rgba(52,211,153,.06);">' +
                        '<div style="font-size:11px;color:#94a3b8;font-weight:800;">ISM VA FAMILIYA</div>' +
                        '<div id="profileFullName" style="margin-top:6px;font-size:16px;font-weight:800;color:#fff;"></div>' +
                    '</div>' +
                    '<div style="padding:16px;border:1px solid rgba(52,211,153,.14);border-radius:17px;background:rgba(52,211,153,.06);">' +
                        '<div style="font-size:11px;color:#94a3b8;font-weight:800;">RO‘YXATDAN O‘TGAN TELEFON RAQAMI</div>' +
                        '<div id="profilePhone" style="margin-top:6px;font-size:16px;font-weight:800;color:#fff;"></div>' +
                    '</div>' +
                    '<div style="padding:16px;border:1px solid rgba(52,211,153,.14);border-radius:17px;background:rgba(52,211,153,.06);">' +
                        '<div style="font-size:11px;color:#94a3b8;font-weight:800;">PROFIL HOLATI</div>' +
                        '<div id="profileStatus" style="margin-top:6px;font-size:16px;font-weight:800;"></div>' +
                    '</div>' +
                    '<div style="padding:18px;border:1px solid rgba(139,92,246,.30);border-radius:19px;background:linear-gradient(145deg,rgba(139,92,246,.10),rgba(52,211,153,.05));">' +
                        '<div style="font-size:11px;color:#c4b5fd;font-weight:800;">TUG‘ILGAN KUNINGIZ</div>' +
                        '<div style="margin-top:5px;color:#94a3b8;font-size:12px;">Tug‘ilgan sanangizni kiriting</div>' +
                        '<input id="studentBirthDate" type="date" value="' + savedBirthDate + '" style="width:100%;height:46px;margin-top:13px;padding:0 12px;box-sizing:border-box;border-radius:12px;border:1px solid rgba(167,139,250,.25);background:#090e16;color:#fff;color-scheme:dark;">' +
                        '<button id="studentBirthDateSave" type="button" style="width:100%;height:44px;margin-top:10px;border:0;border-radius:12px;background:linear-gradient(135deg,#059669,#15803d);color:#fff;font-weight:800;cursor:pointer;">Saqlash</button>' +
                        '<div id="studentBirthDateMessage" style="min-height:17px;margin-top:8px;font-size:12px;"></div>' +
                    '</div>' +
                '</div>';

            document.getElementById("profileFullName").textContent = data.full_name || "O‘quvchi";
            document.getElementById("profilePhone").textContent = data.phone || "—";

            const status = document.getElementById("profileStatus");
            status.textContent = data.is_active ? "● Faol" : "● Faol emas";
            status.style.color = data.is_active ? "#4ade80" : "#f87171";

            document.getElementById("studentBirthDateSave").onclick = function() {
                const input = document.getElementById("studentBirthDate");
                const message = document.getElementById("studentBirthDateMessage");

                if (!input.value) {
                    message.textContent = "Iltimos, tug‘ilgan sanangizni kiriting.";
                    message.style.color = "#f87171";
                    return;
                }

                localStorage.setItem(birthKey, input.value);
                message.textContent = "Tug‘ilgan sana saqlandi ✓";
                message.style.color = "#4ade80";
            };
        })
        .catch(function(error) {
            body.innerHTML = '<div style="padding:18px;border:1px solid rgba(248,113,113,.2);border-radius:15px;color:#f87171;background:rgba(248,113,113,.06);">❌ ' + (error.message || "Profilni yuklashda xatolik") + '</div>';
        });
    }

    window.openStudentProfile = openStudentProfile;

    function saveStudentBirthDate(studentId) {
        const input = document.getElementById("studentBirthDate");
        const message = document.getElementById("studentBirthDateMessage");

        if (!input || !message) return;

        if (!input.value) {
            message.textContent = "Iltimos, tug‘ilgan sanangizni kiriting.";
            message.className = "student-profile-message error";
            return;
        }

        localStorage.setItem(
            "student_birth_date_" + studentId,
            input.value
        );

        message.textContent = "Tug‘ilgan sana saqlandi ✓";
        message.className = "student-profile-message success";
    }

    async function loadStudentPodcasts() {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        try {
            const response = await fetch(API_URL + "/students/podcasts", {headers:{"Authorization":"Bearer "+token}});
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Podcastlarni yuklab bo‘lmadi");
            const content = data.length ? data.map(function(item){
                return '<div style="padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.04);margin-top:12px;"><strong style="color:#fff;">🎧 '+escapeHtml(item.title)+'</strong><p style="margin:7px 0;color:#94a3b8;">'+escapeHtml(item.description||"")+'</p>'+(item.audio_url?'<audio controls style="width:100%;margin-top:8px;" src="'+escapeHtml(item.audio_url)+'"></audio>':'<small>Audio fayl hali qo‘shilmagan.</small>')+'</div>';
            }).join("") : '<div style="padding:25px;text-align:center;">Hozircha podcast mavjud emas.</div>';
            openStudentFeatureModal("Podcastlar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M5 13a7 7 0 0 1 14 0\"/><path d=\"M5 13v4a2 2 0 0 0 2 2h1v-7H7a2 2 0 0 0-2 1ZM19 13v4a2 2 0 0 1-2 2h-1v-7h1a2 2 0 0 1 2 1ZM12 19v2\"/></svg>",content);
        } catch(e){ openStudentFeatureModal("Podcastlar","⚠️",'<span style="color:#f87171;">'+escapeHtml(e.message)+'</span>'); }
    }

    function openStudentPodcasts() {
        selectMenu(getStudentMenuButton("studentPodcastsMenu"));
        openStudentFeatureModal("Podcastlar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M5 13a7 7 0 0 1 14 0\"/><path d=\"M5 13v4a2 2 0 0 0 2 2h1v-7H7a2 2 0 0 0-2 1ZM19 13v4a2 2 0 0 1-2 2h-1v-7h1a2 2 0 0 1 2 1ZM12 19v2\"/></svg>",'<div>Podcastlar yuklanmoqda...</div>');
        loadStudentPodcasts();
    }

    async function loadStudentTrainings() {
        const token=localStorage.getItem("access_token");
        if(!token) return;
        try {
            const response=await fetch(API_URL+"/students/trainings",{headers:{"Authorization":"Bearer "+token}});
            const data=await response.json();
            if(!response.ok) throw new Error(data.detail||"Treninglarni yuklab bo‘lmadi");
            const content=data.length?data.map(function(item){
                const button=item.registered?'<button disabled style="border:0;border-radius:10px;padding:10px 14px;background:#14532d;color:#86efac;font-weight:800;">✓ Ro‘yxatdan o‘tilgan</button>':'<button onclick="registerStudentTraining('+Number(item.id)+')" style="border:0;border-radius:10px;padding:10px 14px;background:#22c55e;color:#052e16;font-weight:800;">Ro‘yxatdan o‘tish</button>';
                return '<div style="padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.04);margin-top:12px;"><strong style="color:#fff;">🎓 '+escapeHtml(item.title)+'</strong><p style="color:#94a3b8;">'+escapeHtml(item.description||"")+'</p><div style="color:#cbd5e1;font-size:13px;">📅 '+escapeHtml(String(item.start_at||""))+(item.location?"<br>📍 "+escapeHtml(item.location):"")+'</div><div style="margin-top:12px;">'+button+'</div></div>';
            }).join(""):'<div style="padding:25px;text-align:center;">Hozircha trening mavjud emas.</div>';
            openStudentFeatureModal("Treninglar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M4 7.5 12 4l8 3.5L12 11 4 7.5Z\"/><path d=\"M6.5 9v5.2c0 1.8 2.5 3.3 5.5 3.3s5.5-1.5 5.5-3.3V9\"/><path d=\"M20 8v6\"/></svg>",content);
        } catch(e){openStudentFeatureModal("Treninglar","⚠️",'<span style="color:#f87171;">'+escapeHtml(e.message)+'</span>');}
    }
    function openStudentTrainings() {
        selectMenu(getStudentMenuButton("studentTrainingsMenu"));
        openStudentFeatureModal("Treninglar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M4 7.5 12 4l8 3.5L12 11 4 7.5Z\"/><path d=\"M6.5 9v5.2c0 1.8 2.5 3.3 5.5 3.3s5.5-1.5 5.5-3.3V9\"/><path d=\"M20 8v6\"/></svg>",'<div>Treninglar yuklanmoqda...</div>');
        loadStudentTrainings();
    }
    async function registerStudentTraining(id) {
        const token=localStorage.getItem("access_token");
        try {
            const r=await fetch(API_URL+"/students/trainings/"+Number(id)+"/register",{method:"POST",headers:{"Authorization":"Bearer "+token}});
            const d=await r.json();
            if(!r.ok) throw new Error(d.detail||"Ro‘yxatdan o‘tishda xatolik");
            showPremiumModal("Treningga ro‘yxatdan o‘tildi","🎓 "+d.message,"Ajoyib!");
            await loadStudentTrainings();
        } catch(e){showPremiumModal("Xatolik yuz berdi",escapeHtml(e.message),"Yopish");}
    }

    async function loadStudentExams() {
        const token=localStorage.getItem("access_token");
        if(!token) return;
        try {
            const response=await fetch(API_URL+"/students/exams",{headers:{"Authorization":"Bearer "+token}});
            const data=await response.json();
            if(!response.ok) throw new Error(data.detail||"Imtihonlarni yuklab bo‘lmadi");
            const content=data.length?data.map(function(item){
                const button=item.registered?'<button disabled style="border:0;border-radius:10px;padding:10px 14px;background:#14532d;color:#86efac;font-weight:800;">✓ Ro‘yxatdan o‘tilgan</button>':'<button onclick="registerStudentExam('+Number(item.id)+')" style="border:0;border-radius:10px;padding:10px 14px;background:#22c55e;color:#052e16;font-weight:800;">Imtihonga yozilish</button>';
                return '<div style="padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.04);margin-top:12px;"><strong style="color:#fff;">🧪 '+escapeHtml(item.title)+'</strong><p style="color:#94a3b8;">'+escapeHtml(item.description||"")+'</p><div style="color:#cbd5e1;font-size:13px;">📅 '+escapeHtml(String(item.start_at||""))+(item.location?"<br>📍 "+escapeHtml(item.location):"")+'</div><div style="margin-top:12px;">'+button+'</div></div>';
            }).join(""):'<div style="padding:25px;text-align:center;">Hozircha imtihon mavjud emas.</div>';
            openStudentFeatureModal("Imtihonlar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M9 3h6M10 3v5l-5 9a3 3 0 0 0 3 4h8a3 3 0 0 0 3-4l-5-9V3\"/><path d=\"M8 15h8\"/></svg>",content);
        } catch(e){openStudentFeatureModal("Imtihonlar","⚠️",'<span style="color:#f87171;">'+escapeHtml(e.message)+'</span>');}
    }
    function openStudentExams() {
        selectMenu(getStudentMenuButton("studentExamsMenu"));
        openStudentFeatureModal("Imtihonlar","<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M9 3h6M10 3v5l-5 9a3 3 0 0 0 3 4h8a3 3 0 0 0 3-4l-5-9V3\"/><path d=\"M8 15h8\"/></svg>",'<div>Imtihonlar yuklanmoqda...</div>');
        loadStudentExams();
    }
    async function registerStudentExam(id) {
        const token=localStorage.getItem("access_token");
        try {
            const r=await fetch(API_URL+"/students/exams/"+Number(id)+"/register",{method:"POST",headers:{"Authorization":"Bearer "+token}});
            const d=await r.json();
            if(!r.ok) throw new Error(d.detail||"Ro‘yxatdan o‘tishda xatolik");
            showPremiumModal("Imtihonga ro‘yxatdan o‘tildi","🧪 "+d.message,"Ajoyib!");
            await loadStudentExams();
        } catch(e){showPremiumModal("Xatolik yuz berdi",escapeHtml(e.message),"Yopish");}
    }

    async function loadStudentStats() {
        const token = localStorage.getItem("access_token");
        if (!token) {
            return;
        }

        const xpEl = document.getElementById("statTotalXp");
        const rankEl = document.getElementById("statRank");
        const homeworkEl = document.getElementById("statHomeworkDone");
        const streakEl = document.getElementById("statStreak");

        try {
            const meResponse = await fetch(
                API_URL + "/students/me",
                {
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                }
            );

            const me = await meResponse.json();

            if (meResponse.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                window.location.href = "index.html";
                return;
            }

            const results = await Promise.allSettled([
                fetch(API_URL + "/students/rewards", {
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                }).then(response => response.json()),
                fetch(API_URL + "/students/ranking").then(response => response.json()),
                fetch(API_URL + "/homework/student/submissions", {
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                }).then(response => response.json())
            ]);

            const rewardData =
                results[0].status === "fulfilled"
                    ? results[0].value
                    : null;

            const ranking =
                results[1].status === "fulfilled"
                    ? results[1].value
                    : [];

            const submissions =
                results[2].status === "fulfilled"
                    ? results[2].value
                    : [];

            if (xpEl && rewardData && rewardData.student) {
                xpEl.textContent =
                    Number(rewardData.student.xp || 0).toLocaleString();
            }

            if (streakEl && rewardData && rewardData.student) {
                streakEl.textContent =
                    Number(rewardData.student.streak_days || 0) + " kun";
            }

            let completedHomework = 0;

            if (homeworkEl && Array.isArray(submissions)) {
                completedHomework = submissions.filter(
                    item => item.status === "checked"
                ).length;

                homeworkEl.textContent = String(completedHomework);
            }

            if (rewardData && rewardData.student) {
                renderStudentActivity(
                    rewardData.student.streak_days,
                    rewardData.student.xp,
                    completedHomework
                );
            }

            if (rankEl && Array.isArray(ranking) && me && me.id) {
                const current = ranking.find(
                    item => Number(item.student_id) === Number(me.id)
                );

                rankEl.textContent =
                    current && current.rank
                        ? "#" + current.rank
                        : "—";
            }
        } catch (error) {
            console.error("Student stats error:", error);
        }
    }


    async function loadStudentDashboardTasks() {
        const token = localStorage.getItem("access_token");
        const container = document.getElementById("studentRecentTasks");

        if (!token || !container) {
            return;
        }

        try {
            const response = await fetch(
                API_URL + "/homework/student",
                {
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                }
            );

            const homeworks = await response.json();

            if (!response.ok) {
                throw new Error(homeworks.detail || "Vazifalarni yuklab bo‘lmadi");
            }

            if (!homeworks.length) {
                container.innerHTML =
                    '<div class="task" onclick="openStudentHomeworkFromHome()" style="cursor:pointer;">' +
                        '<div class="task-check student-homework-task-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h10a2 2 0 0 1 2 2v16H5V5a2 2 0 0 1 2-2Z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg></div>' +
                        '<div>' +
                            '<div class="task-name">Hozircha yangi vazifa yo‘q</div>' +
                            '<div class="task-date">Uy vazifalari bo‘limini ochish uchun bosing</div>' +
                        '</div>' +
                    '</div>';
                return;
            }

            const latest = homeworks.slice(0, 2);

            container.innerHTML = latest.map(function(homework) {
                return (
                    '<div class="task" onclick="openStudentHomeworkFromHome()" style="cursor:pointer;">' +
                        '<div class="task-check">📝</div>' +
                        '<div>' +
                            '<div class="task-name">' +
                                escapeHtml(homework.title || "Uy vazifasi") +
                            '</div>' +
                            '<div class="task-date">' +
                                (homework.deadline
                                    ? "⏰ " + escapeHtml(homework.deadline)
                                    : "Topshirish uchun bosing") +
                            '</div>' +
                        '</div>' +
                    '</div>'
                );
            }).join("");
        } catch (error) {
            console.error("Dashboard tasks error:", error);
            container.innerHTML =
                '<div class="task">' +
                    '<div class="task-check">⚠️</div>' +
                    '<div>' +
                        '<div class="task-name">Vazifalarni yuklab bo‘lmadi</div>' +
                        '<div class="task-date">Uy vazifalari bo‘limidan qayta urinib ko‘ring</div>' +
                    '</div>' +
                '</div>';
        }
    }

    function renderStudentActivity(streakDays, xp, completedHomework) {
        const container = document.getElementById("studentActivityContent");

        if (!container) {
            return;
        }

        const streak = Number(streakDays || 0);
        const totalXp = Number(xp || 0);
        const completed = Number(completedHomework || 0);

        container.innerHTML =
            '<div class="student-activity-grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));">' +

                '<div class="student-activity-card activity-streak">' +
                    '<div class="student-activity-icon">' +
                        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c2.5 3 5 4.5 5 8.5A5 5 0 1 1 7 9c0 2 1 3 2.7 4.1C9.3 9.8 11 7 12 3Z"/><path d="M10 18.5c.6.5 1.3.7 2 .7s1.4-.2 2-.7"/></svg>' +
                    '</div>' +
                    '<div class="student-activity-label">Faollik</div>' +
                    '<strong class="student-activity-value">' + streak + '<span>kun</span></strong>' +
                '</div>' +

                '<div class="student-activity-card activity-xp">' +
                    '<div class="student-activity-icon">' +
                        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.2 5.2 5.6.5-4.2 3.7 1.3 5.5-4.9-2.9-4.9 2.9 1.3-5.5-4.2-3.7L9.8 8.2 12 3Z"/><path d="M12 6v3"/></svg>' +
                    '</div>' +
                    '<div class="student-activity-label">Bilim tajribasi</div>' +
                    '<strong class="student-activity-value">' + totalXp.toLocaleString() + '<span>XP</span></strong>' +
                '</div>' +

                '<div class="student-activity-card activity-tasks">' +
                    '<div class="student-activity-icon">' +
                        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v16H6z"/><path d="m9 12 2 2 4-4"/><path d="M9 8h6"/></svg>' +
                    '</div>' +
                    '<div class="student-activity-label">Bajarilgan vazifalar</div>' +
                    '<strong class="student-activity-value">' + completed + '<span>ta</span></strong>' +
                '</div>' +

            '</div>' +
            '<div class="student-activity-note">O‘qishdagi faolligingiz, XP va bajarilgan vazifalar bir joyda.</div>';
    }

    /* =========================
       NOTIFICATIONS
    ========================= */

    let studentNotificationState = {
        ids: new Set(),
        firstLoad: true
    };

    async function showStudentSystemNotification(title, message) {
        if (!("Notification" in window) || Notification.permission !== "granted") return;
        try {
            const registration = await navigator.serviceWorker?.getRegistration();
            if (registration?.showNotification) {
                await registration.showNotification(title, {
                    body: message,
                    tag: "axsikent-student-notification"
                });
                return;
            }
        } catch (_) {}
        try {
            new Notification(title, {body: message});
        } catch (_) {}
    }

    async function loadStudentNotifications() {
        const token = localStorage.getItem("access_token");
        const badge = document.getElementById("studentNotificationBadge");
        if (!token) {
            if (badge) badge.hidden = true;
            return;
        }

        try {
            const response = await fetch(API_URL + "/students/notifications", {
                headers: {"Authorization": "Bearer " + token}
            });
            if (!response.ok) return;

            const data = await response.json();
            const items = Array.isArray(data.notifications) ? data.notifications : [];
            const unread = Number(data.unread || 0);

            if (badge) {
                badge.textContent = unread > 99 ? "99+" : String(unread);
                badge.hidden = unread <= 0;
            }

            if (studentNotificationState.firstLoad) {
                studentNotificationState.ids = new Set(items.map(item => item.id));
                studentNotificationState.firstLoad = false;
                return;
            }

            const fresh = items.filter(item => !studentNotificationState.ids.has(item.id));
            fresh.slice(0, 3).forEach(item => {
                showStudentSystemNotification(item.title || "Axsikent IT", item.message || "");
            });
            items.forEach(item => studentNotificationState.ids.add(item.id));
        } catch (error) {
            console.debug("Student notifications:", error);
        }
    }

    async function openStudentNotifications() {
        const token = localStorage.getItem("access_token");
        if (!token) {
            showPremiumStudentMessage("Avval Student kabinetiga kiring.");
            return;
        }

        if ("Notification" in window && Notification.permission === "default") {
            try { await Notification.requestPermission(); } catch (_) {}
        }
        try {
            if ("serviceWorker" in navigator) {
                await navigator.serviceWorker.register("sw.js");
            }
        } catch (_) {}

        try {
            const response = await fetch(API_URL + "/students/notifications", {
                headers: {"Authorization": "Bearer " + token}
            });
            const data = await response.json();
            const items = Array.isArray(data.notifications) ? data.notifications : [];

            const rows = items.length
                ? items.map(item =>
                    '<button type="button" class="student-notification-item ' + (item.is_read ? "read" : "unread") + '" data-notification-id="' + Number(item.id) + '">' +
                    '<span class="student-notification-icon">✦</span>' +
                    '<span><strong>' + escapeHtml(item.title || "Bildirishnoma") + '</strong><small>' + escapeHtml(item.message || "") + '</small><em>' + formatStudentContentDate(item.created_at) + '</em></span>' +
                    '</button>'
                ).join("")
                : '<div class="student-notification-empty"><span>✦</span><strong>Hozircha bildirishnoma yo‘q</strong><small>Yangi material yoki muhim xabar kelganda shu yerda chiqadi.</small></div>';

            showStudentNotificationModal(rows);

            document.querySelectorAll(".student-notification-item").forEach(item => {
                item.addEventListener("click", async () => {
                    const id = Number(item.dataset.notificationId);
                    if (!Number.isInteger(id)) return;
                    try {
                        await fetch(API_URL + "/students/notifications/" + id + "/read", {
                            method: "PUT",
                            headers: {"Authorization": "Bearer " + token}
                        });
                        item.classList.remove("unread");
                        item.classList.add("read");
                        await loadStudentNotifications();
                    } catch (_) {}
                });
            });
        } catch (error) {
            showPremiumStudentMessage(error.message || "Bildirishnomalarni yuklab bo‘lmadi.");
        }
    }

    // Make the notification action available to the HTML button.
    window.openStudentNotifications = openStudentNotifications;

    function showStudentNotificationModal(rows) {
        document.getElementById("studentNotificationModal")?.remove();
        const modal = document.createElement("div");
        modal.id = "studentNotificationModal";
        modal.className = "student-premium-overlay";
        modal.innerHTML =
            '<div class="student-premium-modal notification-modal">' +
            '<button type="button" class="student-premium-close" aria-label="Yopish">×</button>' +
            '<div class="student-premium-kicker">AXSIKENT IT / NOTIFICATIONS</div>' +
            '<h2>Bildirishnomalar</h2>' +
            '<div class="student-notification-list">' + rows + '</div>' +
            '</div>';
        document.body.appendChild(modal);
        modal.querySelector(".student-premium-close").addEventListener("click", () => modal.remove());
        modal.addEventListener("click", event => { if (event.target === modal) modal.remove(); });
    }

    function showPremiumStudentMessage(message) {
        document.getElementById("studentMessageModal")?.remove();
        const modal = document.createElement("div");
        modal.id = "studentMessageModal";        modal.className = "student-premium-overlay";
        modal.innerHTML =
            '<div class="student-premium-modal">' +
            '<button type="button" class="student-premium-close" aria-label="Yopish">×</button>' +
            '<div class="student-premium-kicker">AXSIKENT IT</div>' +
            '<h2>Xabar</h2><p>' + escapeHtml(message) + '</p>' +
            '</div>';
        document.body.appendChild(modal);
        modal.querySelector(".student-premium-close").addEventListener("click", () => modal.remove());
    }

    /* =========================
       MESSAGE
    ========================= */

    function showMessage(message) {
        showPremiumStudentMessage(message);
    }

    /* =========================
       START
    ========================= */
async function loadStudentHomeworkResults() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    const container =
        document.getElementById("studentHomeworkResults");

    if (!container) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/homework/student/submissions`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            container.innerHTML = `
                <div style="
                    padding:20px;
                    background:#fff1f2;
                    border-radius:14px;
                    color:#b91c1c;
                ">
                    ${data.detail || "Uy vazifalarini yuklab bo'lmadi."}
                </div>
            `;
            return;
        }

        if (!data.length) {
            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:25px;
                    color:#7b8496;
                ">
                    Hozircha topshirilgan uy vazifalari yo'q.
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(item => {

            const checked = item.status === "checked";

            return `
                <div style="
                    border:1px solid #e7ebf2;
                    border-radius:15px;
                    padding:18px;
                    margin-bottom:12px;
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        gap:10px;
                        margin-bottom:12px;
                    ">
                        <strong>
                            📝 Uy vazifasi #${item.homework_id}
                        </strong>

                        <span style="
                            padding:6px 10px;
                            border-radius:20px;
                            background:${checked ? "#dcfce7" : "#fef3c7"};
                            color:${checked ? "#166534" : "#92400e"};
                            font-size:12px;
                            font-weight:700;
                        ">
                            ${checked ? "✅ Tekshirildi" : "⏳ Tekshirilmoqda"}
                        </span>
                    </div>

                    <div style="
                        background:#f7f8fc;
                        border-radius:12px;
                        padding:14px;
                        margin-bottom:12px;
                    ">
                        <div style="
                            font-size:12px;
                            color:#7b8496;
                            margin-bottom:5px;
                        ">
                            Sizning javobingiz
                        </div>

                        <div>
                            ${item.answer || "Javob yo'q"}
                        </div>
                    </div>

                    ${
                        checked
                        ? `
                            <div style="
                                display:flex;
                                gap:12px;
                                flex-wrap:wrap;
                            ">

                                <div style="
                                    background:#eef4ff;
                                    border-radius:12px;
                                    padding:14px 20px;
                                ">
                                    <div style="
                                        font-size:11px;
                                        color:#7b8496;
                                    ">
                                        Baho
                                    </div>

                                    <strong style="
                                        font-size:25px;
                                        color:#2563eb;
                                    ">
                                        ${item.score ?? 0}/100
                                    </strong>
                                </div>

                                <div style="
                                    flex:1;
                                    min-width:200px;
                                    background:#f0fdf4;
                                    border-radius:12px;
                                    padding:14px;
                                ">
                                    <div style="
                                        font-size:11px;
                                        color:#166534;
                                        margin-bottom:5px;
                                    ">
                                        💬 Ustoz izohi
                                    </div>

                                    <div>
                                        ${item.teacher_comment || "Izoh qoldirilmagan."}
                                    </div>
                                </div>

                            </div>
                        `
                        : `
                            <div style="
                                padding:12px;
                                background:#fff7ed;
                                border-radius:12px;
                                color:#9a3412;
                                font-size:13px;
                            ">
                                ⏳ Ustoz hali bu vazifani tekshirmagan.
                            </div>
                        `
                    }

                </div>
            `;

        }).join("");

        } catch (error) {

        console.error(error);

        container.innerHTML = `
            <div style="
                padding:20px;
                background:#fff1f2;
                border-radius:14px;
                color:#b91c1c;
            ">
                Server bilan bog'lanishda xatolik.
            </div>
        `;
    }

} // loadStudentHomeworkResults() funksiyasi tugadi


/* =========================
   START STUDENT CABINET
========================= */

loadStudent();
loadStudentHomeworkResults();
loadStudentCourses();
loadStudentRanking();
loadStudentStats();
loadStudentDashboardTasks();
loadStudentRewards();
loadStudentBooks();
loadStudentNotifications();
setInterval(loadStudentNotifications, 15000);

    function openStudentBooksMenu(element) {
    selectMenu(element);

    const container = document.getElementById("studentBooks");

    if (!container) {
        return;
    }

    container.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    loadStudentBooks();
}


async function loadStudentBooks() {
    const container = document.getElementById("studentBooksContent");

    if (!container) {
        return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
        container.innerHTML = `
            <div style="
                text-align:center;
                padding:25px;
                color:#ff6b6b;
            ">
                Avval tizimga kiring.
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div style="
            text-align:center;
            padding:25px;
            color:#7b8496;
        ">
            Kitoblar yuklanmoqda...
        </div>
    `;

    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(
            `${API_URL}/students/books?ts=${Date.now()}`,
            {
                cache: "no-store",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                signal: controller.signal
            }
        ).finally(() => clearTimeout(timeout));

        if (!response.ok) {
            throw new Error("Kitoblarni yuklashda xatolik");
        }

        const data = await response.json();

        if (!data.books || data.books.length === 0) {
            container.innerHTML = `
                <div style="
                    text-align:center;
                    padding:30px;
                    color:#7b8496;
                ">
                    Hozircha kitoblar mavjud emas.
                </div>
            `;
            return;
        }

    container.innerHTML = data.books.map(book => ` <div style="
        position:relative;
        overflow:hidden;
        border:1px solid rgba(139,92,246,0.28);
        border-radius:20px;
        padding:22px;
        margin-bottom:16px;
        background:
        radial-gradient(
        circle at top right,
        rgba(139,92,246,0.16),
        transparent 42%
         ),
         linear-gradient(
             145deg,
             rgba(20,18,30,0.96),
             rgba(10,10,15,0.98)
         );
     box-shadow:
         0 12px 35px rgba(0,0,0,0.28),
         inset 0 1px 0 rgba(255,255,255,0.04);
 ">
    <div style="
        position:absolute;
        width:120px;
        height:120px;
        right:-45px;
        top:-45px;
        border-radius:50%;
        background:rgba(139,92,246,0.13);
        filter:blur(35px);
        pointer-events:none;
    "></div>

    <div style="
        display:flex;
        align-items:center;
        gap:14px;
        margin-bottom:14px;
    ">

        <div style="
            width:52px;
            height:52px;
            flex-shrink:0;
            border-radius:16px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:25px;
            background:linear-gradient(
                135deg,
                #8B5CF6,
                #6D28D9
            );
            box-shadow:
                0 8px 22px rgba(139,92,246,0.25);
        ">
            📖
        </div>

        <div style="
            min-width:0;
        ">
            <h3 style="
                margin:0;
                color:#FFFFFF;
                font-size:18px;
                font-weight:800;
                line-height:1.35;
            ">
                ${book.title}
            </h3>
        </div>

    </div>

    <p style="
        color:#AAA5B8;
        margin:0 0 18px;
        line-height:1.6;
        font-size:14px;
    ">
        ${book.description || "Tavsif mavjud emas"}
    </p>

    <div style="
        height:1px;
        background:rgba(255,255,255,0.07);
        margin-bottom:17px;
    "></div>

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:flex-end;
        gap:15px;
        flex-wrap:wrap;
    ">

        <div>

            <div style="
                color:#817C8F;
                font-size:12px;
                margin-bottom:5px;
            ">
                Oddiy narx
            </div>

            <div style="
                color:#E9E5F2;
                font-size:14px;
                font-weight:600;
            ">
                ${book.price.toLocaleString()} so'm
            </div>

            <div style="
                color:#C4B5FD;
                font-size:16px;
                font-weight:800;
                margin-top:7px;
            ">
                🪙 ${book.coin_price} Coin
            </div>

        </div>

        <button
            onclick="buyStudentBook(${book.id})"
            style="
                border:none;
                border-radius:13px;
                padding:12px 20px;
                background:linear-gradient(
                    135deg,
                    #8B5CF6,
                    #6D28D9
                );
                color:#FFFFFF;
                font-size:14px;
                font-weight:800;
                cursor:pointer;
                box-shadow:
                    0 8px 24px rgba(139,92,246,0.25);
            "
        >
            Sotib olish
        </button>

    </div>

    <div style="
        margin-top:16px;
        color:#777285;
        font-size:12px;
    ">
        Mavjud: ${book.stock} dona
    </div>

</div>

`).join("");

    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:25px;
                color:#ff6b6b;
            ">
                Kitoblarni yuklashda xatolik yuz berdi.
            </div>
        `;
    }
}


async function buyStudentBook(bookId) {
    
const token = localStorage.getItem("access_token");

if (!token) {
    showPremiumModal(
        "Tizimga kirish kerak",
        "Kitob sotib olish uchun avval tizimga kiring.",
        "Kirish"
    );
    return;
}

showPremiumModal(
    "📖 Kitobni sotib olish",
    "Bu kitobni Coin orqali sotib olishni tasdiqlaysizmi?",
    "Sotib olish",
    async () => {

        try {

            const response = await fetch(
                `${API_URL}/students/books/${bookId}/buy`,
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Kitobni sotib olishda xatolik"
                );
            }

            showPremiumModal(
                "Xarid muvaffaqiyatli!",
                `🎉 ${data.message}<br><br>` +
                `Buyurtma №${data.order_id}<br>` +
                `🪙 Qolgan Coin: ${data.student.coins}`,
                "Ajoyib!"
            );

            await loadStudentBooks();

        } catch (error) {

            console.error(error);

            showPremiumModal(
                "Xatolik yuz berdi",
                error.message,
                "Yopish"
            );
        }
    }
);

}


/* =========================
   PODCASTS / TRAININGS / EXAMS
========================= */

function closeStudentExtraModal() {
    const modal = document.getElementById("studentExtraContentModal");
    if (modal) modal.remove();
}

function openStudentExtraModal(title) {
    closeStudentExtraModal();

    const modal = document.createElement("div");
    modal.id = "studentExtraContentModal";
    modal.innerHTML = `
        <div style="position:fixed;inset:0;z-index:99998;background:rgba(0,0,0,.78);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;padding:18px;">
            <div style="width:100%;max-width:620px;max-height:88vh;overflow:auto;background:linear-gradient(145deg,#111118,#09090d);border:1px solid rgba(139,92,246,.3);border-radius:24px;padding:24px;color:#f5f3ff;box-sizing:border-box;box-shadow:0 25px 80px rgba(0,0,0,.65);">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:15px;margin-bottom:20px;">
                    <h2 id="studentExtraTitle" style="margin:0;color:#fff;font-size:22px;">${title}</h2>
                    <button type="button" onclick="closeStudentExtraModal()" style="width:40px;height:40px;border:1px solid rgba(255,255,255,.1);border-radius:12px;background:rgba(255,255,255,.05);color:#fff;font-size:20px;cursor:pointer;">×</button>
                </div>
                <div id="studentExtraContentBody"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function studentExtraLoading(text) {
    return `<div style="text-align:center;padding:35px 15px;color:#aaa5b8;font-size:15px;">⏳<br><br>${text}</div>`;
}

function studentExtraError(text) {
    return `<div style="padding:18px;border-radius:15px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.22);color:#fca5a5;">❌ ${escapeHtml(text)}</div>`;
}

function formatStudentContentDate(value) {
    if (!value) return "Vaqt belgilanmagan";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("uz-UZ", {
        day:"2-digit", month:"2-digit", year:"numeric",
        hour:"2-digit", minute:"2-digit"
    });
}

async function loadStudentPodcasts() {
    const body = document.getElementById("studentExtraContentBody");
    if (!body) return;
    const token = localStorage.getItem("access_token");
    if (!token) {
        body.innerHTML = studentExtraError("Avval tizimga kiring.");
        return;
    }

    body.innerHTML = studentExtraLoading("Podcastlar yuklanmoqda...");

    try {
        const response = await fetch(`${API_URL}/students/podcasts`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Podcastlarni yuklashda xatolik.");

        if (!Array.isArray(data) || !data.length) {
            body.innerHTML = '<div style="text-align:center;padding:35px;color:#aaa5b8;"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;"><path d="M5 13a7 7 0 0 1 14 0"/><path d="M5 13v4a2 2 0 0 0 2 2h1v-7H7a2 2 0 0 0-2 1ZM19 13v4a2 2 0 0 1-2 2h-1v-7h1a2 2 0 0 1 2 1ZM12 19v2"/></svg><span style="margin-left:10px;">Hozircha podcastlar mavjud emas.</span></div>';
            return;
        }

        body.innerHTML = data.map(item => `
            <div style="padding:18px;margin-bottom:12px;border:1px solid rgba(139,92,246,.2);border-radius:18px;background:rgba(255,255,255,.035);">
                <div style="font-size:17px;font-weight:800;color:#fff;margin-bottom:7px;">🎧 ${escapeHtml(item.title || "Nomsiz podcast")}</div>
                <div style="color:#aaa5b8;line-height:1.6;margin-bottom:12px;">${escapeHtml(item.description || "Tavsif mavjud emas")}</div>
                ${item.audio_url ? `<audio controls preload="none" style="width:100%;"><source src="${escapeHtml(item.audio_url)}"></audio>` : '<div style="color:#817c8f;font-size:13px;">Audio fayl hali biriktirilmagan.</div>'}
                ${item.duration_minutes ? `<div style="margin-top:10px;color:#c4b5fd;font-size:12px;">⏱ ${item.duration_minutes} daqiqa</div>` : ""}
            </div>
        `).join("");
    } catch (error) {
        console.error("Podcastlar:", error);
        body.innerHTML = studentExtraError(error.message || "Podcastlarni yuklashda xatolik.");
    }
}

async function loadStudentTrainings() {
    const body = document.getElementById("studentExtraContentBody");
    if (!body) return;
    const token = localStorage.getItem("access_token");
    if (!token) {
        body.innerHTML = studentExtraError("Avval tizimga kiring.");
        return;
    }

    body.innerHTML = studentExtraLoading("Treninglar yuklanmoqda...");

    try {
        const response = await fetch(`${API_URL}/students/trainings`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Treninglarni yuklashda xatolik.");

        if (!Array.isArray(data) || !data.length) {
            body.innerHTML = '<div style="text-align:center;padding:35px;color:#aaa5b8;"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;"><path d="M4 7.5 12 4l8 3.5L12 11 4 7.5Z"/><path d="M6.5 9v5.2c0 1.8 2.5 3.3 5.5 3.3s5.5-1.5 5.5-3.3V9"/><path d="M20 8v6"/></svg><span style="margin-left:10px;">Hozircha faol treninglar mavjud emas.</span></div>';
            return;
        }

        body.innerHTML = data.map(item => `
            <div style="padding:18px;margin-bottom:12px;border:1px solid rgba(34,197,94,.18);border-radius:18px;background:rgba(255,255,255,.035);">
                <div style="font-size:17px;font-weight:800;color:#fff;margin-bottom:7px;">📅 ${escapeHtml(item.title || "Nomsiz trening")}</div>
                <div style="color:#aaa5b8;line-height:1.6;margin-bottom:10px;">${escapeHtml(item.description || "Tavsif mavjud emas")}</div>
                <div style="color:#c4b5fd;font-size:13px;line-height:1.7;">
                    🕒 ${escapeHtml(formatStudentContentDate(item.start_at))}
                    ${item.end_at ? " — " + escapeHtml(formatStudentContentDate(item.end_at)) : ""}
                    ${item.location ? "<br>📍 " + escapeHtml(item.location) : ""}
                </div>
                <div style="margin-top:14px;">
                    ${item.registered
                        ? '<div style="padding:11px 14px;border-radius:12px;background:rgba(34,197,94,.1);color:#86efac;font-weight:700;">✅ Siz ro‘yxatdan o‘tgansiz</div>'
                        : `<button type="button" onclick="registerStudentTraining(${Number(item.id)})" style="width:100%;border:0;border-radius:12px;padding:12px;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:800;cursor:pointer;">Treningka ro‘yxatdan o‘tish</button>`}
                </div>
            </div>
        `).join("");
    } catch (error) {
        console.error("Treninglar:", error);
        body.innerHTML = studentExtraError(error.message || "Treninglarni yuklashda xatolik.");
    }
}

async function registerStudentTraining(trainingId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
        showPremiumModal("Tizimga kirish kerak","Treningka yozilish uchun avval tizimga kiring.","Kirish");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/students/trainings/${trainingId}/register`, {
            method:"POST",
            headers:{ "Authorization":`Bearer ${token}` }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Treningka ro‘yxatdan o‘tishda xatolik.");

        showPremiumModal("Ro‘yxatdan o‘tildi",data.message || "Treningka muvaffaqiyatli ro‘yxatdan o‘tildi.","Ajoyib!");
        await loadStudentTrainings();
    } catch (error) {
        console.error("Trening ro‘yxatdan o‘tish:",error);
        showPremiumModal("Xatolik yuz berdi",error.message,"Yopish");
    }
}

async function loadStudentExams() {
    const body = document.getElementById("studentExtraContentBody");
    if (!body) return;
    const token = localStorage.getItem("access_token");
    if (!token) {
        body.innerHTML = studentExtraError("Avval tizimga kiring.");
        return;
    }

    body.innerHTML = studentExtraLoading("Imtihonlar yuklanmoqda...");

    try {
        const response = await fetch(`${API_URL}/students/exams`, {
            headers:{ "Authorization":`Bearer ${token}` }
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Imtihonlarni yuklashda xatolik.");

        if (!Array.isArray(data) || !data.length) {
            body.innerHTML = '<div style="text-align:center;padding:35px;color:#aaa5b8;"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;"><path d="M9 3h6M10 3v5l-5 9a3 3 0 0 0 3 4h8a3 3 0 0 0 3-4l-5-9V3"/><path d="M8 15h8"/></svg><span style="margin-left:10px;">Hozircha faol imtihonlar mavjud emas.</span></div>';
            return;
        }

        body.innerHTML = data.map(item => `
            <div style="padding:18px;margin-bottom:12px;border:1px solid rgba(59,130,246,.18);border-radius:18px;background:rgba(255,255,255,.035);">
                <div style="font-size:17px;font-weight:800;color:#fff;margin-bottom:7px;">🧪 ${escapeHtml(item.title || "Nomsiz imtihon")}</div>
                <div style="color:#aaa5b8;line-height:1.6;margin-bottom:10px;">${escapeHtml(item.description || "Tavsif mavjud emas")}</div>
                <div style="color:#c4b5fd;font-size:13px;line-height:1.7;">
                    🕒 ${escapeHtml(formatStudentContentDate(item.start_at))}
                    ${item.end_at ? " — " + escapeHtml(formatStudentContentDate(item.end_at)) : ""}
                    ${item.location ? "<br>📍 " + escapeHtml(item.location) : ""}
                </div>
                <div style="margin-top:14px;">
                    ${item.registered
                        ? '<div style="padding:11px 14px;border-radius:12px;background:rgba(59,130,246,.1);color:#93c5fd;font-weight:700;">✅ Siz ro‘yxatdan o‘tgansiz</div>'
                        : `<button type="button" onclick="registerStudentExam(${Number(item.id)})" style="width:100%;border:0;border-radius:12px;padding:12px;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:800;cursor:pointer;">Imtihonga ro‘yxatdan o‘tish</button>`}
                </div>
            </div>
        `).join("");
    } catch (error) {
        console.error("Imtihonlar:",error);
        body.innerHTML = studentExtraError(error.message || "Imtihonlarni yuklashda xatolik.");
    }
}

async function registerStudentExam(examId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
        showPremiumModal("Tizimga kirish kerak","Imtihonga yozilish uchun avval tizimga kiring.","Kirish");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/students/exams/${examId}/register`, {
            method:"POST",
            headers:{ "Authorization":`Bearer ${token}` }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Imtihonga ro‘yxatdan o‘tishda xatolik.");

        showPremiumModal("Ro‘yxatdan o‘tildi",data.message || "Imtihonga muvaffaqiyatli ro‘yxatdan o‘tildi.","Ajoyib!");
        await loadStudentExams();
    } catch (error) {
        console.error("Imtihon ro‘yxatdan o‘tish:",error);
        showPremiumModal("Xatolik yuz berdi",error.message,"Yopish");
    }
}

function openStudentPodcasts() {
    openStudentExtraModal("<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M5 13a7 7 0 0 1 14 0\"/><path d=\"M5 13v4a2 2 0 0 0 2 2h1v-7H7a2 2 0 0 0-2 1ZM19 13v4a2 2 0 0 1-2 2h-1v-7h1a2 2 0 0 1 2 1ZM12 19v2\"/></svg><span style=\"margin-left:8px;\">Podcastlar</span>");
    loadStudentPodcasts();
}

function openStudentTrainings() {
    openStudentExtraModal("<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M4 7.5 12 4l8 3.5L12 11 4 7.5Z\"/><path d=\"M6.5 9v5.2c0 1.8 2.5 3.3 5.5 3.3s5.5-1.5 5.5-3.3V9\"/><path d=\"M20 8v6\"/></svg><span style=\"margin-left:8px;\">Treninglar</span>");
    loadStudentTrainings();
}

function openStudentExams() {
    openStudentExtraModal("<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\" style=\"width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;\"><path d=\"M9 3h6M10 3v5l-5 9a3 3 0 0 0 3 4h8a3 3 0 0 0 3-4l-5-9V3\"/><path d=\"M8 15h8\"/></svg><span style=\"margin-left:8px;\">Imtihonlar</span>");
    loadStudentExams();
}

   function showPremiumModal(title, message, buttonText = "Yopish", onConfirm = null) {

const oldModal = document.getElementById("premiumPurchaseModal");

if (oldModal) {
    oldModal.remove();
}

const modal = document.createElement("div");

modal.id = "premiumPurchaseModal";

modal.innerHTML = `
    <div style="
        position:fixed;
        inset:0;
        background:rgba(0,0,0,0.78);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        display:flex;
        align-items:center;
        justify-content:center;
        padding:20px;
        z-index:99999;
    ">

        <div style="
            width:100%;
            max-width:430px;
            background:
                radial-gradient(
                    circle at top right,
                    rgba(139,92,246,0.20),
                    transparent 45%
                ),
                linear-gradient(
                    145deg,
                    #111118,
                    #09090d
                );
            border:1px solid rgba(139,92,246,0.35);
            border-radius:24px;
            padding:28px;
            box-sizing:border-box;
            box-shadow:
                0 25px 80px rgba(0,0,0,0.65),
                0 0 45px rgba(139,92,246,0.12);
            color:#F5F3FF;
            position:relative;
            overflow:hidden;
        ">

            <div style="
                position:absolute;
                width:150px;
                height:150px;
                background:rgba(139,92,246,0.13);
                filter:blur(50px);
                border-radius:50%;
                top:-70px;
                right:-50px;
                pointer-events:none;
            "></div>

            <div style="
                width:58px;
                height:58px;
                border-radius:18px;
                background:linear-gradient(
                    135deg,
                    #8B5CF6,
                    #6D28D9
                );
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:27px;
                margin-bottom:18px;
                box-shadow:0 8px 25px rgba(139,92,246,0.30);
            ">
                ✨
            </div>

            <h2 style="
                margin:0 0 10px;
                font-size:22px;
                font-weight:800;
                letter-spacing:-0.3px;
                color:#FFFFFF;
            ">
                ${title}
            </h2>

            <div style="
                color:#C4B5FD;
                font-size:15px;
                line-height:1.65;
                margin-bottom:25px;
            ">
                ${message}
            </div>

            <div style="
                display:flex;
                gap:10px;
            ">

                <button
                    id="premiumCancelButton"
                    style="
                        flex:1;
                        border:1px solid rgba(255,255,255,0.10);
                        border-radius:13px;
                        padding:13px 15px;
                        background:rgba(255,255,255,0.05);
                        color:#B8B5C7;
                        font-size:14px;
                        font-weight:700;
                        cursor:pointer;
                    "
                >
                    Bekor qilish
                </button>

                <button
                    id="premiumConfirmButton"
                    style="
                        flex:1;
                        border:none;
                        border-radius:13px;
                        padding:13px 15px;
                        background:linear-gradient(
                            135deg,
                            #8B5CF6,
                            #6D28D9
                        );
                        color:#FFFFFF;
                        font-size:14px;
                        font-weight:800;
                        cursor:pointer;
                        box-shadow:
                            0 8px 25px rgba(139,92,246,0.28);
                    "
                >
                    ${buttonText}
                </button>

            </div>

        </div>

    </div>
`;

document.body.appendChild(modal);

const cancelButton = document.getElementById(
    "premiumCancelButton"
);

const confirmButton = document.getElementById(
    "premiumConfirmButton"
);

cancelButton.onclick = () => {
    modal.remove();
};

confirmButton.onclick = async () => {

    if (onConfirm) {
        modal.remove();
        await onConfirm();
    } else {
        modal.remove();
    }

};

}