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
    settings: "Sozlamalar",
    administrators: "Administratorlar"
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
    sidebar.style.transform = "translateX(-100%)";
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
                sidebar.classList.contains("open");

            if (isOpen) {

                sidebar.classList.remove("open");

                sidebar.style.transform =
                    "translateX(-100%)";

            } else {

                sidebar.classList.add("open");

                sidebar.style.transform =
                    "translateX(0)";

            }

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
   EDUCATION + REWARDS MODULES
   ============================================================ */

function moduleLoading(textValue) {
    return `<div class="module-loading"><div class="module-spinner"></div><span>${escapeHtml(textValue)}</span></div>`;
}

function moduleTable(headers, rows) {
    return `<div class="admin-data-table-wrap"><table class="admin-data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

function actionButton(label, action, cls = "") {
    return `<button class="module-action-btn ${cls}" onclick="${action}">${label}</button>`;
}

function showInfoModal(title, body) {
    document.getElementById("moduleInfoModal")?.remove();
    const modal=document.createElement("div");
    modal.id="moduleInfoModal";
    modal.className="admin-modal-overlay show";
    modal.innerHTML=`<div class="admin-modal module-info-modal"><button class="admin-modal-close" onclick="document.getElementById('moduleInfoModal')?.remove()">×</button><div class="modal-eyebrow">AXSIKENT IT</div><h2>${escapeHtml(title)}</h2><div class="module-info-body">${body}</div><div class="modal-actions"><button class="modal-secondary-btn" onclick="document.getElementById('moduleInfoModal')?.remove()">Yopish</button></div></div>`;
    document.body.appendChild(modal);
}

async function loadTeachers() {
    const box=document.getElementById("teachersContent"); if(!box)return;
    box.innerHTML=moduleLoading("O‘qituvchilar yuklanmoqda...");
    try{
        const d=await apiRequest("/admin/teachers/");
        const items=d?.teachers||[];
        box.innerHTML=items.length?moduleTable(["O‘QITUVCHI","FAN","GURUHLAR","HOLAT","AMAL"],items.map(t=>`<tr data-teacher-search="${escapeHtml((t.full_name+" "+t.phone+" "+t.subject).toLowerCase())}"><td><strong>${escapeHtml(t.full_name)}</strong><small>${escapeHtml(t.phone)}</small></td><td>${escapeHtml(t.subject||"—")}</td><td>${t.groups_count??0}</td><td><span class="status-badge ${t.is_active?"status-active":"status-inactive"}"><span></span>${t.is_active?"Faol":"Nofaol"}</span></td><td>${actionButton("Ko‘rish",`viewTeacher(${Number(t.id)})`)} ${actionButton(t.is_active?"Bloklash":"Faollashtirish",`toggleTeacher(${Number(t.id)},${!!t.is_active})`,t.is_active?"danger":"success")}</td></tr>`).join(""):`<div class="module-empty"><h3>O‘qituvchilar yo‘q</h3><p>Tizimda hozircha o‘qituvchi topilmadi.</p></div>`;
    }catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}

function filterTeachers(){
    const q=(document.getElementById("teacherSearch")?.value||"").toLowerCase();
    document.querySelectorAll("[data-teacher-search]").forEach(row=>row.style.display=!q||row.dataset.teacherSearch.includes(q)?"":"none");
}

async function viewTeacher(id){
    try{const d=await apiRequest(`/admin/teachers/${id}`);const t=d.teacher||{};showInfoModal("O‘qituvchi profili",`<div class="module-detail-grid"><div><small>Ism</small><strong>${escapeHtml(t.full_name)}</strong></div><div><small>Telefon</small><strong>${escapeHtml(t.phone)}</strong></div><div><small>Fan</small><strong>${escapeHtml(t.subject||"—")}</strong></div><div><small>Guruhlar</small><strong>${(d.groups||[]).length}</strong></div></div>`);}catch(e){showToast(e.message,"error");}
}

async function toggleTeacher(id,active){
    try{await apiRequest(`/admin/teachers/${id}/${active?"deactivate":"activate"}`,{method:"PUT"});showToast(active?"O‘qituvchi deaktiv qilindi":"O‘qituvchi faollashtirildi");await loadTeachers();}catch(e){showToast(e.message,"error");}
}

async function loadCourses(){
    const box=document.getElementById("coursesContent");if(!box)return;
    box.innerHTML=moduleLoading("Kurslar yuklanmoqda...");
    try{
        const [d,c]=await Promise.all([apiRequest("/admin/courses/"),apiRequest("/admin/courses/categories")]);
        const items=Array.isArray(d)?d:(d?.courses||[]);
        window.adminCategories=Array.isArray(c)?c:(c?.categories||[]);
        box.innerHTML=items.length?moduleTable(["KURS","KATEGORIYA","YOSH","DARS","NARX","HOLAT","AMAL"],items.map(x=>`<tr><td><strong>${escapeHtml(x.name)}</strong><small>#${x.id}</small></td><td>${escapeHtml(x.category?.name||x.category_name||"—")}</td><td>${x.age_min??"—"}–${x.age_max??"—"}</td><td>${x.lesson_minutes??"—"} daq.</td><td>${x.price_min??0}–${x.price_max??0}</td><td><span class="status-badge ${x.is_active?"status-active":"status-inactive"}"><span></span>${x.is_active?"Faol":"Nofaol"}</span></td><td>${actionButton("Ko‘rish",`viewCourse(${Number(x.id)})`)} ${actionButton(x.is_active?"Deaktiv":"Aktiv",`toggleCourse(${Number(x.id)},${!!x.is_active})`,x.is_active?"danger":"success")}</td></tr>`).join(""):`<div class="module-empty"><h3>Kurslar yo‘q</h3><p>Yangi kurs yarating.</p></div>`;
    }catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}

async function viewCourse(id){
    try{const d=await apiRequest(`/admin/courses/${id}`);showInfoModal("Kurs tafsilotlari",`<div class="module-detail-grid"><div><small>Nomi</small><strong>${escapeHtml(d.name)}</strong></div><div><small>Kategoriya</small><strong>${escapeHtml(d.category?.name||"—")}</strong></div><div><small>Yosh</small><strong>${d.age_min??"—"}–${d.age_max??"—"}</strong></div><div><small>Dars</small><strong>${d.lesson_minutes??"—"} daq.</strong></div></div><div class="module-detail-list">${(d.modules||[]).map(m=>`<div><strong>${escapeHtml(m.title)}</strong><span>${(m.lessons||[]).length} ta dars</span></div>`).join("")||"<p>Modullar yo‘q.</p>"}</div>`);}catch(e){showToast(e.message,"error");}
}
async function toggleCourse(id,active){try{await apiRequest(`/admin/courses/${id}/${active?"deactivate":"activate"}`,{method:"PUT"});showToast(active?"Kurs deaktiv qilindi":"Kurs faollashtirildi");await loadCourses();await loadDashboard();}catch(e){showToast(e.message,"error");}}
async function openCourseCreate(){await loadCourses();const cats=window.adminCategories||[];const category=prompt("Kategoriya ID:\n"+cats.map(x=>`${x.id} — ${x.name}`).join("\n"));if(category===null)return;const name=prompt("Kurs nomi:");if(!name)return;try{await apiRequest("/admin/courses/",{method:"POST",body:JSON.stringify({category_id:Number(category),name:name.trim(),description:""})});showToast("Kurs yaratildi");await loadCourses();}catch(e){showToast(e.message,"error");}}

async function loadGroups(){
    const box=document.getElementById("groupsContent");if(!box)return;
    box.innerHTML=moduleLoading("Guruhlar yuklanmoqda...");
    try{const d=await apiRequest("/admin/groups/");const items=d?.groups||d||[];box.innerHTML=items.length?moduleTable(["GURUH","KURS","O‘QITUVCHI","O‘QUVCHILAR","HOLAT","AMAL"],items.map(g=>`<tr><td><strong>${escapeHtml(g.name)}</strong><small>#${g.id}</small></td><td>${escapeHtml(g.course?.name||"—")}</td><td>${escapeHtml(g.teacher?.full_name||"—")}</td><td>${g.students_count??0}/${g.capacity??0}</td><td><span class="status-badge ${g.is_active?"status-active":"status-inactive"}"><span></span>${g.is_active?"Faol":"Nofaol"}</span></td><td>${actionButton("Ko‘rish",`viewGroup(${Number(g.id)})`)} ${actionButton(g.is_active?"Deaktiv":"Aktiv",`toggleGroup(${Number(g.id)},${!!g.is_active})`,g.is_active?"danger":"success")}</td></tr>`).join(""):`<div class="module-empty"><h3>Guruhlar yo‘q</h3><p>Yangi guruh yarating.</p></div>`;}catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}
async function viewGroup(id){try{const d=await apiRequest(`/admin/groups/${id}`);showInfoModal("Guruh tafsilotlari",`<div class="module-detail-grid"><div><small>Guruh</small><strong>${escapeHtml(d.name)}</strong></div><div><small>Kurs</small><strong>${escapeHtml(d.course?.name||"—")}</strong></div><div><small>O‘qituvchi</small><strong>${escapeHtml(d.teacher?.full_name||"—")}</strong></div><div><small>O‘quvchilar</small><strong>${d.students_count??0}/${d.capacity??0}</strong></div></div>`);}catch(e){showToast(e.message,"error");}}
async function toggleGroup(id,active){try{await apiRequest(`/admin/groups/${id}/${active?"deactivate":"activate"}`,{method:"PUT"});showToast(active?"Guruh deaktiv qilindi":"Guruh faollashtirildi");await loadGroups();}catch(e){showToast(e.message,"error");}}
async function openGroupCreate(){const name=prompt("Guruh nomi:");if(!name)return;const course=prompt("Kurs ID:");if(course===null)return;const teacher=prompt("O‘qituvchi ID:");if(teacher===null)return;try{await apiRequest("/admin/groups/",{method:"POST",body:JSON.stringify({name:name.trim(),course_id:Number(course),teacher_id:Number(teacher),capacity:15,status:"active"})});showToast("Guruh yaratildi");await loadGroups();}catch(e){showToast(e.message,"error");}}

async function loadRewards(){
    const box=document.getElementById("rewardsContent");if(!box)return;box.innerHTML=moduleLoading("Mukofotlar yuklanmoqda...");
    try{const [p,r]=await Promise.all([apiRequest("/admin/shop/products"),apiRequest("/admin/shop/rules")]);window.adminRules=r||[];box.innerHTML=p.length?moduleTable(["MUKOFOT","COIN","CRYSTAL","STOCK","HOLAT","AMAL"],p.map(x=>`<tr><td><strong>${escapeHtml(x.name)}</strong><small>#${x.id}</small></td><td>${x.coin_price}</td><td>${x.crystal_price}</td><td>${x.stock}</td><td><span class="status-badge ${x.is_active?"status-active":"status-inactive"}"><span></span>${x.is_active?"Faol":"Nofaol"}</span></td><td>${actionButton("Ko‘rish",`viewProduct(${Number(x.id)})`)} ${actionButton(x.is_active?"Deaktiv":"Aktiv",`toggleProduct(${Number(x.id)},${!!x.is_active})`,x.is_active?"danger":"success")} ${actionButton("O‘chirish",`deleteProduct(${Number(x.id)})`,"danger")}</td></tr>`).join(""):`<div class="module-empty"><h3>Mukofotlar yo‘q</h3><p>Yangi mukofot yarating.</p></div>`;}catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}
async function viewProduct(id){try{const d=await apiRequest(`/admin/shop/products/${id}`);showInfoModal("Mukofot tafsilotlari",`<div class="module-detail-grid"><div><small>Nomi</small><strong>${escapeHtml(d.name)}</strong></div><div><small>Coin</small><strong>${d.coin_price}</strong></div><div><small>Crystal</small><strong>${d.crystal_price}</strong></div><div><small>Stock</small><strong>${d.stock}</strong></div></div><p>${escapeHtml(d.description||"Tavsif yo‘q.")}</p>`);}catch(e){showToast(e.message,"error");}}
async function toggleProduct(id,active){try{await apiRequest(`/admin/shop/products/${id}/${active?"deactivate":"activate"}`,{method:"PUT"});showToast(active?"Mukofot deaktiv qilindi":"Mukofot faollashtirildi");await loadRewards();await loadShopStats();}catch(e){showToast(e.message,"error");}}
async function deleteProduct(id){if(!confirm("Bu mukofotni o‘chirishni tasdiqlaysizmi?"))return;try{await apiRequest(`/admin/shop/products/${id}`,{method:"DELETE"});showToast("Mukofot o‘chirildi");await loadRewards();await loadShopStats();}catch(e){showToast(e.message,"error");}}
async function openProductCreate(){const name=prompt("Mukofot nomi:");if(!name)return;const coin=prompt("Coin narxi:","0");if(coin===null)return;const crystal=prompt("Crystal narxi:","0");if(crystal===null)return;const stock=prompt("Stock:","0");if(stock===null)return;try{await apiRequest("/admin/shop/products",{method:"POST",body:JSON.stringify({name:name.trim(),description:"",image_url:"",coin_price:Number(coin),crystal_price:Number(crystal),stock:Number(stock)})});showToast("Mukofot qo‘shildi");await loadRewards();await loadShopStats();}catch(e){showToast(e.message,"error");}}

async function loadOrders(){
    const box=document.getElementById("ordersContent");if(!box)return;box.innerHTML=moduleLoading("Buyurtmalar yuklanmoqda...");
    try{const items=await apiRequest("/admin/shop/orders");box.innerHTML=items.length?moduleTable(["ID","O‘QUVCHI","MAHSULOT","SARF","STATUS","AMAL"],items.map(o=>`<tr><td>#${o.id}</td><td>#${o.student_id}</td><td>${escapeHtml(o.product_name||"—")}</td><td>${o.coin_spent} coin / ${o.crystal_spent} crystal</td><td>${escapeHtml(o.status)}</td><td><select class="module-status-select" onchange="updateOrderStatus(${Number(o.id)},this.value)"><option value="">Status</option><option value="pending">pending</option><option value="processing">processing</option><option value="completed">completed</option><option value="cancelled">cancelled</option></select> ${actionButton("Ko‘rish",`viewOrder(${Number(o.id)})`)}</td></tr>`).join(""):`<div class="module-empty"><h3>Buyurtmalar yo‘q</h3><p>Hozircha buyurtma mavjud emas.</p></div>`;}catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}
async function updateOrderStatus(id,status){if(!status)return;try{await apiRequest(`/admin/shop/orders/${id}/status`,{method:"PUT",body:JSON.stringify({status})});showToast("Buyurtma statusi yangilandi");await loadOrders();await loadShopStats();}catch(e){showToast(e.message,"error");}}
async function viewOrder(id){try{const d=await apiRequest(`/admin/shop/orders/${id}`);showInfoModal("Buyurtma",`<div class="module-detail-grid"><div><small>ID</small><strong>#${d.id}</strong></div><div><small>O‘quvchi</small><strong>#${d.student_id}</strong></div><div><small>Mahsulot</small><strong>${escapeHtml(d.product_name||"—")}</strong></div><div><small>Miqdor</small><strong>${d.quantity}</strong></div></div>`);}catch(e){showToast(e.message,"error");}}

async function loadBooks(){
    const box=document.getElementById("booksContent");if(!box)return;box.innerHTML=moduleLoading("Kitoblar yuklanmoqda...");
    try{const items=await apiRequest("/admin/books");box.innerHTML=items.length?moduleTable(["KITOB","NARX","COIN","STOCK","HOLAT"],items.map(b=>`<tr><td><strong>${escapeHtml(b.title)}</strong><small>#${b.id}</small></td><td>${b.price}</td><td>${b.coin_price}</td><td>${b.stock}</td><td>${b.is_active?"Faol":"Nofaol"}</td></tr>`).join("")):`<div class="module-empty"><h3>Kitoblar yo‘q</h3><p>Yangi kitob qo‘shishingiz mumkin.</p></div>`;}catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
}
async function openBookCreate(){const title=prompt("Kitob nomi:");if(!title)return;const price=prompt("Narxi:","0");if(price===null)return;const coin=prompt("Coin narxi:","0");if(coin===null)return;const stock=prompt("Stock:","0");if(stock===null)return;try{await apiRequest("/admin/books",{method:"POST",body:JSON.stringify({title:title.trim(),description:"",image_url:"",price:Number(price),coin_price:Number(coin),stock:Number(stock)})});showToast("Kitob qo‘shildi");await loadBooks();}catch(e){showToast(e.message,"error");}}

async function loadRanking(){
    const box=document.getElementById("rankingContent");if(!box)return;box.innerHTML=moduleLoading("Reyting yuklanmoqda...");
    try{const d=await apiRequest("/students/ranking");const items=Array.isArray(d)?d:(d?.ranking||d?.students||[]);box.innerHTML=items.length?moduleTable(["#","O‘QUVCHI","BALL"],items.map((x,i)=>`<tr><td>${i+1}</td><td><strong>${escapeHtml(x.full_name||x.name||"—")}</strong></td><td>${x.points??x.score??x.total_points??0}</td></tr>`).join(""):`<div class="module-empty"><h3>Reyting ma’lumoti yo‘q</h3><p>Hozircha ma’lumot mavjud emas.</p></div>`;}catch(e){box.innerHTML=`<div class="module-empty"><h3>Xatolik</h3><p>${escapeHtml(e.message)}</p></div>`;}
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

    initAdministratorManagement();


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
