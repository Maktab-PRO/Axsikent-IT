(function () {
    const AI_API = "https://axsikent-it-backend.onrender.com";
    let aiCheckController = null;

    function aiEsc(value) {
        return String(value ?? "").replace(/[&<>"']/g, function (ch) {
            return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch];
        });
    }

    function ensureAiChecker() {
        const section = document.getElementById("studentAiSection");
        if (!section || document.getElementById("studentAiChecker")) return;

        const box = document.createElement("div");
        box.id = "studentAiChecker";
        box.style.cssText = "position:relative;z-index:1;margin-top:18px;padding:18px;border-radius:17px;background:rgba(2,6,23,.48);border:1px solid rgba(167,139,250,.18);";
        box.innerHTML =
            '<div style="color:#c4b5fd;font-size:11px;font-weight:900;letter-spacing:.1em;">AI TEKSHIRUV</div>' +
            '<div style="margin-top:6px;color:#fff;font-size:15px;font-weight:900;">Uy vazifangizni shu yerda tekshirtiring</div>' +
            '<div style="margin-top:5px;color:#7f8da3;font-size:11px;line-height:1.5;">Topshiriq va javobni kiriting. 80% va undan yuqori natija — o‘tish.</div>' +
            '<div style="display:grid;gap:10px;margin-top:14px;">' +
                '<textarea id="studentAiTask" rows="3" placeholder="Topshiriq..." style="width:100%;box-sizing:border-box;resize:vertical;padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:#090e16;color:#fff;outline:none;"></textarea>' +
                '<textarea id="studentAiAnswer" rows="5" placeholder="Javobingiz..." style="width:100%;box-sizing:border-box;resize:vertical;padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:#090e16;color:#fff;outline:none;"></textarea>' +
                '<button id="studentAiCheckButton" type="button" style="min-height:44px;border:0;border-radius:13px;background:linear-gradient(135deg,#7c3aed,#059669);color:#fff;font-weight:900;cursor:pointer;">🤖 AI bilan tekshirish</button>' +
            '</div>' +
            '<div id="studentAiResult" style="margin-top:12px;"></div>';

        const telegramBlock = document.getElementById("studentTelegramConnectButton");
        const parent = telegramBlock ? telegramBlock.closest("div[style*=\"position:relative\"]") : null;
        if (parent && parent.parentElement === section) {
            section.insertBefore(box, parent);
        } else {
            section.appendChild(box);
        }

        document.getElementById("studentAiCheckButton").addEventListener("click", checkStudentHomeworkWithAI);
    }

    async function checkStudentHomeworkWithAI() {
        const token = localStorage.getItem("access_token");
        const taskEl = document.getElementById("studentAiTask");
        const answerEl = document.getElementById("studentAiAnswer");
        const button = document.getElementById("studentAiCheckButton");
        const resultEl = document.getElementById("studentAiResult");

        if (!token) {
            window.location.href = "index.html";
            return;
        }

        const task = taskEl ? taskEl.value.trim() : "";
        const answer = answerEl ? answerEl.value.trim() : "";

        if (!task || !answer) {
            resultEl.innerHTML = '<div style="padding:12px;border-radius:12px;color:#fbbf24;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.18);">Topshiriq va javobni to‘liq kiriting.</div>';
            return;
        }

        if (aiCheckController) aiCheckController.abort();
        aiCheckController = new AbortController();
        const timeout = setTimeout(() => aiCheckController.abort(), 60000);

        button.disabled = true;
        button.textContent = "🤖 AI tekshirmoqda...";
        resultEl.innerHTML = '<div style="padding:12px;color:#94a3b8;">Javob tahlil qilinmoqda...</div>';

        try {
            const response = await fetch(AI_API + "/ai/homework/check", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({task: task, answer: answer}),
                signal: aiCheckController.signal
            });

            const data = await response.json().catch(() => ({}));

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                window.location.href = "index.html";
                return;
            }

            if (!response.ok) {
                throw new Error(data.detail || "AI tekshiruvda xatolik yuz berdi.");
            }

            const mistakes = Array.isArray(data.mistakes) ? data.mistakes : [];
            const correctPoints = Array.isArray(data.correct_points) ? data.correct_points : [];
            const mistakesHtml = mistakes.length
                ? mistakes.map(item => "<li>" + aiEsc(item) + "</li>").join("")
                : "<li>Xato topilmadi.</li>";
            const correctHtml = correctPoints.length
                ? correctPoints.map(item => "<li>" + aiEsc(item) + "</li>").join("")
                : "<li>To‘g‘ri bajarilgan qismlar ko‘rsatilmagan.</li>";

            resultEl.innerHTML =
                '<div style="padding:15px;border-radius:15px;background:rgba(255,255,255,.035);border:1px solid rgba(167,139,250,.18);">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">' +
                        '<strong style="color:#fff;">🤖 AKHSIKENT AI natijasi</strong>' +
                        '<strong style="font-size:22px;color:' + (Number(data.score) >= 80 ? "#4ade80" : "#fbbf24") + ';">' + aiEsc(data.score) + '%</strong>' +
                    '</div>' +
                    '<div style="margin-top:8px;color:' + (data.passed ? "#4ade80" : "#fbbf24") + ';font-weight:900;">' +
                        (data.passed ? "✅ Keyingi dars uchun o‘tish chegarasidan o‘tdingiz." : "🔒 80% ga yetmadi. Xatolarni ko‘rib, qayta ishlang.") +
                    '</div>' +
                    '<div style="margin-top:12px;color:#a7f3d0;font-weight:800;font-size:12px;">To‘g‘ri bajarilganlar</div>' +
                    '<ul style="margin:7px 0 0 18px;color:#cbd5e1;font-size:12px;line-height:1.6;">' + correctHtml + '</ul>' +
                    '<div style="margin-top:10px;color:#fca5a5;font-weight:800;font-size:12px;">Xatolar</div>' +
                    '<ul style="margin:7px 0 0 18px;color:#cbd5e1;font-size:12px;line-height:1.6;">' + mistakesHtml + '</ul>' +
                    '<div style="margin-top:10px;color:#c4b5fd;font-weight:800;font-size:12px;">Izoh</div>' +
                    '<div style="margin-top:5px;color:#cbd5e1;font-size:12px;line-height:1.6;">' + aiEsc(data.explanation || "—") + '</div>' +
                    '<div style="margin-top:10px;color:#c4b5fd;font-weight:800;font-size:12px;">Tavsiya</div>' +
                    '<div style="margin-top:5px;color:#cbd5e1;font-size:12px;line-height:1.6;">' + aiEsc(data.recommendation || "—") + '</div>' +
                '</div>';
        } catch (error) {
            if (error && error.name === "AbortError") {
                resultEl.innerHTML = '<div style="padding:12px;border-radius:12px;color:#fbbf24;background:rgba(245,158,11,.08);">AI serveri javob berishi uzoq davom etdi. Qayta urinib ko‘ring.</div>';
            } else {
                resultEl.innerHTML = '<div style="padding:12px;border-radius:12px;color:#f87171;background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.18);">❌ ' + aiEsc(error.message || "AI tekshiruvda xatolik") + '</div>';
            }
        } finally {
            clearTimeout(timeout);
            button.disabled = false;
            button.textContent = "🤖 AI bilan tekshirish";
            aiCheckController = null;
        }
    }

    function initStudentAi() {
        ensureAiChecker();
        if (typeof window.loadStudentTelegramStatus === "function") {
            window.loadStudentTelegramStatus();
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initStudentAi);
    } else {
        initStudentAi();
    }
})();