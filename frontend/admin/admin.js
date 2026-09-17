/* =========================================================
   AXSIKENT IT — COMMAND CENTER
   ADMIN JAVASCRIPT
========================================================= */

"use strict";


/* =========================================================
   CONFIG
========================================================= */

const API_BASE = "https://axsikent-it-4.onrender.com";


/* =========================================================
   STORAGE
========================================================= */

const TOKEN_KEY = "axsikent_admin_token";
const ADMIN_KEY = "axsikent_admin";
function requireAdminAuth() {
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
        window.location.replace("login.html");
        return false;
    }

    return true;
}

/* =========================================================
   DOM HELPERS
========================================================= */

const $ = (selector) => document.querySelector(selector);

const $$ = (selector) => document.querySelectorAll(selector);


/* =========================================================
   AUTH
========================================================= */

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}


function getSavedAdmin() {
    try {
        return JSON.parse(
            localStorage.getItem(ADMIN_KEY)
        );
    } catch {
        return null;
    }
}


function saveAdmin(data) {

    if (!data) return;

    localStorage.setItem(
        ADMIN_KEY,
        JSON.stringify(data)
    );
}


function clearAuth() {

    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ADMIN_KEY);
}


/* =========================================================
   API REQUEST
========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    const token = getToken();

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] =
            `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    if (response.status === 401) {

        clearAuth();

        showToast(
            "Sessiya tugagan. Qayta login qiling.",
            "error"
        );

        setTimeout(() => {
            window.location.reload();
        }, 1200);

        throw new Error("Unauthorized");
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


/* =========================================================
   TOAST
========================================================= */

function showToast(
    message,
    type = "success"
) {

    const container =
        $("#toastContainer");

    if (!container) return;

    const toast =
        document.createElement("div");

    toast.className =
        `toast toast-${type}`;

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


/* =========================================================
   HTML ESCAPE
========================================================= */

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


/* =========================================================
   NAVIGATION
========================================================= */

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


function openSection(section) {

    if (!section) return;

    /* NAV ACTIVE */

    $$(".nav-item").forEach(item => {

        item.classList.toggle(
            "active",
            item.dataset.section === section
        );

    });


    /* SECTIONS */

    $$(".page-section").forEach(page => {

        page.classList.toggle(
            "active",
            page.id === `section-${section}`
        );

    });


    /* HEADER */

    const title =
        sectionTitles[section] ||
        "Command Center";

    const pageTitle =
        $("#pageTitle");

    const breadcrumb =
        $("#breadcrumbCurrent");

    if (pageTitle) {
        pageTitle.textContent = title;
    }

    if (breadcrumb) {
        breadcrumb.textContent = title;
    }


    /* MOBILE SIDEBAR */

    const sidebar =
        $("#sidebar");

    if (sidebar) {
        sidebar.classList.remove("mobile-open");
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* =========================================================
   NAVIGATION EVENTS
========================================================= */

function initNavigation() {

    $$(".nav-item").forEach(item => {

        item.addEventListener(
            "click",
            () => {
                openSection(
                    item.dataset.section
                );
            }
        );

    });


    $$(".quick-action").forEach(item => {

        item.addEventListener(
            "click",
            () => {
                openSection(
                    item.dataset.section
                );
            }
        );

    });


    $$(".panel-link").forEach(item => {

        item.addEventListener(
            "click",
            () => {
                openSection(
                    item.dataset.section
                );
            }
        );

    });
}


/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const data =
            await apiRequest(
                "/admins/dashboard"
            );


        if (!data?.success) {
            throw new Error(
                "Dashboard ma'lumotlari olinmadi"
            );
        }


        const overview =
            data.overview || {};


        /* STUDENTS */

        setText(
            "statStudents",
            overview.students?.active ?? 0
        );


        /* TEACHERS */

        setText(
            "statTeachers",
            overview.teachers?.active ?? 0
        );


        /* COURSES */

        setText(
            "statCourses",
            overview.courses?.active ?? 0
        );


        /* GROUPS */

        const groups =
            overview.groups?.active ?? 0;


        /* LEADS */

        const newLeads =
            overview.leads?.new ?? 0;

        setText(
            "leadBadge",
            newLeads
        );


        /* ADMIN NAME */

        if (data.admin?.full_name) {

            setText(
                "adminName",
                data.admin.full_name
            );

        }


        /* SAVE ADMIN */

        if (data.admin) {
            saveAdmin(data.admin);
        }


        /* GAMIFICATION */

        window.adminDashboardData =
            data;


        showToast(
            "Dashboard yangilandi",
            "success"
        );


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


/* =========================================================
   SHOP STATISTICS
========================================================= */

async function loadShopStats() {

    try {

        const data =
            await apiRequest(
                "/admin/shop/stats/summary"
            );


        /*
         * Backend javobining turli shakllarini
         * xavfsiz o'qish uchun.
         */

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


/* =========================================================
   GENERIC TEXT SETTER
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (!element) return;

    element.textContent =
        value ?? "0";
}


/* =========================================================
   ADMIN PROFILE
========================================================= */

async function loadAdminProfile() {

    try {

        const data =
            await apiRequest(
                "/admins/me"
            );

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


/* =========================================================
   REFRESH
========================================================= */

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


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    clearAuth();

    showToast(
        "Admin sessiyasi yopildi",
        "success"
    );

    setTimeout(() => {

        window.location.href =
            "../index.html";

    }, 700);
}


/* =========================================================
   MOBILE MENU
========================================================= */

function initMobileMenu() {

    const button =
        $("#mobileMenuBtn");

    const sidebar =
        $("#sidebar");

    if (!button || !sidebar) return;

    button.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "mobile-open"
            );

        }
    );
}


/* =========================================================
   NOTIFICATION
========================================================= */

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


/* =========================================================
   INIT
========================================================= */

async function initAdminPanel() {

    async function initAdminPanel() {
    if (!requireAdminAuth()) return;

    console.log("Axsikent IT Command Center ishga tushdi.");


    initNavigation();

    initMobileMenu();

    initNotifications();


    /* LOGOUT */

    const logoutButton =
        $("#logoutBtn");

    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            logout
        );

    }


    /* REFRESH */

    const refreshButton =
        $("#refreshBtn");

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            refreshDashboard
        );

    }


    /* LOAD DATA */

    await loadAdminProfile();

    await refreshDashboard();


    console.log(
        "Command Center tayyor."
    );
}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initAdminPanel
);

   // ============================================================
// STUDENTS MODULE
// ============================================================

async function loadStudents() {
    const container = document.getElementById("studentsContent");
    if (!container) return;

    container.innerHTML = `
        <div class="module-loading">
            <div class="module-spinner"></div>
            <span>O‘quvchilar yuklanmoqda...</span>
        </div>
    `;

    try {
        const data = await apiRequest("/admin/students/");

        const students = Array.isArray(data)
            ? data
            : (data.students || data.items || data.data || []);

        renderStudents(students);

    } catch (error) {
        console.error("Students error:", error);

        container.innerHTML = `
            <div class="module-error">
                <div class="module-error-icon">!</div>
                <h3>O‘quvchilarni yuklab bo‘lmadi</h3>
                <p>${escapeHtml(error.message || "Server xatosi")}</p>
                <button class="module-retry" onclick="loadStudents()">
                    Qayta urinish
                </button>
            </div>
        `;
    }
}


function renderStudents(students) {
    const container = document.getElementById("studentsContent");
    if (!container) return;

    if (!students.length) {
        container.innerHTML = `
            <div class="module-empty">
                <div class="module-empty-icon">◎</div>
                <h3>Hozircha o‘quvchilar yo‘q</h3>
                <p>Tizimda ro‘yxatdan o‘tgan o‘quvchilar ko‘rinadi.</p>
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
                    <option value="all">Barcha holatlar</option>
                    <option value="active">Faol</option>
                    <option value="inactive">Nofaol</option>
                </select>
            </div>
        </div>

        <div class="students-table-wrap">
            <table class="students-table">
                <thead>
                    <tr>
                        <th>O‘QUVCHI</th>
                        <th>TELEFON</th>
                        <th>ID</th>
                        <th>HOLAT</th>
                        <th>AMAL</th>
                    </tr>
                </thead>

                <tbody id="studentsTableBody">
                    ${students.map(student => studentRow(student)).join("")}
                </tbody>
            </table>
        </div>

        <div class="students-footer">
            <span>Jami: <strong>${students.length}</strong> ta o‘quvchi</span>
        </div>
    `;

    const searchInput = document.getElementById("studentSearchInput");
    const statusFilter = document.getElementById("studentStatusFilter");

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            filterStudents(students);
        });
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", () => {
            filterStudents(students);
        });
    }
}


function studentRow(student) {
    const id = student.id ?? "-";
    const name = student.full_name || student.name || "Noma’lum";
    const phone = student.phone || "-";
    const active = student.is_active !== false;

    const initials = name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map(word => word.charAt(0).toUpperCase())
        .join("");

    return `
        <tr
            data-name="${escapeHtml(name.toLowerCase())}"
            data-phone="${escapeHtml(phone.toLowerCase())}"
            data-status="${active ? "active" : "inactive"}"
        >
            <td>
                <div class="student-identity">
                    <div class="student-avatar">
                        ${escapeHtml(initials || "U")}
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
                <span class="status-badge ${active ? "status-active" : "status-inactive"}">
                    <span></span>
                    ${active ? "Faol" : "Nofaol"}
                </span>
            </td>

            <td>
                <div class="student-actions">
                    <button
                        class="student-action-btn"
                        onclick="viewStudent(${Number(id)})"
                        title="Profil"
                    >
                        Ko‘rish
                    </button>

                    <button
                        class="student-action-btn ${active ? "danger" : "success"}"
                        onclick="toggleStudentStatus(${Number(id)}, ${active})"
                        title="${active ? "Deaktivatsiya" : "Aktivatsiya"}"
                    >
                        ${active ? "Bloklash" : "Faollashtirish"}
                    </button>
                </div>
            </td>
        </tr>
    `;
}


function filterStudents(students) {
    const search =
        (document.getElementById("studentSearchInput")?.value || "")
            .trim()
            .toLowerCase();

    const status =
        document.getElementById("studentStatusFilter")?.value || "all";

    const filtered = students.filter(student => {
        const name = (student.full_name || student.name || "").toLowerCase();
        const phone = (student.phone || "").toLowerCase();
        const active = student.is_active !== false;

        const matchesSearch =
            !search ||
            name.includes(search) ||
            phone.includes(search);

        const matchesStatus =
            status === "all" ||
            (status === "active" && active) ||
            (status === "inactive" && !active);

        return matchesSearch && matchesStatus;
    });

    const tbody = document.getElementById("studentsTableBody");

    if (!tbody) return;

    tbody.innerHTML = filtered.length
        ? filtered.map(student => studentRow(student)).join("")
        : `
            <tr>
                <td colspan="5">
                    <div class="table-empty">
                        Hech narsa topilmadi.
                    </div>
                </td>
            </tr>
        `;
}


async function viewStudent(studentId) {
    try {
        const data = await apiRequest(`/admin/students/${studentId}`);

        showStudentModal(data);

    } catch (error) {
        showToast(
            error.message || "O‘quvchi ma’lumotlarini olishda xatolik",
            "error"
        );
    }
}


function showStudentModal(student) {
    const oldModal = document.getElementById("studentModal");

    if (oldModal) oldModal.remove();

    const name =
        student.full_name ||
        student.name ||
        "Noma’lum o‘quvchi";

    const phone = student.phone || "-";
    const id = student.id ?? "-";
    const active = student.is_active !== false;

    const modal = document.createElement("div");

    modal.id = "studentModal";
    modal.className = "admin-modal-overlay";

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
                        name
                            .split(" ")
                            .filter(Boolean)
                            .slice(0, 2)
                            .map(x => x[0])
                            .join("")
                            .toUpperCase()
                    )}
                </div>

                <div>
                    <div class="modal-eyebrow">
                        STUDENT PROFILE
                    </div>

                    <h2>
                        ${escapeHtml(name)}
                    </h2>

                    <span class="status-badge ${active ? "status-active" : "status-inactive"}">
                        <span></span>
                        ${active ? "Faol" : "Nofaol"}
                    </span>
                </div>
            </div>

            <div class="modal-info-grid">

                <div class="modal-info-card">
                    <span>ID</span>
                    <strong>#${escapeHtml(id)}</strong>
                </div>

                <div class="modal-info-card">
                    <span>Telefon</span>
                    <strong>${escapeHtml(phone)}</strong>
                </div>

                <div class="modal-info-card">
                    <span>Rol</span>
                    <strong>Student</strong>
                </div>

                <div class="modal-info-card">
                    <span>Holat</span>
                    <strong>${active ? "Faol" : "Nofaol"}</strong>
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
                    onclick="toggleStudentStatus(${Number(id)}, ${active}); closeStudentModal();"
                >
                    ${active ? "Bloklash" : "Faollashtirish"}
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
    const modal = document.getElementById("studentModal");

    if (!modal) return;

    modal.classList.remove("show");

    setTimeout(() => {
        modal.remove();
    }, 250);
}


async function toggleStudentStatus(studentId, currentlyActive) {
    const action = currentlyActive ? "deactivate" : "activate";

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
            error.message || "Holatni o‘zgartirishda xatolik",
            "error"
        );
    }
                          }
