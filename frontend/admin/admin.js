"use strict";

const API_BASE = "https://axsikent-it-4.onrender.com";
const TOKEN_KEY = "axsikent_admin_token";
const ADMIN_KEY = "axsikent_admin";
const SESSION_KEY = "axsikent_admin_session";

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
    const session = sessionStorage.getItem(SESSION_KEY);

    if (!token || session !== "active") {
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
    settings: "Sozlamalar",
    administrators: "Administratorlar",
    podcasts: "Podcastlar",
    trainings: "Treninglar",
    exams: "Imtihonlar"
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
        sidebar.classList.remove("open");
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

    if (section === "teachers") loadTeachers();
    if (section === "courses") loadCourses();
    if (section === "groups") loadGroups();
    if (section === "rewards") loadRewards();
    if (section === "orders") loadOrders();
    if (section === "books") loadBooks();
    if (section === "ranking") loadRanking();
    if (section === "podcasts") loadPodcasts();
    if (section === "trainings") loadTrainings();
    if (section === "exams") loadExams();

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

        updateAdministratorAccess(data);

    } catch (error) {

        console.error(
            "Admin profile error:",
            error
        );

    }
}


/* ============================================================
   ADMINISTRATOR MANAGEMENT
   ============================================================ */

function updateAdministratorAccess(admin) {

    const nav = document.getElementById(
        "administratorNav"
    );

    const navSection = document.getElementById(
        "administratorNavSection"
    );

    const isSuperadmin =
        admin?.is_superadmin === true;

    if (nav) {
        nav.hidden = !isSuperadmin;
    }

    if (navSection) {
        navSection.hidden = !isSuperadmin;
    }

    if (
        !isSuperadmin &&
        window.location.hash === "#administrators"
    ) {
        openSection("dashboard");
    }
}


function initAdministratorManagement() {

    const form = document.getElementById(
        "administratorCreateForm"
    );

    const phoneInput = document.getElementById(
        "administratorPhone"
    );

    const passwordInput = document.getElementById(
        "administratorPassword"
    );

    if (!form) return;

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const fullName =
                document.getElementById(
                    "administratorFullName"
                )?.value
                .trim();

            let phone =
                phoneInput?.value
                .trim()
                .replace(/[\s()-]/g, "");

            const password =
                passwordInput?.value || "";

            if (!fullName || fullName.length < 2) {
                showToast(
                    "To‘liq ismni to‘g‘ri kiriting.",
                    "error"
                );
                return;
            }

            if (phone.startsWith("+")) {
                phone = phone.slice(1);
            }

            if (
                !/^998\d{9}$/.test(phone)
            ) {
                showToast(
                    "Telefon raqamni +998901234567 yoki 998901234567 ko‘rinishida kiriting.",
                    "error"
                );
                phoneInput?.focus();
                return;
            }

            if (
                password.length < 8
            ) {
                showToast(
                    "Parol kamida 8 ta belgidan iborat bo‘lishi kerak.",
                    "error"
                );
                passwordInput?.focus();
                return;
            }

            const button =
                document.getElementById(
                    "administratorSubmit"
                );

            if (button) {
                button.disabled = true;
                button.textContent =
                    "Yaratilmoqda...";
            }

            try {

                const data =
                    await apiRequest(
                        "/admins/create",
                        {
                            method: "POST",
                            body: JSON.stringify({
                                full_name: fullName,
                                phone,
                                password
                            })
                        }
                    );

                showToast(
                    data?.message ||
                    "Yangi administrator yaratildi.",
                    "success"
                );

                form.reset();

            } catch (error) {

                showToast(
                    error.message ||
                    "Administrator yaratishda xatolik yuz berdi.",
                    "error"
                );

            } finally {

                if (button) {
                    button.disabled = false;
                    button.textContent =
                        "Administrator yaratish";
                }
            }
        }
    );
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

            const isOpen =
                sidebar.classList.toggle("open");

            button.setAttribute(
                "aria-expanded",
                String(isOpen)
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
    sessionStorage.removeItem(SESSION_KEY);

    window.location.replace("login.html");
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
                `/admin/students/${studentId}/profile`
            );


        showStudentFullProfile(data);

    } catch (error) {

        showToast(
            error.message ||
            "O‘quvchi profilini olishda xatolik",
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
                method: "PUT"
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
   ADMIN MODULES — EDUCATION / REWARDS
   ============================================================ */

function moduleLoading(textValue) {
    return '<div class="module-loading"><div class="module-spinner"></div><span>' +
        escapeHtml(textValue || "Yuklanmoqda...") +
        '</span></div>';
}

function moduleTable(headers, rows) {
    return '<div class="module-table-wrap"><table class="module-table"><thead><tr>' +
        headers.map(h => '<th>' + escapeHtml(h) + '</th>').join("") +
        '</tr></thead><tbody>' + rows.join("") + '</tbody></table></div>';
}

function actionButton(label, action, cls) {
    return '<button type="button" class="module-action-btn ' +
        escapeHtml(cls || "") + '" onclick="' +
        escapeHtml(action) + '">' + escapeHtml(label) + '</button>';
}

function showInfoModal(title, body) {
    document.getElementById("moduleInfoModal")?.remove();

    const modal = document.createElement("div");
    modal.id = "moduleInfoModal";
    modal.className = "admin-modal-overlay";

    modal.innerHTML =
        '<div class="admin-modal">' +
        '<button type="button" class="admin-modal-close" aria-label="Yopish">×</button>' +
        '<div class="modal-eyebrow">AXSIKENT IT / ADMIN</div>' +
        '<h2>' + escapeHtml(title) + '</h2>' +
        '<div class="admin-detail-body">' + body + '</div>' +
        '</div>';

    document.body.appendChild(modal);

    modal.querySelector(".admin-modal-close")?.addEventListener(
        "click",
        () => modal.remove()
    );

    modal.addEventListener("click", event => {
        if (event.target === modal) modal.remove();
    });
}

function asArray(data, keys) {
    if (Array.isArray(data)) return data;

    for (const key of (keys || [])) {
        if (Array.isArray(data?.[key])) return data[key];
    }

    return [];
}

function formatDate(value) {
    if (!value) return "—";

    try {
        return new Date(value).toLocaleString("uz-UZ");
    } catch {
        return String(value);
    }
}

/* ============================================================
   STUDENTS — FULL PROFILE
   ============================================================ */

async function viewStudent(id) {
    try {
        const data = await apiRequest(
            "/admin/students/" + Number(id) + "/profile"
        );

        showStudentFullProfile(data);
    } catch (error) {
        showToast(error.message || "O‘quvchi profili yuklanmadi", "error");
    }
}

function showStudentFullProfile(data) {
    const student = data?.student || {};
    const courses = asArray(data, ["courses"]);
    const groups = asArray(data, ["groups"]);
    const grades = asArray(data, ["grades"]);
    const homework = asArray(data, ["homework"]);
    const attendance = data?.attendance || {};
    const game = data?.gamification || {};

    const active = student.is_active !== false;

    let courseHtml = courses.length
        ? courses.map(item =>
            '<div class="admin-detail-list-item">' +
            '<strong>' + escapeHtml(item.name || "—") + '</strong>' +
            '<span>' + (item.progress ?? 0) + '%</span>' +
            '</div>'
        ).join("")
        : '<p>Biriktirilgan kurs yo‘q.</p>';

    let groupHtml = groups.length
        ? groups.map(item =>
            '<div class="admin-detail-list-item">' +
            '<strong>' + escapeHtml(item.name || "—") + '</strong>' +
            '<span>' + escapeHtml(item.course || "—") + '</span>' +
            '</div>'
        ).join("")
        : '<p>Guruh mavjud emas.</p>';

    let gradeHtml = grades.length
        ? grades.slice(0, 10).map(item =>
            '<div class="admin-detail-list-item">' +
            '<strong>' + escapeHtml(item.title || "Baholash") + '</strong>' +
            '<span>' + (item.score ?? 0) + '/' + (item.max_score ?? 0) + '</span>' +
            '</div>'
        ).join("")
        : '<p>Baholar yo‘q.</p>';

    let homeworkHtml = homework.length
        ? homework.slice(0, 10).map(item =>
            '<div class="admin-detail-list-item">' +
            '<strong>' + escapeHtml(item.title || "Uy vazifasi") + '</strong>' +
            '<span>' + escapeHtml(item.status || "—") +
            (item.score !== null && item.score !== undefined
                ? " · " + item.score + " ball"
                : "") +
            '</span></div>'
        ).join("")
        : '<p>Uy vazifalari yo‘q.</p>';

    showInfoModal(
        student.full_name || "O‘quvchi profili",
        '<div class="admin-detail-grid">' +
        '<div><small>ID</small><strong>#' + (student.id ?? "—") + '</strong></div>' +
        '<div><small>Telefon</small><strong>' + escapeHtml(student.phone || "—") + '</strong></div>' +
        '<div><small>Holat</small><strong>' + (active ? "Faol" : "Nofaol") + '</strong></div>' +
        '<div><small>Daraja</small><strong>' + (game.level ?? 1) + '</strong></div>' +
        '<div><small>Coin</small><strong>' + (game.coins ?? 0) + '</strong></div>' +
        '<div><small>Crystal</small><strong>' + (game.crystals ?? 0) + '</strong></div>' +
        '<div><small>XP</small><strong>' + (game.xp ?? 0) + '</strong></div>' +
        '<div><small>Davomat</small><strong>' + (attendance.rate ?? 0) + '%</strong></div>' +
        '</div>' +

        '<div class="admin-detail-block"><h3>Kurslar</h3>' +
        courseHtml + '</div>' +

        '<div class="admin-detail-block"><h3>Guruhlar</h3>' +
        groupHtml + '</div>' +

        '<div class="admin-detail-block"><h3>Davomat</h3>' +
        '<p>Jami: ' + (attendance.total ?? 0) +
        ' · Kelgan: ' + (attendance.present ?? 0) +
        ' · Kelmagan: ' + (attendance.absent ?? 0) +
        ' · Kechikkan: ' + (attendance.late ?? 0) + '</p></div>' +

        '<div class="admin-detail-block"><h3>Baholar</h3>' +
        gradeHtml + '</div>' +

        '<div class="admin-detail-block"><h3>Uy vazifalari</h3>' +
        homeworkHtml + '</div>' +

        '<div class="modal-actions">' +
        actionButton(
            active ? "Bloklash" : "Faollashtirish",
            "toggleStudentStatus(" + Number(student.id) + "," + active + ");document.getElementById('moduleInfoModal')?.remove()",
            active ? "danger" : "success"
        ) +
        '</div>'
    );
}

/* ============================================================
   LEADS / ARIZALAR
   ============================================================ */

async function loadLeads() {
    const box = document.getElementById("leadsContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Arizalar yuklanmoqda...");

    try {
        const stats = await apiRequest("/admin/leads/stats/summary");
        const data = await apiRequest("/admin/leads/");
        const leads = asArray(data, ["leads", "items", "data"]);

        let html =
            '<div class="homework-stats">' +
            '<div class="homework-stat-card"><span>📋</span><div><small>Jami</small><strong>' + (stats?.total ?? leads.length) + '</strong></div></div>' +
            '<div class="homework-stat-card"><span>🆕</span><div><small>Yangi</small><strong>' + (stats?.new ?? 0) + '</strong></div></div>' +
            '<div class="homework-stat-card"><span>📞</span><div><small>Bog‘langan</small><strong>' + (stats?.contacted ?? 0) + '</strong></div></div>' +
            '<div class="homework-stat-card"><span>✅</span><div><small>Qabul qilingan</small><strong>' + (stats?.enrolled ?? 0) + '</strong></div></div>' +
            '</div>';

        if (!leads.length) {
            html += '<div class="module-empty"><h3>Arizalar yo‘q</h3><p>Hozircha yangi ariza mavjud emas.</p></div>';
            box.innerHTML = html;
            return;
        }

        html += moduleTable(
            ["ISM", "TELEFON", "KURS", "YOSH", "VAQT", "STATUS", "AMAL"],
            leads.map(lead =>
                '<tr>' +
                '<td><strong>' + escapeHtml(lead.full_name || "—") + '</strong><small>#' + Number(lead.id) + ' · ' + escapeHtml(formatDate(lead.created_at)) + '</small></td>' +
                '<td>' + escapeHtml(lead.phone || "—") + '</td>' +
                '<td>' + escapeHtml(lead.interested_course || "—") + '</td>' +
                '<td>' + (lead.age ?? "—") + '</td>' +
                '<td>' + escapeHtml(lead.preferred_time || "—") + '</td>' +
                '<td><select class="module-status-select" onchange="updateLeadStatus(' + Number(lead.id) + ',this.value)">' +
                '<option value="new"' + (lead.status === "new" ? " selected" : "") + '>Yangi</option>' +
                '<option value="contacted"' + (lead.status === "contacted" ? " selected" : "") + '>Bog‘langan</option>' +
                '<option value="enrolled"' + (lead.status === "enrolled" ? " selected" : "") + '>Qabul qilingan</option>' +
                '<option value="rejected"' + (lead.status === "rejected" ? " selected" : "") + '>Rad etilgan</option>' +
                '</select></td>' +
                '<td>' +
                '<div class="lead-action-group">' +
                '<button type="button" class="lead-view-btn" data-lead-action="view" data-lead-id="' + Number(lead.id) + '">' +
                '<span class="lead-view-icon">⌕</span> Ko‘rish</button>' +
                (lead.status === "new" || lead.status === "contacted"
                    ? '<button type="button" class="lead-approve-btn" data-lead-action="approve" data-lead-id="' + Number(lead.id) + '">✓ Tasdiqlash</button>'
                    : '') +
                '<button type="button" class="lead-delete-btn" data-lead-action="delete" data-lead-id="' + Number(lead.id) + '">O‘chirish</button>' +
                '</div>' +
                '</td></tr>'
            )
        );

        box.innerHTML = html;
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

function initLeadActions() {
    if (window.__axsikentLeadActionsReady) return;
    window.__axsikentLeadActionsReady = true;

    document.addEventListener("click", event => {
        const button = event.target.closest("[data-lead-action]");
        if (!button) return;

        event.preventDefault();
        event.stopPropagation();

        const id = Number(button.dataset.leadId);
        const action = button.dataset.leadAction;

        if (!Number.isInteger(id) || id <= 0) {
            showToast("Ariza ID noto‘g‘ri.", "error");
            return;
        }

        if (action === "view") viewLead(id);
        if (action === "approve") approveLead(id);
        if (action === "delete") deleteLead(id);
    });
}

async function viewLead(id) {
    try {
        const lead = await apiRequest("/admin/leads/" + Number(id));
        const statusText = {
            new: "Yangi",
            contacted: "Bog‘langan",
            enrolled: "Tasdiqlangan",
            rejected: "Rad etilgan"
        }[lead.status] || lead.status || "—";

        showInfoModal(
            "O‘quvchi arizasi",
            '<div class="lead-detail-card">' +
            '<div class="lead-detail-hero">' +
            '<div class="lead-detail-avatar">' + escapeHtml((lead.full_name || "O").trim().charAt(0).toUpperCase()) + '</div>' +
            '<div><span class="lead-detail-kicker">YANGI ARIZA</span><h3>' + escapeHtml(lead.full_name || "—") + '</h3><span class="lead-detail-status">' + escapeHtml(statusText) + '</span></div>' +
            '</div>' +
            '<div class="lead-detail-grid">' +
            '<div><span>TELEFON</span><strong>' + escapeHtml(lead.phone || "—") + '</strong></div>' +
            '<div><span>KURS</span><strong>' + escapeHtml(lead.interested_course || "—") + '</strong></div>' +
            '<div><span>QULAY VAQT</span><strong>' + escapeHtml(lead.preferred_time || "—") + '</strong></div>' +
            '<div><span>YOSH</span><strong>' + (lead.age ?? "—") + '</strong></div>' +
            '</div>' +
            '<div class="lead-detail-extra">' +
            '<div><span>OLDINGI IT KURSI</span><strong>' + escapeHtml(lead.previous_it_course || "—") + '</strong></div>' +
            '<div><span>ARIZA YUBORILGAN</span><strong>' + escapeHtml(formatDate(lead.created_at)) + '</strong></div>' +
            '</div>' +
            '<div class="lead-detail-note"><span>QO‘SHIMCHA IZOH</span><p>' + escapeHtml(lead.comment || "Izoh qoldirilmagan.") + '</p></div>' +
            '<div class="lead-detail-actions">' +
            ((lead.status === "new" || lead.status === "contacted") ? '<button type="button" class="lead-approve-btn lead-approve-large" onclick="approveLead(' + Number(lead.id) + ')">✓ O‘quvchini tasdiqlash</button>' : '') +
            '<button type="button" class="lead-secondary-btn" onclick="editLeadComment(' + Number(lead.id) + ')">Izohni o‘zgartirish</button>' +
            '</div>' +
            '</div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function approveLead(id) {
    try {
        const data = await apiRequest("/admin/leads/" + Number(id) + "/status", {
            method: "PUT",
            body: JSON.stringify({ status: "enrolled" })
        });

        document.getElementById("moduleInfoModal")?.remove();
        showToast("O‘quvchi tasdiqlandi. Student akkaunti faollashtirildi.");
        await loadLeads();
        await loadDashboard();
    } catch (error) {
        showToast(error.message || "O‘quvchini tasdiqlashda xatolik", "error");
    }
}

async function updateLeadStatus(id, status) {
    if (!status) return;

    try {
        await apiRequest("/admin/leads/" + Number(id) + "/status", {
            method: "PUT",
            body: JSON.stringify({ status: status })
        });

        showToast("Ariza statusi yangilandi");
        await loadLeads();
        await loadDashboard();
    } catch (error) {
        showToast(error.message, "error");
        await loadLeads();
    }
}

async function editLeadComment(id) {
    try {
        const lead = await apiRequest("/admin/leads/" + Number(id));
        const comment = window.prompt(
            "Ariza izohi:",
            lead.comment || ""
        );

        if (comment === null) return;

        await apiRequest("/admin/leads/" + Number(id) + "/comment", {
            method: "PUT",
            body: JSON.stringify({ comment: comment })
        });

        showToast("Ariza izohi yangilandi");
        document.getElementById("moduleInfoModal")?.remove();
        await loadLeads();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function deleteLead(id) {
    if (!window.confirm("Bu arizani o‘chirishni tasdiqlaysizmi?")) return;

    try {
        await apiRequest("/admin/leads/" + Number(id), {
            method: "DELETE"
        });

        showToast("Ariza o‘chirildi");
        await loadLeads();
        await loadDashboard();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   TEACHERS
   ============================================================ */

async function loadTeachers() {
    const box = document.getElementById("teachersContent");
    if (!box) return;

    box.innerHTML = moduleLoading("O‘qituvchilar yuklanmoqda...");

    try {
        const data = await apiRequest("/admin/teachers/");
        const items = asArray(data, ["teachers", "items", "data"]);

        box.innerHTML = items.length
            ? moduleTable(
                ["O‘QITUVCHI", "FAN", "GURUHLAR", "HOLAT", "AMAL"],
                items.map(t => {
                    const search = [
                        t.full_name,
                        t.phone,
                        t.subject
                    ].filter(Boolean).join(" ").toLowerCase();

                    return '<tr data-teacher-search="' +
                        escapeHtml(search) + '">' +
                        '<td><strong>' + escapeHtml(t.full_name || "—") +
                        '</strong><small>' + escapeHtml(t.phone || "") +
                        '</small></td>' +
                        '<td>' + escapeHtml(t.subject || "—") + '</td>' +
                        '<td>' + (t.groups_count ?? 0) + '</td>' +
                        '<td><span class="status-badge ' +
                        (t.is_active ? "status-active" : "status-inactive") +
                        '"><span></span>' +
                        (t.is_active ? "Faol" : "Nofaol") +
                        '</span></td>' +
                        '<td>' +
                        actionButton("Ko‘rish", "viewTeacher(" + Number(t.id) + ")") +
                        " " +
                        actionButton(
                            t.is_active ? "Bloklash" : "Faollashtirish",
                            "toggleTeacher(" + Number(t.id) + "," +
                            Boolean(t.is_active) + ")",
                            t.is_active ? "danger" : "success"
                        ) +
                        '</td></tr>';
                })
            )
            : '<div class="module-empty"><h3>O‘qituvchilar yo‘q</h3>' +
              '<p>Tizimda hozircha o‘qituvchi topilmadi.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

function filterTeachers() {
    const q = (
        document.getElementById("teacherSearch")?.value || ""
    ).trim().toLowerCase();

    document.querySelectorAll("[data-teacher-search]").forEach(row => {
        row.style.display =
            !q || row.dataset.teacherSearch.includes(q) ? "" : "none";
    });
}

async function viewTeacher(id) {
    try {
        const data = await apiRequest(
            "/admin/teachers/" + Number(id)
        );

        const teacher = data?.teacher || {};
        const groups = asArray(data, ["groups"]);

        const groupHtml = groups.length
            ? groups.map(group =>
                '<div class="admin-detail-list-item">' +
                '<strong>' + escapeHtml(group.name || "—") + '</strong>' +
                '<span>' + escapeHtml(group.course?.name || "—") +
                ' · ' + (group.students_count ?? 0) + ' o‘quvchi</span>' +
                '</div>'
            ).join("")
            : "<p>Guruhlar yo‘q.</p>";

        showInfoModal(
            "O‘qituvchi profili",
            '<div class="admin-detail-grid">' +
            '<div><small>Ism</small><strong>' +
            escapeHtml(teacher.full_name || "—") + '</strong></div>' +
            '<div><small>Telefon</small><strong>' +
            escapeHtml(teacher.phone || "—") + '</strong></div>' +
            '<div><small>Fan</small><strong>' +
            escapeHtml(teacher.subject || "—") + '</strong></div>' +
            '<div><small>Holat</small><strong>' +
            (teacher.is_active ? "Faol" : "Nofaol") + '</strong></div>' +
            '</div>' +
            '<div class="admin-detail-block"><h3>Guruhlar</h3>' +
            groupHtml + '</div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function toggleTeacher(id, active) {
    try {
        await apiRequest(
            "/admin/teachers/" + Number(id) + "/" +
            (active ? "deactivate" : "activate"),
            { method: "PUT" }
        );

        showToast(
            active ? "O‘qituvchi deaktiv qilindi" :
            "O‘qituvchi faollashtirildi"
        );

        await loadTeachers();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   COURSES
   ============================================================ */

async function loadCourses() {
    const box = document.getElementById("coursesContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Kurslar yuklanmoqda...");

    try {
        const data = await apiRequest("/admin/courses/");
        const catData = await apiRequest("/admin/courses/categories");

        const items = asArray(data, ["courses", "items", "data"]);
        window.adminCategories = asArray(
            catData,
            ["categories", "items", "data"]
        );

        box.innerHTML = items.length
            ? moduleTable(
                ["KURS", "KATEGORIYA", "YOSH", "DARS", "NARX", "HOLAT", "AMAL"],
                items.map(course =>
                    '<tr>' +
                    '<td><strong>' + escapeHtml(course.name || "—") +
                    '</strong><small>#' + Number(course.id) + '</small></td>' +
                    '<td>' + escapeHtml(course.category?.name || "—") + '</td>' +
                    '<td>' + (course.age_min ?? "—") + "–" +
                    (course.age_max ?? "—") + '</td>' +
                    '<td>' + (course.lesson_minutes ?? "—") + ' daq.</td>' +
                    '<td>' + (course.price_min ?? 0) + "–" +
                    (course.price_max ?? 0) + '</td>' +
                    '<td><span class="status-badge ' +
                    (course.is_active ? "status-active" : "status-inactive") +
                    '"><span></span>' +
                    (course.is_active ? "Faol" : "Nofaol") +
                    '</span></td>' +
                    '<td>' +
                    actionButton("Ko‘rish", "viewCourse(" + Number(course.id) + ")") +
                    " " +
                    actionButton(
                        course.is_active ? "Deaktiv" : "Aktiv",
                        "toggleCourse(" + Number(course.id) + "," +
                        Boolean(course.is_active) + ")",
                        course.is_active ? "danger" : "success"
                    ) +
                    '</td></tr>'
                )
            )
            : '<div class="module-empty"><h3>Kurslar yo‘q</h3>' +
              '<p>Yangi kurs yarating.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

async function viewCourse(id) {
    try {
        const data = await apiRequest(
            "/admin/courses/" + Number(id)
        );

        const course = data?.course || {};
        const modules = asArray(data, ["modules"]);

        const modulesHtml = modules.length
            ? modules.map(module =>
                '<div class="admin-detail-list-item">' +
                '<strong>' + escapeHtml(module.title || "—") + '</strong>' +
                '<span>' + (module.lessons_count ??
                asArray(module, ["lessons"]).length) + ' ta dars</span>' +
                '</div>'
            ).join("")
            : "<p>Modullar yo‘q.</p>";

        showInfoModal(
            "Kurs tafsilotlari",
            '<div class="admin-detail-grid">' +
            '<div><small>Nomi</small><strong>' +
            escapeHtml(course.name || "—") + '</strong></div>' +
            '<div><small>Kategoriya</small><strong>' +
            escapeHtml(course.category?.name || "—") + '</strong></div>' +
            '<div><small>Yosh</small><strong>' +
            (course.age_min ?? "—") + "–" + (course.age_max ?? "—") +
            '</strong></div>' +
            '<div><small>Dars</small><strong>' +
            (course.lesson_minutes ?? "—") + ' daq.</strong></div>' +
            '<div><small>O‘quvchilar</small><strong>' +
            (data?.statistics?.students_count ?? 0) + '</strong></div>' +
            '<div><small>Modullar</small><strong>' +
            (data?.statistics?.modules_count ?? modules.length) + '</strong></div>' +
            '</div>' +
            '<div class="admin-detail-block"><h3>Modullar</h3>' +
            modulesHtml + '</div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function toggleCourse(id, active) {
    try {
        await apiRequest(
            "/admin/courses/" + Number(id) + "/" +
            (active ? "deactivate" : "activate"),
            { method: "PUT" }
        );

        showToast(
            active ? "Kurs deaktiv qilindi" :
            "Kurs faollashtirildi"
        );

        await loadCourses();
        await loadDashboard();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function openCourseCreate() {
    const categories = window.adminCategories || [];

    const categoryText = categories.length
        ? categories.map(c => c.id + " — " + c.name).join("\n")
        : "Kategoriya ma’lumoti topilmadi.";

    const category = window.prompt(
        "Kategoriya ID:\n" + categoryText
    );

    if (category === null) return;

    const name = window.prompt("Kurs nomi:");
    if (!name?.trim()) return;

    const categoryId = Number(category);

    if (!Number.isInteger(categoryId) || categoryId <= 0) {
        showToast("Kategoriya ID noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest("/admin/courses/", {
            method: "POST",
            body: JSON.stringify({
                category_id: categoryId,
                name: name.trim(),
                description: ""
            })
        });

        showToast("Kurs yaratildi");
        await loadCourses();
        await loadDashboard();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   GROUPS
   ============================================================ */

async function loadGroups() {
    const box = document.getElementById("groupsContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Guruhlar yuklanmoqda...");

    try {
        const data = await apiRequest("/admin/groups/");
        const items = asArray(data, ["groups", "items", "data"]);

        box.innerHTML = items.length
            ? moduleTable(
                ["GURUH", "KURS", "O‘QITUVCHI", "O‘QUVCHILAR", "HOLAT", "AMAL"],
                items.map(group =>
                    '<tr>' +
                    '<td><strong>' + escapeHtml(group.name || "—") +
                    '</strong><small>#' + Number(group.id) + '</small></td>' +
                    '<td>' + escapeHtml(group.course?.name || "—") + '</td>' +
                    '<td>' + escapeHtml(group.teacher?.full_name || "—") + '</td>' +
                    '<td>' + (group.students_count ?? 0) + "/" +
                    (group.capacity ?? 0) + '</td>' +
                    '<td><span class="status-badge ' +
                    (group.is_active ? "status-active" : "status-inactive") +
                    '"><span></span>' +
                    (group.is_active ? "Faol" : "Nofaol") +
                    '</span></td>' +
                    '<td>' +
                    actionButton("Ko‘rish", "viewGroup(" + Number(group.id) + ")") +
                    " " +
                    actionButton(
                        group.is_active ? "Deaktiv" : "Aktiv",
                        "toggleGroup(" + Number(group.id) + "," +
                        Boolean(group.is_active) + ")",
                        group.is_active ? "danger" : "success"
                    ) +
                    '</td></tr>'
                )
            )
            : '<div class="module-empty"><h3>Guruhlar yo‘q</h3>' +
              '<p>Yangi guruh yarating.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

async function viewGroup(id) {
    try {
        const data = await apiRequest(
            "/admin/groups/" + Number(id)
        );

        const group = data?.group || {};
        const students = asArray(data, ["students"]);

        const studentsHtml = students.length
            ? students.map(student =>
                '<div class="admin-detail-list-item">' +
                '<strong>' + escapeHtml(student.full_name || "—") + '</strong>' +
                '<span>#' + Number(student.id) + ' · ' +
                escapeHtml(student.phone || "—") + '</span>' +
                '</div>'
            ).join("")
            : "<p>Guruhda o‘quvchi yo‘q.</p>";

        showInfoModal(
            "Guruh tafsilotlari",
            '<div class="admin-detail-grid">' +
            '<div><small>Guruh</small><strong>' +
            escapeHtml(group.name || "—") + '</strong></div>' +
            '<div><small>Kurs</small><strong>' +
            escapeHtml(data?.course?.name || "—") + '</strong></div>' +
            '<div><small>O‘qituvchi</small><strong>' +
            escapeHtml(data?.teacher?.full_name || "—") + '</strong></div>' +
            '<div><small>Xona</small><strong>' +
            escapeHtml(group.room || "—") + '</strong></div>' +
            '<div><small>Sig‘im</small><strong>' +
            (data?.statistics?.students_count ?? students.length) + "/" +
            (group.capacity ?? 0) + '</strong></div>' +
            '</div>' +
            '<div class="admin-detail-block"><h3>O‘quvchilar</h3>' +
            studentsHtml + '</div>' +
            '<div class="modal-actions">' +
            actionButton(
                "O‘quvchi qo‘shish",
                "addStudentToGroupPrompt(" + Number(group.id) + ")"
            ) +
            '</div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function addStudentToGroupPrompt(groupId) {
    const value = window.prompt("O‘quvchi ID:");
    if (value === null) return;

    const studentId = Number(value);

    if (!Number.isInteger(studentId) || studentId <= 0) {
        showToast("O‘quvchi ID noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest(
            "/admin/groups/" + Number(groupId) +
            "/students/" + studentId,
            { method: "POST" }
        );

        showToast("O‘quvchi guruhga qo‘shildi");
        document.getElementById("moduleInfoModal")?.remove();
        await loadGroups();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function toggleGroup(id, active) {
    try {
        await apiRequest(
            "/admin/groups/" + Number(id) + "/" +
            (active ? "deactivate" : "activate"),
            { method: "PUT" }
        );

        showToast(
            active ? "Guruh deaktiv qilindi" :
            "Guruh faollashtirildi"
        );

        await loadGroups();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function openGroupCreate() {
    const name = window.prompt("Guruh nomi:");
    if (!name?.trim()) return;

    const course = window.prompt("Kurs ID:");
    if (course === null) return;

    const teacher = window.prompt("O‘qituvchi ID:");
    if (teacher === null) return;

    const courseId = Number(course);
    const teacherId = Number(teacher);

    if (
        !Number.isInteger(courseId) ||
        !Number.isInteger(teacherId) ||
        courseId <= 0 ||
        teacherId <= 0
    ) {
        showToast("Kurs yoki o‘qituvchi ID noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest("/admin/groups/", {
            method: "POST",
            body: JSON.stringify({
                name: name.trim(),
                course_id: courseId,
                teacher_id: teacherId,
                capacity: 15,
                status: "active"
            })
        });

        showToast("Guruh yaratildi");
        await loadGroups();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   REWARDS — PRODUCTS / RULES / TRANSACTIONS
   ============================================================ */

async function loadRewards() {
    const box = document.getElementById("rewardsContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Mukofotlar yuklanmoqda...");

    try {
        const productData = await apiRequest("/admin/shop/products");
        const ruleData = await apiRequest("/admin/shop/rules");
        const transactionData = await apiRequest("/admin/shop/transactions");

        const products = asArray(productData, ["products", "items", "data"]);
        const rules = asArray(ruleData, ["rules", "items", "data"]);
        const transactions = asArray(
            transactionData,
            ["transactions", "items", "data"]
        );

        window.adminRules = rules;

        let html = "";

        html += '<div class="admin-detail-block"><h3>Mukofot mahsulotlari</h3>';

        if (products.length) {
            html += moduleTable(
                ["MUKOFOT", "COIN", "CRYSTAL", "STOCK", "HOLAT", "AMAL"],
                products.map(product =>
                    '<tr>' +
                    '<td><strong>' + escapeHtml(product.name || "—") +
                    '</strong><small>#' + Number(product.id) + '</small></td>' +
                    '<td>' + (product.coin_price ?? 0) + '</td>' +
                    '<td>' + (product.crystal_price ?? 0) + '</td>' +
                    '<td>' + (product.stock ?? 0) + '</td>' +
                    '<td><span class="status-badge ' +
                    (product.is_active ? "status-active" : "status-inactive") +
                    '"><span></span>' +
                    (product.is_active ? "Faol" : "Nofaol") +
                    '</span></td>' +
                    '<td>' +
                    actionButton("Ko‘rish", "viewProduct(" + Number(product.id) + ")") +
                    " " +
                    actionButton(
                        "Tahrirlash",
                        "editProduct(" + Number(product.id) + ")"
                    ) +
                    " " +
                    actionButton(
                        product.is_active ? "Deaktiv" : "Aktiv",
                        "toggleProduct(" + Number(product.id) + "," +
                        Boolean(product.is_active) + ")",
                        product.is_active ? "danger" : "success"
                    ) +
                    " " +
                    actionButton(
                        "O‘chirish",
                        "deleteProduct(" + Number(product.id) + ")",
                        "danger"
                    ) +
                    '</td></tr>'
                )
            );
        } else {
            html += '<div class="module-empty"><h3>Mukofotlar yo‘q</h3>' +
                '<p>Yangi mukofot yarating.</p></div>';
        }

        html += '</div>';

        html += '<div class="admin-detail-block"><h3>Reward qoidalari</h3>';

        if (rules.length) {
            html += moduleTable(
                ["QOIDA", "HARAKAT", "MUKOFOT", "MIQDOR", "HOLAT", "AMAL"],
                rules.map(rule =>
                    '<tr>' +
                    '<td><strong>' + escapeHtml(rule.name || "—") +
                    '</strong><small>#' + Number(rule.id) + '</small></td>' +
                    '<td>' + escapeHtml(rule.action_type || "—") + '</td>' +
                    '<td>' + escapeHtml(rule.reward_type || "—") + '</td>' +
                    '<td>' + (rule.reward_amount ?? 0) + '</td>' +
                    '<td>' + (rule.is_active ? "Faol" : "Nofaol") + '</td>' +
                    '<td>' +
                    actionButton(
                        rule.is_active ? "Deaktiv" : "Aktiv",
                        "toggleRule(" + Number(rule.id) + "," +
                        Boolean(rule.is_active) + ")",
                        rule.is_active ? "danger" : "success"
                    ) +
                    " " +
                    actionButton(
                        "O‘chirish",
                        "deleteRule(" + Number(rule.id) + ")",
                        "danger"
                    ) +
                    '</td></tr>'
                )
            );
        } else {
            html += '<div class="module-empty"><p>Reward qoidalari yo‘q.</p></div>';
        }

        html += '<div class="modal-actions">' +
            actionButton("＋ Qoida qo‘shish", "openRuleCreate()") +
            '</div></div>';

        html += '<div class="admin-detail-block"><h3>Reward tranzaksiyalari</h3>';

        if (transactions.length) {
            html += moduleTable(
                ["ID", "O‘QUVCHI", "TURI", "MIQDOR", "SABAB", "SANA"],
                transactions.slice(0, 30).map(item =>
                    '<tr>' +
                    '<td>#' + Number(item.id) + '</td>' +
                    '<td>#' + Number(item.student_id) + '</td>' +
                    '<td>' + escapeHtml(item.reward_type || "—") + '</td>' +
                    '<td>' + (item.amount ?? 0) + '</td>' +
                    '<td>' + escapeHtml(item.reason || "—") + '</td>' +
                    '<td>' + escapeHtml(formatDate(item.created_at)) + '</td>' +
                    '</tr>'
                )
            );
        } else {
            html += '<div class="module-empty"><p>Tranzaksiyalar yo‘q.</p></div>';
        }

        html += '</div>';

        box.innerHTML = html;
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

async function viewProduct(id) {
    try {
        const product = await apiRequest(
            "/admin/shop/products/" + Number(id)
        );

        showInfoModal(
            "Mukofot tafsilotlari",
            '<div class="admin-detail-grid">' +
            '<div><small>Nomi</small><strong>' +
            escapeHtml(product.name || "—") + '</strong></div>' +
            '<div><small>Coin</small><strong>' +
            (product.coin_price ?? 0) + '</strong></div>' +
            '<div><small>Crystal</small><strong>' +
            (product.crystal_price ?? 0) + '</strong></div>' +
            '<div><small>Stock</small><strong>' +
            (product.stock ?? 0) + '</strong></div>' +
            '<div><small>Holat</small><strong>' +
            (product.is_active ? "Faol" : "Nofaol") + '</strong></div>' +
            '</div>' +
            '<div class="admin-detail-block"><h3>Tavsif</h3><p>' +
            escapeHtml(product.description || "Tavsif yo‘q.") +
            '</p></div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function editProduct(id) {
    try {
        const product = await apiRequest(
            "/admin/shop/products/" + Number(id)
        );

        const name = window.prompt(
            "Mukofot nomi:",
            product.name || ""
        );
        if (name === null) return;

        const coin = window.prompt(
            "Coin narxi:",
            String(product.coin_price ?? 0)
        );
        if (coin === null) return;

        const crystal = window.prompt(
            "Crystal narxi:",
            String(product.crystal_price ?? 0)
        );
        if (crystal === null) return;

        const stock = window.prompt(
            "Stock:",
            String(product.stock ?? 0)
        );
        if (stock === null) return;

        await apiRequest(
            "/admin/shop/products/" + Number(id),
            {
                method: "PUT",
                body: JSON.stringify({
                    name: name.trim(),
                    description: product.description || "",
                    image_url: product.image_url || "",
                    coin_price: Number(coin),
                    crystal_price: Number(crystal),
                    stock: Number(stock)
                })
            }
        );

        showToast("Mukofot yangilandi");
        await loadRewards();
        await loadShopStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function toggleProduct(id, active) {
    try {
        await apiRequest(
            "/admin/shop/products/" + Number(id) + "/" +
            (active ? "deactivate" : "activate"),
            { method: "PUT" }
        );

        showToast(
            active ? "Mukofot deaktiv qilindi" :
            "Mukofot faollashtirildi"
        );

        await loadRewards();
        await loadShopStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function deleteProduct(id) {
    if (!window.confirm("Bu mukofotni o‘chirishni tasdiqlaysizmi?")) {
        return;
    }

    try {
        await apiRequest(
            "/admin/shop/products/" + Number(id),
            { method: "DELETE" }
        );

        showToast("Mukofot o‘chirildi");
        await loadRewards();
        await loadShopStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function openProductCreate() {
    const name = window.prompt("Mukofot nomi:");
    if (!name?.trim()) return;

    const coin = window.prompt("Coin narxi:", "0");
    if (coin === null) return;

    const crystal = window.prompt("Crystal narxi:", "0");
    if (crystal === null) return;

    const stock = window.prompt("Stock:", "0");
    if (stock === null) return;

    const coinValue = Number(coin);
    const crystalValue = Number(crystal);
    const stockValue = Number(stock);

    if (
        !Number.isInteger(coinValue) || coinValue < 0 ||
        !Number.isInteger(crystalValue) || crystalValue < 0 ||
        !Number.isInteger(stockValue) || stockValue < 0
    ) {
        showToast("Narx yoki stock noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest("/admin/shop/products", {
            method: "POST",
            body: JSON.stringify({
                name: name.trim(),
                description: "",
                image_url: "",
                coin_price: coinValue,
                crystal_price: crystalValue,
                stock: stockValue
            })
        });

        showToast("Mukofot qo‘shildi");
        await loadRewards();
        await loadShopStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function openRuleCreate() {
    const name = window.prompt("Qoida nomi:");
    if (!name?.trim()) return;

    const actionType = window.prompt(
        "Action type:",
        "homework_completed"
    );
    if (!actionType?.trim()) return;

    const rewardType = window.prompt(
        "Reward type: coin yoki crystal",
        "coin"
    );
    if (!rewardType?.trim()) return;

    const amount = window.prompt(
        "Mukofot miqdori:",
        "10"
    );
    if (amount === null) return;

    const amountValue = Number(amount);

    if (
        !Number.isInteger(amountValue) ||
        amountValue < 0 ||
        !["coin", "crystal"].includes(
            rewardType.trim().toLowerCase()
        )
    ) {
        showToast("Reward qoidasi ma’lumotlari noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest("/admin/shop/rules", {
            method: "POST",
            body: JSON.stringify({
                name: name.trim(),
                description: "",
                action_type: actionType.trim(),
                reward_type: rewardType.trim().toLowerCase(),
                reward_amount: amountValue
            })
        });

        showToast("Reward qoidasi yaratildi");
        await loadRewards();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function toggleRule(id, active) {
    try {
        await apiRequest(
            "/admin/shop/rules/" + Number(id) + "/" +
            (active ? "deactivate" : "activate"),
            { method: "PUT" }
        );

        showToast(
            active ? "Reward qoidasi deaktiv qilindi" :
            "Reward qoidasi faollashtirildi"
        );

        await loadRewards();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function deleteRule(id) {
    if (!window.confirm("Bu reward qoidasini o‘chirishni tasdiqlaysizmi?")) {
        return;
    }

    try {
        await apiRequest(
            "/admin/shop/rules/" + Number(id),
            { method: "DELETE" }
        );

        showToast("Reward qoidasi o‘chirildi");
        await loadRewards();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   ORDERS
   ============================================================ */

async function loadOrders() {
    const box = document.getElementById("ordersContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Buyurtmalar yuklanmoqda...");

    try {
        const data = await apiRequest("/admin/shop/orders");
        const items = asArray(data, ["orders", "items", "data"]);

        box.innerHTML = items.length
            ? moduleTable(
                ["ID", "O‘QUVCHI", "MAHSULOT", "MIQDOR", "SARF", "STATUS", "AMAL"],
                items.map(order =>
                    '<tr>' +
                    '<td>#' + Number(order.id) + '</td>' +
                    '<td>#' + Number(order.student_id) + '</td>' +
                    '<td>' + escapeHtml(order.product_name || "—") + '</td>' +
                    '<td>' + (order.quantity ?? 0) + '</td>' +
                    '<td>' + (order.coin_spent ?? 0) +
                    ' coin / ' + (order.crystal_spent ?? 0) + ' crystal</td>' +
                    '<td>' + escapeHtml(order.status || "—") + '</td>' +
                    '<td>' +
                    '<select class="module-status-select" onchange="updateOrderStatus(' +
                    Number(order.id) + ',this.value)">' +
                    '<option value="">Status</option>' +
                    '<option value="pending">pending</option>' +
                    '<option value="processing">processing</option>' +
                    '<option value="completed">completed</option>' +
                    '<option value="cancelled">cancelled</option>' +
                    '</select> ' +
                    actionButton("Ko‘rish", "viewOrder(" + Number(order.id) + ")") +
                    '</td></tr>'
                )
            )
            : '<div class="module-empty"><h3>Buyurtmalar yo‘q</h3>' +
              '<p>Hozircha buyurtma mavjud emas.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

async function updateOrderStatus(id, status) {
    if (!status) return;

    try {
        await apiRequest(
            "/admin/shop/orders/" + Number(id) + "/status",
            {
                method: "PUT",
                body: JSON.stringify({ status })
            }
        );

        showToast("Buyurtma statusi yangilandi");
        await loadOrders();
        await loadShopStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function viewOrder(id) {
    try {
        const order = await apiRequest(
            "/admin/shop/orders/" + Number(id)
        );

        showInfoModal(
            "Buyurtma tafsilotlari",
            '<div class="admin-detail-grid">' +
            '<div><small>ID</small><strong>#' +
            Number(order.id) + '</strong></div>' +
            '<div><small>O‘quvchi</small><strong>#' +
            Number(order.student_id) + '</strong></div>' +
            '<div><small>Mahsulot</small><strong>' +
            escapeHtml(order.product_name || "—") + '</strong></div>' +
            '<div><small>Miqdor</small><strong>' +
            (order.quantity ?? 0) + '</strong></div>' +
            '<div><small>Coin</small><strong>' +
            (order.coin_spent ?? 0) + '</strong></div>' +
            '<div><small>Crystal</small><strong>' +
            (order.crystal_spent ?? 0) + '</strong></div>' +
            '<div><small>Status</small><strong>' +
            escapeHtml(order.status || "—") + '</strong></div>' +
            '</div>'
        );
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   BOOKS
   ============================================================ */

async function loadBooks() {
    const box = document.getElementById("booksContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Kitoblar yuklanmoqda...");

    try {
        const data = await apiRequest("/admin/books");
        const items = asArray(data, ["books", "items", "data"]);

        box.innerHTML = items.length
            ? moduleTable(
                ["KITOB", "NARX", "COIN", "STOCK", "HOLAT"],
                items.map(book =>
                    '<tr>' +
                    '<td><strong>' + escapeHtml(book.title || "—") +
                    '</strong><small>#' + Number(book.id) + '</small></td>' +
                    '<td>' + (book.price ?? 0) + '</td>' +
                    '<td>' + (book.coin_price ?? 0) + '</td>' +
                    '<td>' + (book.stock ?? 0) + '</td>' +
                    '<td>' + (book.is_active ? "Faol" : "Nofaol") + '</td>' +
                    '</tr>'
                )
            )
            : '<div class="module-empty"><h3>Kitoblar yo‘q</h3>' +
              '<p>Yangi kitob qo‘shishingiz mumkin.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}

async function openBookCreate() {
    const title = window.prompt("Kitob nomi:");
    if (!title?.trim()) return;

    const price = window.prompt("Narxi:", "0");
    if (price === null) return;

    const coin = window.prompt("Coin narxi:", "0");
    if (coin === null) return;

    const stock = window.prompt("Stock:", "0");
    if (stock === null) return;

    const priceValue = Number(price);
    const coinValue = Number(coin);
    const stockValue = Number(stock);

    if (
        !Number.isFinite(priceValue) || priceValue < 0 ||
        !Number.isInteger(coinValue) || coinValue < 0 ||
        !Number.isInteger(stockValue) || stockValue < 0
    ) {
        showToast("Kitob narxi yoki stock noto‘g‘ri.", "error");
        return;
    }

    try {
        await apiRequest("/admin/books", {
            method: "POST",
            body: JSON.stringify({
                title: title.trim(),
                description: "",
                image_url: "",
                price: priceValue,
                coin_price: coinValue,
                stock: stockValue
            })
        });

        showToast("Kitob qo‘shildi");
        await loadBooks();
    } catch (error) {
        showToast(error.message, "error");
    }
}

/* ============================================================
   RANKING
   ============================================================ */

async function loadRanking() {
    const box = document.getElementById("rankingContent");
    if (!box) return;

    box.innerHTML = moduleLoading("Reyting yuklanmoqda...");

    try {
        const data = await apiRequest("/students/ranking");
        const items = asArray(
            data,
            ["ranking", "students", "items", "data"]
        );

        box.innerHTML = items.length
            ? moduleTable(
                ["#", "O‘QUVCHI", "BALL"],
                items.map((item, index) =>
                    '<tr>' +
                    '<td>' + (index + 1) + '</td>' +
                    '<td><strong>' +
                    escapeHtml(item.full_name || item.name || "—") +
                    '</strong></td>' +
                    '<td>' +
                    (item.points ?? item.score ??
                    item.total_points ?? 0) +
                    '</td>' +
                    '</tr>'
                )
            )
            : '<div class="module-empty"><h3>Reyting ma’lumoti yo‘q</h3>' +
              '<p>Hozircha ma’lumot mavjud emas.</p></div>';
    } catch (error) {
        box.innerHTML =
            '<div class="module-empty"><h3>Xatolik</h3><p>' +
            escapeHtml(error.message) + '</p></div>';
    }
}


/* ============================================================
   STUDENT CONTENT — PODCASTS / TRAININGS / EXAMS
   ============================================================ */

async function loadPodcasts() {
    const box = document.getElementById("podcastsContent");
    if (!box) return;
    box.innerHTML = moduleLoading("Podcastlar yuklanmoqda...");
    try {
        const items = await apiRequest("/admin/content/podcasts");
        box.innerHTML = items.length
            ? moduleTable(
                ["ID","NOMI","DAVOMI","HOLAT","AMAL"],
                items.map(x =>
                    '<tr><td>#'+Number(x.id)+'</td><td><strong>'+escapeHtml(x.title)+'</strong><small>'+escapeHtml(x.description||"")+'</small></td><td>'+((x.duration_minutes??"—"))+' min</td><td>'+ (x.is_active?"Faol":"Nofaol") +'</td><td><button class="module-action" onclick="togglePodcast('+Number(x.id)+')">'+(x.is_active?"Deaktiv":"Aktivlashtirish")+'</button></td></tr>'
                )
              )
            : '<div class="module-empty"><h3>Podcastlar yo‘q</h3><p>Student panelga audio material qo‘shing.</p></div>';
    } catch(e) {
        box.innerHTML='<div class="module-empty"><h3>Xatolik</h3><p>'+escapeHtml(e.message)+'</p></div>';
    }
}


function openAdminContentForm(title, fields, onSubmit) {
    document.getElementById("adminContentFormModal")?.remove();

    const modal = document.createElement("div");
    modal.id = "adminContentFormModal";
    modal.className = "admin-modal-overlay";

    const fieldHtml = fields.map(field => {
        const inputType = field.type || "text";
        const inputClass = inputType === "textarea" ? "admin-form-textarea" : "admin-form-input";
        const control = inputType === "textarea"
            ? '<textarea class="' + inputClass + '" id="' + field.id + '" placeholder="' + escapeHtml(field.placeholder || "") + '">' + escapeHtml(field.value || "") + '</textarea>'
            : '<input class="' + inputClass + '" id="' + field.id + '" type="' + inputType + '" value="' + escapeHtml(field.value || "") + '" placeholder="' + escapeHtml(field.placeholder || "") + '"' + (field.required ? " required" : "") + '>';
        return '<label class="admin-form-field"><span>' + escapeHtml(field.label) + '</span>' + control + '</label>';
    }).join("");

    modal.innerHTML =
        '<div class="admin-modal admin-content-form-modal">' +
            '<button type="button" class="admin-modal-close" id="adminContentFormClose" aria-label="Yopish">×</button>' +
            '<div class="modal-eyebrow">AXSIKENT IT / ADMIN</div>' +
            '<h2>' + escapeHtml(title) + '</h2>' +
            '<p class="admin-form-subtitle">Ma’lumotlarni kiriting va saqlang.</p>' +
            '<form id="adminContentForm" class="admin-content-form">' +
                fieldHtml +
                '<div class="admin-form-actions">' +
                    '<button type="button" class="modal-secondary-btn" id="adminContentFormCancel">Bekor qilish</button>' +
                    '<button type="submit" class="modal-primary-btn">Saqlash</button>' +
                '</div>' +
            '</form>' +
        '</div>';

    document.body.appendChild(modal);
    requestAnimationFrame(() => modal.classList.add("show"));

    const close = () => {
        modal.classList.remove("show");
        setTimeout(() => modal.remove(), 180);
    };

    document.getElementById("adminContentFormClose").onclick = close;
    document.getElementById("adminContentFormCancel").onclick = close;

    document.getElementById("adminContentForm").addEventListener("submit", async event => {
        event.preventDefault();
        const button = event.currentTarget.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = "Saqlanmoqda...";

        try {
            const values = {};
            fields.forEach(field => {
                values[field.id] = document.getElementById(field.id).value.trim();
            });
            await onSubmit(values);
            close();
        } catch (error) {
            showToast(error.message || "Saqlashda xatolik", "error");
            button.disabled = false;
            button.textContent = "Saqlash";
        }
    });
}

async function openPodcastCreate() {
    openAdminContentForm("🎧 Yangi podcast", [
        {id:"title", label:"Podcast nomi", required:true, placeholder:"Masalan: IT olamiga kirish"},
        {id:"description", label:"Tavsif", type:"textarea", placeholder:"Podcast haqida qisqacha..."},
        {id:"audio", label:"Audio URL", placeholder:"https://..."},
        {id:"duration", label:"Davomiyligi (minut)", type:"number", value:"0", placeholder:"30"}
    ], async values => {
        if (!values.title) throw new Error("Podcast nomini kiriting.");
        await apiRequest("/admin/content/podcasts", {
            method:"POST",
            body:JSON.stringify({
                title:values.title,
                description:values.description,
                audio_url:values.audio,
                duration_minutes:Number(values.duration || 0)
            })
        });
        showToast("Podcast qo‘shildi");
        await loadPodcasts();
    });
}

async function openTrainingCreate() {
    openAdminContentForm("📅 Yangi trening", [
        {id:"title", label:"Trening nomi", required:true, placeholder:"Masalan: Frontend Masterclass"},
        {id:"description", label:"Tavsif", type:"textarea", placeholder:"Trening haqida..."},
        {id:"start", label:"Boshlanish vaqti", required:true, placeholder:"2026-09-20T18:00:00"},
        {id:"end", label:"Tugash vaqti", placeholder:"2026-09-20T20:00:00"},
        {id:"location", label:"Manzil", placeholder:"Axsikent IT / 2-xona"},
        {id:"capacity", label:"Sig‘im", type:"number", placeholder:"20"}
    ], async values => {
        if (!values.title || !values.start) throw new Error("Trening nomi va boshlanish vaqtini kiriting.");
        await apiRequest("/admin/content/trainings", {
            method:"POST",
            body:JSON.stringify({
                title:values.title,
                description:values.description,
                start_at:values.start,
                end_at:values.end || null,
                location:values.location,
                capacity:values.capacity ? Number(values.capacity) : null
            })
        });
        showToast("Trening qo‘shildi");
        await loadTrainings();
    });
}

async function openExamCreate() {
    openAdminContentForm("🧪 Yangi imtihon", [
        {id:"title", label:"Imtihon nomi", required:true, placeholder:"Masalan: Python yakuniy imtihon"},
        {id:"description", label:"Tavsif", type:"textarea", placeholder:"Imtihon haqida..."},
        {id:"start", label:"Boshlanish vaqti", required:true, placeholder:"2026-09-20T10:00:00"},
        {id:"end", label:"Tugash vaqti", placeholder:"2026-09-20T12:00:00"},
        {id:"location", label:"Manzil", placeholder:"Axsikent IT / 1-xona"},
        {id:"capacity", label:"Sig‘im", type:"number", placeholder:"20"}
    ], async values => {
        if (!values.title || !values.start) throw new Error("Imtihon nomi va boshlanish vaqtini kiriting.");
        await apiRequest("/admin/content/exams", {
            method:"POST",
            body:JSON.stringify({
                title:values.title,
                description:values.description,
                start_at:values.start,
                end_at:values.end || null,
                location:values.location,
                capacity:values.capacity ? Number(values.capacity) : null
            })
        });
        showToast("Imtihon qo‘shildi");
        await loadExams();
    });
}

/* ============================================================
   MOBILE / INIT
   ============================================================ */

function initMobileMenu() {
    const button = document.getElementById("mobileMenuBtn");
    const sidebar = document.getElementById("sidebar");

    if (!button || !sidebar) return;

    button.setAttribute("aria-expanded", "false");

    button.addEventListener("click", event => {
        event.preventDefault();
        event.stopPropagation();

        const open = sidebar.classList.toggle("open");
        button.setAttribute("aria-expanded", String(open));
    });

    document.addEventListener("click", event => {
        if (!sidebar.classList.contains("open")) return;
        if (sidebar.contains(event.target) || button.contains(event.target)) {
            return;
        }

        sidebar.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
    });
}

async function initAdminPanel() {
    if (!requireAdminAuth()) return;

    initNavigation();
    initLeadActions();
    initMobileMenu();
    initNotifications();
    initAdministratorManagement();

    const logoutButton = document.getElementById("logoutBtn");
    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }

    const refreshButton = document.getElementById("refreshBtn");
    if (refreshButton) {
        refreshButton.addEventListener("click", refreshDashboard);
    }

    await loadAdminProfile();
    await refreshDashboard();
}

document.addEventListener("DOMContentLoaded", initAdminPanel);
