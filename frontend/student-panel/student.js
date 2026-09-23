async function fetchStudentApi(path, token, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60000);
    const externalSignal = options.signal;
    const abortFromExternal = () => controller.abort();

    if (externalSignal) {
        if (externalSignal.aborted) {
            controller.abort();
        } else {
            externalSignal.addEventListener("abort", abortFromExternal, {once: true});
        }
    }

    try {
        const response = await fetch(API_URL + path, {
            ...options,
            headers: {
                "Accept": "application/json",
                ...(options.headers || {}),
                "Authorization": "Bearer " + token
            },
            cache: "no-store",
            signal: controller.signal
        });

        const text = await response.text();
        let data = {};

        if (text) {
            try {
                data = JSON.parse(text);
            } catch (_) {
                data = {};
            }
        }

        return {response, data};
    } finally {
        clearTimeout(timeout);
        if (externalSignal) {
            externalSignal.removeEventListener("abort", abortFromExternal);
        }
    }
}

const API_URL = "https://axsikent-it-backend.onrender.com";
// Student API fetches use a hard timeout so Rewards/Notifications cannot stay on loading forever.
    /* =========================
   LOAD STUDENT COURSES
========================= */

async function loadStudentCourses() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    const container = document.getElementById("studentCourses");

    if (!container) {
        console.error("Student courses container topilmadi.");
        return;
    }

    try {
        if (studentCoursesLoadController) studentCoursesLoadController.abort();
        const controller = new AbortController();
        studentCoursesLoadController = controller;

        const {response, data: courses} = await fetchStudentApi(
            "/students/courses",
            token,
            {method: "GET", signal: controller.signal}
        );

        if (response.status === 401) {

            localStorage.removeItem("access_token");
            localStorage.removeItem("user_role");

            window.location.href = "../index.html";
            return;
        }

        if (!response.ok) {
            // Vaqtinchalik API/network xatosini studentga ko‘rsatmaymiz.
            return;
        }

        if (!Array.isArray(courses)) {
            throw new Error("Kurslar ma'lumotlari noto'g'ri formatda");
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
                                ${escapeHtml(course.name || "Kurs")}
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
        if (error?.name === "AbortError") return;

        // Render/Internet qisqa uzilishida bir marta qayta urinib ko‘ramiz.
        // Muvaffaqiyatsiz bo‘lsa ham studentga xatolik oynasi/yozuvi chiqmaydi.
        try {
            await new Promise(resolve => setTimeout(resolve, 800));
            const retryController = new AbortController();
            studentCoursesLoadController = retryController;
            const {response: retryResponse, data: retryCourses} = await fetchStudentApi(
                "/students/courses",
                token,
                {method: "GET", signal: retryController.signal}
            );

            if (retryResponse.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                window.location.href = "../index.html";
                return;
            }

            if (retryResponse.ok && Array.isArray(retryCourses)) {
                if (!retryCourses.length) {
                    container.innerHTML = `
                        <div style="text-align:center;padding:25px;color:#7b8496;">
                            Hozircha kurs biriktirilmagan
                        </div>
                    `;
                    return;
                }

                container.innerHTML = retryCourses.map(course => {
                    const progress = Math.min(100, Math.max(0, Number(course.progress) || 0));
                    return `
                        <div class="course" onclick="openStudentCourse(${course.id})" style="cursor:pointer;">
                            <div class="course-top">
                                <div class="course-icon student-modern-course-icon">
                                    <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="11" rx="2"/><path d="M8 20h8M12 16v4"/></svg>
                                </div>
                                <div>
                                    <div class="course-name">${escapeHtml(course.name || "Kurs")}</div>
                                    <div class="course-info">Kurs davom etmoqda</div>
                                </div>
                            </div>
                            <div class="progress"><div class="progress-bar" style="width:${progress}%"></div></div>
                            <div class="progress-text"><span>Jarayon</span><span>${progress}%</span></div>
                        </div>
                    `;
                }).join("");
                return;
            }
        } catch (retryError) {
            console.error("Student courses retry:", retryError);
            if (retryError?.name === "AbortError") return;
        }

        // Qayta urinish ham muvaffaqiyatsiz bo‘lsa, mavjud UI holatini saqlaymiz.
        return;
    }
}


    /* =========================
       LOAD STUDENT
    ========================= */
async function openStudentCourse(courseId) {

    const token = localStorage.getItem("access_token");
    const container = document.getElementById("studentCourses");

    if (!token) {
        window.location.href = "../index.html";
        return;
    }

    if (!container) {
        console.error("Student courses container topilmadi.");
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
        if (studentOpenCourseController) studentOpenCourseController.abort();
        const controller = new AbortController();
        studentOpenCourseController = controller;

        const {response, data: modules} = await fetchStudentApi(
            `/students/courses/${courseId}/modules`,
            token,
            {signal: controller.signal}
        );
        if (response.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user_role");
            window.location.href = "../index.html";
            return;
        }



        if (!response.ok) {
            throw new Error("Modullarni yuklashda xatolik");
        }

        if (!Array.isArray(modules)) {
            throw new Error("Modullar ma'lumotlari noto'g'ri formatda");