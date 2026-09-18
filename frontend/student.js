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
                    <div style="font-size:40px; margin-bottom:10px;">
                        📚
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

                        <div class="course-icon">
                            💻
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
            <div style="
                font-size:32px;
                margin-bottom:10px;
            ">📚</div>

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
                            font-size:17px;
                            font-weight:800;
                            color:#f8fafc;
                        ">
                            📚 ${module.title}
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
            📖 Darslar yuklanmoqda...
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

                <div style="
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
                    ${lesson.completed ? "✅" : "📖"}
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
            <div style="font-size:35px;">📝</div>
            <div style="margin-top:10px;font-weight:600;">
                Tekshiruv yuklanmoqda...
            </div>
        </div>
    `;

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
                    <div style="
                        text-align:center;
                        color:#7b8496;
                        padding:10px;
                    ">
                        Tekshirilmoqda...
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

    if (!container) {
        return;
    }

    container.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    await loadStudentRewards();
}

    async function loadStudentRewards() {

    const container = document.getElementById("studentRewardsContent");

    if (!container) {
        return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
        container.innerHTML =
            '<div style="text-align:center;padding:30px;color:#ef4444;">' +
            'Avval tizimga kiring.' +
            '</div>';
        return;
    }

    container.innerHTML =
        '<div style="text-align:center;padding:25px;color:#7b8496;">' +
        'Mukofotlar yuklanmoqda...' +
        '</div>';

    try {

        const response = await fetch(
            API_URL + "/students/rewards",
            {
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            throw new Error("Mukofotlarni yuklab bo‘lmadi");
        }

        const data = await response.json();
        const student = data.student || {};
        const rewards = data.rewards || [];

        const rewardHtml = rewards.map(function(reward) {

            const crystalHtml =
                Number(reward.crystal_price || 0) > 0
                    ? '<div style="color:#C4B5FD;font-size:16px;font-weight:800;margin-top:7px;">' +
                      '💎 ' + reward.crystal_price + ' Crystal' +
                      '</div>'
                    : "";

            return (
                '<div style="' +
                    'position:relative;overflow:hidden;' +
                    'border:1px solid rgba(139,92,246,0.28);' +
                    'border-radius:20px;padding:22px;margin-bottom:16px;' +
                    'background:radial-gradient(circle at top right,rgba(139,92,246,0.16),transparent 42%),' +
                    'linear-gradient(145deg,rgba(20,18,30,0.96),rgba(10,10,15,0.98));' +
                    'box-shadow:0 12px 35px rgba(0,0,0,0.28),inset 0 1px 0 rgba(255,255,255,0.04);' +
                '">' +

                    '<div style="position:absolute;width:120px;height:120px;right:-45px;top:-45px;border-radius:50%;' +
                        'background:rgba(139,92,246,0.13);filter:blur(35px);pointer-events:none;">' +
                    '</div>' +

                    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">' +

                        '<div style="width:52px;height:52px;flex-shrink:0;border-radius:16px;display:flex;' +
                            'align-items:center;justify-content:center;font-size:25px;' +
                            'background:linear-gradient(135deg,#8B5CF6,#6D28D9);' +
                            'box-shadow:0 8px 22px rgba(139,92,246,0.25);">' +
                            '🎁' +
                        '</div>' +

                        '<div style="min-width:0;">' +
                            '<h3 style="margin:0;color:#FFFFFF;font-size:18px;font-weight:800;line-height:1.35;">' +
                                escapeHtml(reward.name || "Mukofot") +
                            '</h3>' +
                        '</div>' +

                    '</div>' +

                    '<p style="color:#AAA5B8;margin:0 0 18px;line-height:1.6;font-size:14px;">' +
                        escapeHtml(reward.description || "Mukofot tavsifi mavjud emas") +
                    '</p>' +

                    '<div style="height:1px;background:rgba(255,255,255,0.07);margin-bottom:17px;"></div>' +

                    '<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:15px;flex-wrap:wrap;">' +

                        '<div>' +
                            '<div style="color:#817C8F;font-size:12px;margin-bottom:5px;">Mukofot narxi</div>' +

                            '<div style="color:#C4B5FD;font-size:16px;font-weight:800;">' +
                                '🪙 ' + Number(reward.coin_price || 0) + ' Coin' +
                            '</div>' +

                            crystalHtml +
                        '</div>' +

                        '<button' +
                            ' onclick="buyStudentReward(' + Number(reward.id) + ')"' +
                            ' style="border:none;border-radius:13px;padding:12px 20px;' +
                                'background:linear-gradient(135deg,#8B5CF6,#6D28D9);' +
                                'color:#FFFFFF;font-size:14px;font-weight:800;cursor:pointer;' +
                                'box-shadow:0 8px 24px rgba(139,92,246,0.25);"' +
                        '>' +
                            'Sotib olish' +
                        '</button>' +

                    '</div>' +

                    '<div style="margin-top:16px;color:#777285;font-size:12px;">' +
                        'Mavjud: ' + Number(reward.stock || 0) + ' dona' +
                    '</div>' +

                '</div>'
            );

        }).join("");

        container.innerHTML =
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:20px;">' +

                '<div style="padding:16px;border-radius:16px;background:rgba(52,211,153,.10);border:1px solid rgba(52,211,153,.18);">' +
                    '<div style="font-size:22px;">🪙</div>' +
                    '<div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' +
                        Number(student.coins || 0) +
                    '</div>' +
                    '<div style="color:#9ca3af;font-size:12px;">Coin</div>' +
                '</div>' +

                '<div style="padding:16px;border-radius:16px;background:rgba(168,85,247,.10);border:1px solid rgba(168,85,247,.18);">' +
                    '<div style="font-size:22px;">💎</div>' +
                    '<div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' +
                        Number(student.crystals || 0) +
                    '</div>' +
                    '<div style="color:#9ca3af;font-size:12px;">Crystal</div>' +
                '</div>' +

                '<div style="padding:16px;border-radius:16px;background:rgba(59,130,246,.10);border:1px solid rgba(59,130,246,.18);">' +
                    '<div style="font-size:22px;">⭐</div>' +
                    '<div style="color:#fff;font-size:20px;font-weight:800;margin-top:5px;">' +
                        Number(student.xp || 0) +
                    '</div>' +
                    '<div style="color:#9ca3af;font-size:12px;">XP · Level ' +
                        Number(student.level || 1) +
                    '</div>' +
                '</div>' +

            '</div>' +

            '<h3 style="color:#fff;margin:0 0 14px;font-size:17px;">' +
                '🎁 Mavjud mukofotlar' +
            '</h3>' +

            rewardHtml;

    } catch (error) {

        console.error(error);

        container.innerHTML =
            '<div style="text-align:center;padding:30px;color:#ef4444;">' +
            'Mukofotlarni yuklashda xatolik yuz berdi.' +
            '</div>';
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

                    <div style="
                        font-size:45px;
                        margin-bottom:12px;
                    ">
                        🎉
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
        alert("Avval javobingizni yozing.");
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

        alert("✅ Uy vazifasi muvaffaqiyatli topshirildi!");

        await loadStudentHomework();
        await loadStudentHomeworkResults();

    } catch (error) {

        console.error(error);

        alert("❌ " + error.message);
    }
}

    /* =========================
       MESSAGE
    ========================= */

    function showMessage(message) {

        alert(message);

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
        const response = await fetch(
            `${API_URL}/students/books`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

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

