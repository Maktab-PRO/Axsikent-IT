"use strict";

const API_BASE = "https://axsikent-it-4.onrender.com";
const TOKEN_KEY = "axsikent_admin_token";
const ADMIN_KEY = "axsikent_admin";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);


/* ============================================================
   AUTH
   ============================================================ */

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function getSavedAdmin() {
    try {
        return JSON.parse(localStorage.getItem(ADMIN_KEY));
    } catch {
        return null;
    }
}

function saveAdmin(data) {
    if (!data) return;
    localStorage.setItem(ADMIN_KEY, JSON.stringify(data));
}

function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ADMIN_KEY);
}

function requireAdminAuth() {
    const token = getToken();

    if (!token) {
        window.location.replace("login.html");
        return false;
    }

    return true;
}


/* ============================================================
   API
   ============================================================ */

async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        clearAuth();
        window.location.replace("login.html");
        throw new Error("Sessiya tugagan");
    }

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            "Serverda xatolik yuz berdi";

        throw new Error(message);
    }

    return data;
}


/* ============================================================
   HELPERS
   ============================================================ */

function setText(id, value) {
    const element = document.getElementById(id);

    if (!element) return;

    element.textContent = value ?? "0";
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   TOAST
   ============================================================ */

function showToast(message, type = "success") {
    const container = $("#toastContainer");

    if (!container) return;

    const toast = document.createElement("div");

    toast.className = `toast toast-${type}`;

    toast.innerHTML = `
        <span class="toast-icon">
            ${type === "error" ? "!" : "✓"}
        </span>

        <span class="toast-message">
            ${escapeHtml(message)}
        </span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("hide");

        setTimeout(() => {
            toast.remove();
        }, 300);

    }, 3000);
}


/* ============================================================
   SECTION TITLES
   ============================================================ */

const sectionTitles = {
    dashboard: "Command Center",
    students: "O‘quvchilar",
    teachers: "O‘qituvchilar",
    courses: "Kurslar",
    groups: "Guruhlar",
    homework: "Uy vazifalari",
    leads: "Arizalar",
    rewards: "Mukofotlar",
    orders: "Buyurtmalar",
    books: "Kitoblar",
    ranking: "Ranking",
    reports: "Hisobotlar",
    settings: "Sozlamalar"
};


/* ============================================================
   NAVIGATION
   ============================================================ */

function openSection(section) {
    if (!section) return;

    $$(".nav-item").forEach(item => {
        item.classList.toggle(
            "active",
            item.dataset.section === section
        );
    });

    $$(".page-section").forEach(page => {
        page.classList.toggle(
            "active",
            page.id === `section-${section}`
        );
    });

    const title =
        sectionTitles[section] ||
        "Command Center";

    const pageTitle = $("#pageTitle");
    const breadcrumb = $("#breadcrumbCurrent");

    if (pageTitle) {
        pageTitle.textContent = title;
    }

    if (breadcrumb) {
        breadcrumb.textContent = title;
    }

    const sidebar = $("#sidebar");

    if (sidebar) {
        sidebar.classList.remove("mobile-open");
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    /*
     * MUHIM:
     * O‘quvchilar bo‘limi ochilganda
     * backenddan real ma'lumot olinadi.
     */
    if (section === "students") {
        loadStudents();
    }
   if (section === "homework") { 
    loadHomeworkSubmissions();
}

}

function initNavigation() {

    $$(".nav-item").forEach(item => {

        item.addEventListener("click", () => {

            openSection(
                item.dataset.section
            );

        });

    });


    $$(".quick-action").forEach(item => {

        item.addEventListener("click", () => {

            openSection(
                item.dataset.section
            );

        });

    });


    $$(".panel-link").forEach(item => {

        item.addEventListener("click", () => {

            openSection(
                item.dataset.section
            );

        });

    });
}


/* ============================================================
   DASHBOARD
   ============================================================ */

async function loadDashboard() {

    try {

        const data =
            await apiRequest("/admins/dashboard");

        if (!data?.success) {
            throw new Error(
                "Dashboard ma'lumotlari olinmadi"
            );
        }

        const overview =
            data.overview || {};


        setText(
            "statStudents",
            overview.students?.active ?? 0
        );


        setText(
            "statTeachers",
            overview.teachers?.active ?? 0
        );


        setText(
            "statCourses",
            overview.courses?.active ?? 0
        );


        const newLeads =
            overview.leads?.new ?? 0;

        setText(
            "leadBadge",
            newLeads
        );


        if (data.admin?.full_name) {

            setText(
                "adminName",
                data.admin.full_name
            );

        }


        if (data.admin) {
            saveAdmin(data.admin);
        }


        window.adminDashboardData = data;

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        showToast(
            error.message ||
            "Dashboard yuklanmadi",
            "error"
        );
    }
}


/* ============================================================
   SHOP STATS
   ============================================================ */

async function loadShopStats() {

    try {

        const data =
            await apiRequest(
                "/admin/shop/stats/summary"
            );


        const products =
            data?.products ||
            data?.overview?.products ||
            {};


        const orders =
            data?.orders ||
            data?.overview?.orders ||
            {};


        setText(
            "statProducts",
            products.total ??
            data?.total_products ??
            0
        );


        setText(
            "statActiveProducts",
            products.active ??
            data?.active_products ??
            0
        );


        setText(
            "statPendingOrders",
            orders.pending ??
            data?.pending_orders ??
            0
        );


        setText(
            "statOrders",
            orders.pending ??
            data?.pending_orders ??
            0
        );

    } catch (error) {

        console.error(
            "Shop stats error:",
            error
        );

    }
}


/* ============================================================
   ADMIN PROFILE
   ============================================================ */

async function loadAdminProfile() {

    try {

        const data =
            await apiRequest("/admins/me");

        if (!data) return;


        setText(
            "adminName",
            data.full_name ||
            "Axsikent Admin"
        );


        saveAdmin(data);

    } catch (error) {

        console.error(
            "Admin profile error:",
            error
        );

    }
}


/* ============================================================
   REFRESH DASHBOARD
   ============================================================ */

async function refreshDashboard() {

    const button =
        $("#refreshBtn");


    if (button) {
        button.classList.add(
            "is-loading"
        );
    }


    try {

        await Promise.all([
            loadDashboard(),
            loadShopStats()
        ]);

    } finally {

        if (button) {

            setTimeout(() => {

                button.classList.remove(
                    "is-loading"
                );

            }, 500);

        }

    }
}


/* ============================================================
   MOBILE MENU
   ============================================================ */

function initMobileMenu() {

    const button =
        $("#mobileMenuBtn");

    const sidebar =
        $("#sidebar");


    if (!button || !sidebar) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
               "open"
            );

        }
    );
}


/* ============================================================
   NOTIFICATIONS
   ============================================================ */

function initNotifications() {

    const button =
        $("#notificationBtn");


    if (!button) return;


    button.addEventListener(
        "click",
        () => {

            showToast(
                "Hozircha yangi bildirishnoma yo‘q.",
                "success"
            );

        }
    );
}


/* ============================================================
   LOGOUT
   ============================================================ */

function logout() {

    clearAuth();

    window.location.href =
        "login.html";
}


/* ============================================================
   STUDENTS
   ============================================================ */

async function loadStudents() {

    const container =
        document.getElementById(
            "studentsContent"
        );


    if (!container) {

        console.error(
            "studentsContent topilmadi"
        );

        return;
    }


    container.innerHTML = `
        <div class="module-loading">

            <div class="module-spinner"></div>

            <span>
                O‘quvchilar yuklanmoqda...
            </span>

        </div>
    `;


    try {

        const data =
            await apiRequest(
                "/admin/students/"
            );


        console.log(
            "Students API:",
            data
        );


        let students = [];


        if (Array.isArray(data)) {

            students = data;

        } else if (
            Array.isArray(data.students)
        ) {

            students = data.students;

        } else if (
            Array.isArray(data.items)
        ) {

            students = data.items;

        } else if (
            Array.isArray(data.data)
        ) {

            students = data.data;

        }


        renderStudents(students);


    } catch (error) {

        console.error(
            "Students error:",
            error
        );


        container.innerHTML = `

            <div class="module-error">

                <div class="module-error-icon">
                    !
                </div>

                <h3>
                    O‘quvchilarni yuklab bo‘lmadi
                </h3>

                <p>
                    ${escapeHtml(
                        error.message ||
                        "Server xatosi"
                    )}
                </p>

                <button
                    class="module-retry"
                    onclick="loadStudents()"
                >
                    Qayta urinish
                </button>

            </div>

        `;
    }
}

   async function loadHomeworkSubmissions() {
    const container = document.getElementById(
        "homeworkSubmissionsContent"
    );

    if (!container) return;

    container.innerHTML = `
        <div class="module-loading">
            <div class="module-spinner"></div>
            <span>Topshirilgan vazifalar yuklanmoqda...</span>
        </div>
    `;

    try {
        const data = await apiRequest(
            "/admin/homework/submissions"
        );

        const submissions = data.submissions || [];

        setText(
            "homeworkTotal",
            submissions.length
        );

        setText(
            "homeworkPending",
            submissions.filter(
                item => item.status === "submitted"
            ).length
        );

        setText(
            "homeworkChecked",
            submissions.filter(
                item => item.status === "checked"
            ).length
        );

        renderHomeworkSubmissions(
            submissions
        );

    } catch (error) {

        console.error(
            "Homework submissions error:",
            error
        );

        container.innerHTML = `
            <div class="empty-module">
                <span>⚠</span>
                <h2>Ma’lumotlarni yuklab bo‘lmadi</h2>
                <p>
                    Topshirilgan vazifalarni yuklashda xatolik yuz berdi.
                </p>
            </div>
        `;
    }
}


function renderHomeworkSubmissions(
    submissions
) {

    const container = document.getElementById(
        "homeworkSubmissionsContent"
    );

    if (!container) return;

    if (!submissions.length) {

        container.innerHTML = `
            <div class="empty-module">
                <span>📝</span>
                <h2>Hozircha topshiriqlar yo‘q</h2>
                <p>
                    O‘quvchilar vazifa topshirganda
                    shu yerda ko‘rinadi.
                </p>
            </div>
        `;

        return;
    }

    container.innerHTML = `
        <div class="homework-table-wrap">

            <table class="admin-table">

                <thead>
                    <tr>
                        <th>O‘quvchi</th>
                        <th>Vazifa</th>
                        <th>Javob</th>
                        <th>Status</th>
                        <th>Ball</th>
                        <th>Topshirilgan vaqt</th>
                    </tr>
                </thead>

                <tbody>

                    ${submissions.map(item => {

                        let statusText =
                            "Kutilmoqda";

                        if (
                            item.status === "checked"
                        ) {
                            statusText =
                                "Tekshirildi";
                        } else if (
                            item.status === "late"
                        ) {
                            statusText =
                                "Kechikkan";
                        } else if (
                            item.status === "rejected"
                        ) {
                            statusText =
                                "Rad etilgan";
                        }

                        return `
                            <tr
                                onclick="viewHomeworkSubmission(${item.id})"
                                style="cursor:pointer"
                            >

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            item.student_name ||
                                            "Noma’lum"
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        item.homework_title ||
                                        "Noma’lum vazifa"
                                    )}
                                </td>

                                <td>
                                    <div class="homework-answer-preview">
                                        ${escapeHtml(
                                            item.answer ||
                                            "Javob berilmagan"
                                        )}
                                    </div>
                                </td>

                                <td>
                                    <span class="status-badge">
                                        ${statusText}
                                    </span>
                                </td>

                                <td>
                                    ${
                                        item.score !== null &&
                                        item.score !== undefined
                                            ? `${item.score}/100`
                                            : "—"
                                    }
                                </td>

                                <td>
                                    ${
                                        item.submitted_at
                                            ? new Date(
                                                item.submitted_at
                                            ).toLocaleString(
                                                "uz-UZ"
                                            )
                                            : "—"
                                    }
                                </td>

                            </tr>
                        `;

                    }).join("")}

                </tbody>

            </table>

        </div>
    `;
}


function filterHomeworkSubmissions() {

    const input = document.getElementById(
        "homeworkSearch"
    );

    if (!input) return;

    const search = input.value
        .trim()
        .toLowerCase();

    const rows = document.querySelectorAll(
        "#homeworkSubmissionsContent tbody tr"
    );

    rows.forEach(row => {

        const text = row.textContent
            .toLowerCase();

        row.style.display =
            text.includes(search)
                ? ""
                : "none";
    });
}


async function viewHomeworkSubmission(
    submissionId
) {

    try {

        const data = await apiRequest(
            `/admin/homework/submissions/${submissionId}`
        );

        const modal = document.createElement(
            "div"
        );

        modal.className =
            "admin-detail-modal";

        modal.innerHTML = `
            <div class="admin-detail-card">

                <button
                    class="admin-detail-close"
                    onclick="this.closest('.admin-detail-modal').remove()"
                >
                    ×
                </button>

                <div class="section-eyebrow">
                    UY VAZIFASI / TOPSHIRIQ
                </div>

                <h2>
                    ${escapeHtml(
                        data.student_name ||
                        "Noma’lum o‘quvchi"
                    )}
                </h2>

                <p class="admin-detail-subtitle">
                    ${escapeHtml(
                        data.homework_title ||
                        "Noma’lum vazifa"
                    )}
                </p>

                <div class="admin-detail-grid">

                    <div>
                        <small>O‘quvchi ID</small>
                        <strong>
                            ${data.student_id}
                        </strong>
                    </div>

                    <div>
                        <small>Vazifa ID</small>
                        <strong>
                            ${data.homework_id}
                        </strong>
                    </div>

                    <div>
                        <small>Status</small>
                        <strong>
                            ${escapeHtml(
                                data.status ||
                                "—"
                            )}
                        </strong>
                    </div>

                    <div>
                        <small>Ball</small>
                        <strong>
                            ${
                                data.score !== null &&
                                data.score !== undefined
                                    ? `${data.score}/100`
                                    : "—"
                            }
                        </strong>
                    </div>

                </div>

                <div class="admin-detail-block">

                    <small>O‘quvchi javobi</small>

                    <div class="homework-answer-box">
                        ${escapeHtml(
                            data.answer ||
                            "Javob berilmagan"
                        )}
                    </div>

                </div>

                ${
                    data.file_url
                        ? `
                            <div class="admin-detail-block">
                                <small>Fayl</small>
                                <a
                                    href="${escapeHtml(
                                        data.file_url
                                    )}"
                                    target="_blank"
                                >
                                    📎 Faylni ochish
                                </a>
                            </div>
                        `
                        : ""
                }

                <div class="admin-detail-block">

                    <small>
                        O‘qituvchi izohi
                    </small>

                    <div class="homework-answer-box">
                        ${escapeHtml(
                            data.teacher_comment ||
                            "Izoh berilmagan"
                        )}
                    </div>

                </div>

            </div>
        `;

        document.body.appendChild(
            modal
        );

    } catch (error) {

        console.error(
            "Submission detail error:",
            error
        );

        showToast(
            "Topshiriq ma’lumotlarini yuklab bo‘lmadi.",
            "error"
        );
    }
}
   
   /* ============================================================
   RENDER STUDENTS
   ============================================================ */

function renderStudents(students) {

    const container =
        document.getElementById(
            "studentsContent"
        );


    if (!container) return;


    if (!students.length) {

        container.innerHTML = `

            <div class="module-empty">

                <div class="module-empty-icon">
                    ◎
                </div>

                <h3>
                    Hozircha o‘quvchilar yo‘q
                </h3>

                <p>
                    Tizimda ro‘yxatdan o‘tgan
                    o‘quvchilar shu yerda ko‘rinadi.
                </p>

            </div>

        `;

        return;
    }


    container.innerHTML = `

        <div class="students-toolbar">

            <div class="students-search">

                <span>⌕</span>

                <input
                    type="text"
                    id="studentSearchInput"
                    placeholder="Ism yoki telefon bo‘yicha qidirish..."
                >

            </div>


            <div class="students-filter">

                <select id="studentStatusFilter">

                    <option value="all">
                        Barcha holatlar
                    </option>

                    <option value="active">
                        Faol
                    </option>

                    <option value="inactive">
                        Nofaol
                    </option>

                </select>

            </div>

        </div>


        <div class="students-table-wrap">

            <table class="students-table">

                <thead>

                    <tr>

                        <th>
                            O‘QUVCHI
                        </th>

                        <th>
                            TELEFON
                        </th>

                        <th>
                            ID
                        </th>

                        <th>
                            HOLAT
                        </th>

                        <th>
                            AMAL
                        </th>

                    </tr>

                </thead>


                <tbody id="studentsTableBody">

                    ${students
                        .map(student => studentRow(student))
                        .join("")}

                </tbody>

            </table>

        </div>


        <div class="students-footer">

            Jami:
            <strong>
                ${students.length}
            </strong>
            ta o‘quvchi

        </div>

    `;


    const searchInput =
        document.getElementById(
            "studentSearchInput"
        );


    const statusFilter =
        document.getElementById(
            "studentStatusFilter"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            () => {

                filterStudents(
                    students
                );

            }
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            () => {

                filterStudents(
                    students
                );

            }
        );

    }
}


/* ============================================================
   STUDENT ROW
   ============================================================ */

function studentRow(student) {

    const id =
        student.id ?? "-";


    const name =
        student.full_name ||
        student.name ||
        "Noma’lum";


    const phone =
        student.phone ||
        "-";


    const active =
        student.is_active !== false;


    const initials =
        name
            .split(" ")
            .filter(Boolean)
            .slice(0, 2)
            .map(word =>
                word.charAt(0).toUpperCase()
            )
            .join("");


    return `

        <tr
            data-name="${escapeHtml(
                name.toLowerCase()
            )}"

            data-phone="${escapeHtml(
                phone.toLowerCase()
            )}"

            data-status="${
                active
                    ? "active"
                    : "inactive"
            }"
        >

            <td>

                <div class="student-identity">

                    <div class="student-avatar">

                        ${escapeHtml(
                            initials || "U"
                        )}

                    </div>


                    <div>

                        <div class="student-name">

                            ${escapeHtml(name)}

                        </div>


                        <div class="student-role">

                            Student

                        </div>

                    </div>

                </div>

            </td>


            <td>

                <span class="student-phone">

                    ${escapeHtml(phone)}

                </span>

            </td>


            <td>

                <span class="student-id">

                    #${escapeHtml(id)}

                </span>

            </td>


            <td>

                <span
                    class="status-badge ${
                        active
                            ? "status-active"
                            : "status-inactive"
                    }"
                >

                    <span></span>

                    ${
                        active
                            ? "Faol"
                            : "Nofaol"
                    }

                </span>

            </td>


            <td>

                <div class="student-actions">

                    <button
                        class="student-action-btn"
                        onclick="viewStudent(${Number(id)})"
                    >
                        Ko‘rish
                    </button>


                    <button
                        class="student-action-btn ${
                            active
                                ? "danger"
                                : "success"
                        }"

                        onclick="toggleStudentStatus(
                            ${Number(id)},
                            ${active}
                        )"
                    >

                        ${
                            active
                                ? "Bloklash"
                                : "Faollashtirish"
                        }

                    </button>

                </div>

            </td>

        </tr>

    `;
}


/* ============================================================
   SEARCH / FILTER
   ============================================================ */

function filterStudents(students) {

    const search =
        (
            document.getElementById(
                "studentSearchInput"
            )?.value || ""
        )
        .trim()
        .toLowerCase();


    const status =
        document.getElementById(
            "studentStatusFilter"
        )?.value || "all";


    const filtered =
        students.filter(student => {

            const name =
                (
                    student.full_name ||
                    student.name ||
                    ""
                ).toLowerCase();


            const phone =
                (
                    student.phone ||
                    ""
                ).toLowerCase();


            const active =
                student.is_active !== false;


            const matchesSearch =
                !search ||
                name.includes(search) ||
                phone.includes(search);


            const matchesStatus =
                status === "all" ||
                (
                    status === "active" &&
                    active
                ) ||
                (
                    status === "inactive" &&
                    !active
                );


            return (
                matchesSearch &&
                matchesStatus
            );
        });


    const tbody =
        document.getElementById(
            "studentsTableBody"
        );


    if (!tbody) return;


    if (!filtered.length) {

        tbody.innerHTML = `

            <tr>

                <td colspan="5">

                    <div class="table-empty">

                        Hech narsa topilmadi.

                    </div>

                </td>

            </tr>

        `;

        return;
    }


    tbody.innerHTML =
        filtered
            .map(student =>
                studentRow(student)
            )
            .join("");
}


/* ============================================================
   STUDENT PROFILE
   ============================================================ */

async function viewStudent(studentId) {

    try {

        const data =
            await apiRequest(
                `/admin/students/${studentId}`
            );


        showStudentModal(data);

    } catch (error) {

        showToast(
            error.message ||
            "O‘quvchi ma’lumotlarini olishda xatolik",
            "error"
        );
    }
}


/* ============================================================
   STUDENT MODAL
   ============================================================ */

function showStudentModal(student) {

    const oldModal =
        document.getElementById(
            "studentModal"
        );


    if (oldModal) {
        oldModal.remove();
    }


    const name =
        student.full_name ||
        student.name ||
        "Noma’lum o‘quvchi";


    const phone =
        student.phone ||
        "-";


    const id =
        student.id ?? "-";


    const active =
        student.is_active !== false;


    const initials =
        name
            .split(" ")
            .filter(Boolean)
            .slice(0, 2)
            .map(x => x[0])
            .join("")
            .toUpperCase();


    const modal =
        document.createElement("div");


    modal.id =
        "studentModal";


    modal.className =
        "admin-modal-overlay";


    modal.innerHTML = `

        <div class="admin-modal">

            <button
                class="admin-modal-close"
                onclick="closeStudentModal()"
            >
                ×
            </button>


            <div class="modal-profile">

                <div class="modal-avatar">

                    ${escapeHtml(
                        initials || "U"
                    )}

                </div>


                <div>

                    <div class="modal-eyebrow">

                        STUDENT PROFILE

                    </div>


                    <h2>

                        ${escapeHtml(name)}

                    </h2>


                    <span
                        class="status-badge ${
                            active
                                ? "status-active"
                                : "status-inactive"
                        }"
                    >

                        <span></span>

                        ${
                            active
                                ? "Faol"
                                : "Nofaol"
                        }

                    </span>

                </div>

            </div>


            <div class="modal-info-grid">

                <div class="modal-info-card">

                    <span>ID</span>

                    <strong>
                        #${escapeHtml(id)}
                    </strong>

                </div>


                <div class="modal-info-card">

                    <span>Telefon</span>

                    <strong>
                        ${escapeHtml(phone)}
                    </strong>

                </div>


                <div class="modal-info-card">

                    <span>Rol</span>

                    <strong>
                        Student
                    </strong>

                </div>


                <div class="modal-info-card">

                    <span>Holat</span>

                    <strong>
                        ${
                            active
                                ? "Faol"
                                : "Nofaol"
                        }
                    </strong>

                </div>

            </div>


            <div class="modal-actions">

                <button
                    class="modal-secondary-btn"
                    onclick="closeStudentModal()"
                >
                    Yopish
                </button>


                <button
                    class="modal-primary-btn"

                    onclick="
                        toggleStudentStatus(
                            ${Number(id)},
                            ${active}
                        );
                        closeStudentModal();
                    "
                >

                    ${
                        active
                            ? "Bloklash"
                            : "Faollashtirish"
                    }

                </button>

            </div>

        </div>

    `;


    document.body.appendChild(modal);


    requestAnimationFrame(() => {

        modal.classList.add("show");

    });
}


function closeStudentModal() {

    const modal =
        document.getElementById(
            "studentModal"
        );


    if (!modal) return;


    modal.classList.remove(
        "show"
    );


    setTimeout(() => {

        modal.remove();

    }, 250);
}


/* ============================================================
   STUDENT STATUS
   ============================================================ */

async function toggleStudentStatus(
    studentId,
    currentlyActive
) {

    const action =
        currentlyActive
            ? "deactivate"
            : "activate";


    try {

        await apiRequest(
            `/admin/students/${studentId}/${action}`,
            {
                method: "PATCH"
            }
        );


        showToast(
            currentlyActive
                ? "O‘quvchi deaktiv qilindi"
                : "O‘quvchi faollashtirildi",
            "success"
        );


        await loadStudents();

        await loadDashboard();

    } catch (error) {

        showToast(
            error.message ||
            "Holatni o‘zgartirishda xatolik",
            "error"
        );
    }
}


/* ============================================================
   INITIALIZE
   ============================================================ */

async function initAdminPanel() {

    if (!requireAdminAuth()) {
        return;
    }


    console.log(
        "Axsikent IT Command Center ishga tushdi."
    );


    initNavigation();

    initMobileMenu();

    initNotifications();


    const logoutButton =
        $("#logoutBtn");


    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            logout
        );

    }


    const refreshButton =
        $("#refreshBtn");


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            refreshDashboard
        );

    }


    await loadAdminProfile();

    await refreshDashboard();


    console.log(
        "Command Center tayyor."
    );
}


document.addEventListener(
    "DOMContentLoaded",
    initAdminPanel
);
