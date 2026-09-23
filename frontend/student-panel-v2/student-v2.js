(() => {
  "use strict";

  const API = "https://axsikent-it-backend.onrender.com";
  const tokenKey = "access_token";
  let currentStudent = null;
  let currentCourse = null;
  let examState = null;
  let examTimer = null;
  let activeAbort = null;

  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const fmtDate = (v) => v ? new Date(v).toLocaleString("uz-UZ") : "—";

  function token() { return localStorage.getItem(tokenKey); }

  function showStatus(message, warning=false) {
    const el = $("statusBar");
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("warn", !!warning);
  }

  async function request(path, options = {}, retry = 1) {
    const controller = new AbortController();
    const timeout = Number(options.timeout || 60000);
    const timer = setTimeout(() => controller.abort(), timeout);
    const headers = {
      "Accept": "application/json",
      ...(options.body ? {"Content-Type":"application/json"} : {}),
      ...(options.headers || {})
    };

    if (!options.publicRequest) {
      const t = token();
      if (!t) {
        clearTimeout(timer);
        throw new Error("NO_SESSION");
      }
      headers.Authorization = "Bearer " + t;
    }

    try {
      const res = await fetch(API + path, {
        method: options.method || "GET",
        headers,
        body: options.body,
        cache: "no-store",
        signal: controller.signal
      });

      const raw = await res.text();
      let data = {};
      if (raw) {
        try { data = JSON.parse(raw); }
        catch (_) { data = {detail: raw}; }
      }

      if (res.status === 401 && !options.publicRequest) {
        localStorage.removeItem(tokenKey);
        localStorage.removeItem("user_role");
        throw new Error("SESSION_EXPIRED");
      }

      if (!res.ok) {
        const e = new Error(data.detail || "REQUEST_FAILED");
        e.status = res.status;
        throw e;
      }

      return data;
    } catch (e) {
      if ((e.name === "AbortError" || e.message === "Failed to fetch") && retry > 0) {
        await new Promise(r => setTimeout(r, 900));
        return request(path, options, retry - 1);
      }
      throw e;
    } finally {
      clearTimeout(timer);
    }
  }

  const api = (path, options = {}, retry = 1) => request(path, options, retry);

  function go(view) {
    document.querySelectorAll(".view").forEach(x => x.classList.remove("active"));
    const v = $("view-" + view);
    if (v) v.classList.add("active");
    document.querySelectorAll(".nav-item").forEach(x => x.classList.toggle("active", x.dataset.view === view));
    if (view === "courses") loadCourses();
    if (view === "homework") loadHomework();
    if (view === "ranking") loadRanking();
    if (view === "rewards") loadRewards();
    if (view === "books") loadBooks();
    if (view === "notifications") loadNotifications();
    if (view === "podcasts") loadPodcasts();
    if (view === "trainings") loadTrainings();
    if (view === "exams") loadExams();
    if (view === "online-tests") loadOnlineTests();
  }

  function renderEmpty(target, text) {
    const el = $(target);
    if (el) el.innerHTML = '<div class="item"><strong>' + esc(text) + '</strong></div>';
  }

  async function loginFromPanel(event) {
    event.preventDefault();
    const phone = $("loginPhone")?.value.trim();
    const password = $("loginPassword")?.value || "";
    const message = $("loginMessage");
    const button = $("loginBtn");
    if (!phone || !password) {
      if (message) message.textContent = "Telefon raqam va parolni kiriting.";
      return;
    }
    if (button) { button.disabled = true; button.textContent = "Kirilmoqda..."; }
    try {
      const data = await request("/students/login", {
        method: "POST",
        body: JSON.stringify({phone, password}),
        publicRequest: true,
        timeout: 60000
      }, 1);
      localStorage.setItem(tokenKey, data.access_token);
      localStorage.setItem("user_role", data.role || "student");
      if (message) message.textContent = "Muvaffaqiyatli kirildi.";
      await init();
    } catch (e) {
      console.error("Student login:", e);
      if (message) message.textContent = "Login yoki parol noto‘g‘ri, yoki server vaqtincha javob bermadi.";
    } finally {
      if (button) { button.disabled = false; button.textContent = "Kirish"; }
    }
  }

  async function init() {
    if (!token()) {
      $("sessionGate").classList.remove("hidden");
      $("dashboard").classList.add("hidden");
      return;
    }
    $("sessionGate").classList.add("hidden");
    $("dashboard").classList.remove("hidden");
    showStatus("Student ma’lumotlari yuklanmoqda...");
    try {
      currentStudent = await api("/students/me", {timeout:60000});
      $("welcomeName").textContent = "Xush kelibsiz, " + (currentStudent.full_name || "O‘quvchi") + "! 👋";
      await Promise.allSettled([loadHomeCourses(), loadHomeNotifications(), loadHomeRanking(), loadHomeRewards()]);
      showStatus("Student panel tayyor.");
    } catch (e) {
      console.error(e);
      if (e.message === "SESSION_EXPIRED") {
        location.href = "../index.html";
        return;
      }
      showStatus("Server vaqtincha band. Ma’lumotlar qayta urinishda yuklanadi.", true);
    }
  }

  async function loadHomeCourses() {
    try {
      const data = await api("/students/courses", {timeout:60000});
      const list = Array.isArray(data) ? data : [];
      const html = list.slice(0,4).map(c => courseItem(c)).join("");
      $("homeCourses").innerHTML = html || '<div class="item"><strong>Hozircha kurs biriktirilmagan.</strong></div>';
    } catch (e) {
      renderEmpty("homeCourses", "Kurslar hozircha yuklanmadi.");
    }
  }

  async function loadHomeNotifications() {
    try {
      const data = await api("/students/notifications", {timeout:60000});
      const list = Array.isArray(data) ? data : (data.notifications || []);
      $("homeNotifications").innerHTML = list.slice(0,4).map(notificationItem).join("") || '<div class="item"><strong>Yangi bildirishnoma yo‘q.</strong></div>';
    } catch (e) {
      renderEmpty("homeNotifications", "Bildirishnomalar hozircha yuklanmadi.");
    }
  }

  async function loadHomeRanking() {
    try {
      const data = await api("/students/ranking", {timeout:60000});
      const list = Array.isArray(data) ? data : [];
      const me = list.find(x => Number(x.student_id) === Number(currentStudent?.id));
      $("statXp").textContent = Number(me?.xp || 0);
      $("statRank").textContent = me?.rank ? "#" + me.rank : "—";
    } catch (_) {}
  }

  async function loadHomeRewards() {
    try {
      const data = await api("/students/rewards", {timeout:60000});
      const s = data.student || {};
      $("statCoins").textContent = Number(s.coins || 0);
      $("statStreak").textContent = Number(s.streak_days || 0) + " kun";
    } catch (_) {}
  }

  function courseItem(c) {
    const p = Math.max(0, Math.min(100, Number(c.progress || 0)));
    return '<div class="item" data-course="' + Number(c.id) + '" style="cursor:pointer;">' +
      '<strong>' + esc(c.name || "Kurs") + '</strong>' +
      '<small>' + esc(c.description || "Kurs davom etmoqda") + '</small>' +
      '<div class="progress"><span style="width:' + p + '%"></span></div>' +
      '<small>' + p + '%</small></div>';
  }

  function notificationItem(n) {
    const id = Number(n.id || 0);
    return '<div class="item"><strong>' + esc(n.title || n.message || "Bildirishnoma") + '</strong><small>' + esc(n.message || n.description || "") + '</small><small>' + esc(fmtDate(n.created_at || n.createdAt)) + '</small>' +
      (id ? '<button class="small-btn mark-read" data-id="' + id + '" type="button">O‘qildi</button>' : '') + '</div>';
  }

  async function loadCourses() {
    $("coursesList").innerHTML = '<div class="item">Kurslar yuklanmoqda...</div>';
    try {
      const list = await api("/students/courses", {timeout:60000});
      $("coursesList").innerHTML = (Array.isArray(list) ? list : []).map(courseItem).join("") || '<div class="item"><strong>Hozircha kurs biriktirilmagan.</strong></div>';
    } catch (_) { renderEmpty("coursesList", "Kurslar hozircha yuklanmadi."); }
  }

  async function openCourse(id) {
    currentCourse = Number(id);
    go("course-detail");
    $("courseDetail").innerHTML = '<div class="item">Kurs yuklanmoqda...</div>';
    try {
      const modules = await api("/students/courses/" + currentCourse + "/modules", {timeout:60000});
      const list = Array.isArray(modules) ? modules : [];
      $("courseDetail").innerHTML =
        '<div class="section-title"><div><div class="eyebrow">KURS</div><h2>Kurs modullari</h2></div></div>' +
        '<div class="stack">' +
        (list.map(m => '<div class="item module" data-module="' + Number(m.id) + '"><strong>' + esc(m.title) + '</strong><small>' + esc(m.description || "") + '</small><div class="progress"><span style="width:' + Number(m.progress || 0) + '%"></span></div><small>' + Number(m.progress || 0) + '% · ' + Number(m.completed_lessons || 0) + '/' + Number(m.total_lessons || 0) + ' dars</small><div class="lesson-list"></div></div>').join("") || '<div class="item">Modullar mavjud emas.</div>') +
        '</div>';
      document.querySelectorAll(".module").forEach(el => el.addEventListener("click", () => loadLessons(Number(el.dataset.module), el.querySelector(".lesson-list"))));
    } catch (_) { $("courseDetail").innerHTML = '<div class="item"><strong>Kursni yuklab bo‘lmadi.</strong></div>'; }
  }

  async function loadLessons(moduleId, target) {
    if (!target) return;
    target.innerHTML = "<small>Darslar yuklanmoqda...</small>";
    try {
      const lessons = await api("/students/courses/" + currentCourse + "/modules/" + moduleId + "/lessons", {timeout:60000});
      target.innerHTML = (Array.isArray(lessons) ? lessons : []).map(l =>
        '<div class="item lesson" style="margin-top:8px" data-lesson="' + Number(l.id) + '">' +
        '<strong>' + esc(l.title) + (l.completed ? " ✅" : "") + '</strong><small>' + esc(l.content || "") + '</small>' +
        (l.video_url ? '<a class="small-btn" target="_blank" rel="noopener" href="' + esc(l.video_url) + '">▶ Video</a>' : '') +
        '</div>'
      ).join("") || "<small>Darslar mavjud emas.</small>";
      target.querySelectorAll(".lesson").forEach(el => el.addEventListener("click", e => {
        if (!e.target.closest("a")) openLesson(moduleId, Number(el.dataset.lesson), lessons.find(x => Number(x.id) === Number(el.dataset.lesson)));
      }));
    } catch (_) { target.innerHTML = "<small>Darslar hozircha yuklanmadi.</small>"; }
  }

  async function openLesson(moduleId, lessonId, lesson) {
    const modal = makeModal("Dars");
    const body = modal.querySelector(".modal-body");
    body.innerHTML =
      '<h3>' + esc(lesson?.title || "Dars") + '</h3>' +
      '<div class="item"><p>' + esc(lesson?.content || "Kontent mavjud emas.") + '</p></div>' +
      '<button class="primary-btn" id="markReadBtn">Darsni o‘qildi deb belgilash</button>';
    modal.querySelector("#markReadBtn").onclick = async () => {
      try {
        const res = await api("/students/courses/" + currentCourse + "/modules/" + moduleId + "/lessons/" + lessonId + "/read", {method:"POST",timeout:60000});
        if (res.has_quiz) {
          await openQuiz(moduleId, lessonId, modal);
        } else {
          await completeLesson(moduleId, lessonId, modal);
        }
      } catch (e) { alert("Darsni belgilash hozircha bajarilmadi."); }
    };
  }

  async function openQuiz(moduleId, lessonId, parentModal) {
    try {
      const quizzes = await api("/students/courses/" + currentCourse + "/modules/" + moduleId + "/lessons/" + lessonId + "/quiz", {timeout:60000});
      const questions = Array.isArray(quizzes) ? quizzes : [];
      const body = parentModal.querySelector(".modal-body");
      body.innerHTML = '<h3>Yakuniy tekshiruv</h3>' +
        questions.map(q => '<div class="question"><strong>' + esc(q.question) + '</strong>' +
          [["A",q.option_a],["B",q.option_b],["C",q.option_c],["D",q.option_d]].filter(x=>x[1]).map(x=>'<label class="option"><input type="radio" name="quiz_'+Number(q.id)+'" value="'+x[0]+'"> '+esc(x[1])+'</label>').join("") +
        '</div>').join("") +
        '<button class="primary-btn" id="submitQuizBtn">Tekshirish</button>';
      parentModal.querySelector("#submitQuizBtn").onclick = async () => {
        const answers = {};
        questions.forEach(q => {
          const v = parentModal.querySelector('input[name="quiz_' + Number(q.id) + '"]:checked');
          if (v) answers[String(q.id)] = v.value;
        });
        try {
          const result = await api("/students/courses/" + currentCourse + "/modules/" + moduleId + "/lessons/" + lessonId + "/quiz", {method:"POST",body:JSON.stringify(answers),timeout:60000});
          alert(result.message || "Tekshirildi");
          if (result.passed) await completeLesson(moduleId, lessonId, parentModal);
        } catch (e) { alert(e.message || "Quizni tekshirishda xatolik."); }
      };
    } catch (_) { parentModal.querySelector(".modal-body").innerHTML = "<div class='item'>Bu dars uchun tekshiruv mavjud emas.</div>"; }
  }

  async function completeLesson(moduleId, lessonId, parentModal) {
    try {
      const result = await api("/students/courses/" + currentCourse + "/modules/" + moduleId + "/lessons/" + lessonId + "/complete", {method:"POST",timeout:60000});
      parentModal.remove();
      showStatus((result.message || "Dars tugallandi") + " • Progress: " + Number(result.progress || 0) + "%");
      loadCourses();
      loadHomeCourses();
    } catch (e) { alert(e.message || "Darsni yakunlash hozircha bajarilmadi."); }
  }

  async function loadHomework() {
    $("homeworkList").innerHTML = '<div class="item">Uy vazifalari yuklanmoqda...</div>';
    try {
      const [tasks, subs] = await Promise.all([
        api("/homework/student", {timeout:60000}),
        api("/homework/student/submissions", {timeout:60000})
      ]);
      const subMap = new Map((Array.isArray(subs) ? subs : []).map(x => [Number(x.homework_id), x]));
      const list = Array.isArray(tasks) ? tasks : [];
      $("homeworkList").innerHTML = list.map(h => {
        const s = subMap.get(Number(h.id));
        return '<div class="item"><strong>' + esc(h.title || "Uy vazifasi") + '</strong><small>' + esc(h.description || "") + '</small>' +
          (s ? '<small>Holat: ' + esc(s.status || "topshirilgan") + ' • Baho: ' + esc(s.score ?? "—") + '</small>' :
          '<textarea class="hw-answer" data-id="' + Number(h.id) + '" rows="4" placeholder="Javobingiz..."></textarea><button class="primary-btn submit-hw" data-id="' + Number(h.id) + '" type="button">Topshirish</button>') + '</div>';
      }).join("") || '<div class="item">Hozircha uy vazifasi yo‘q.</div>';
      document.querySelectorAll(".submit-hw").forEach(b => b.onclick = () => submitHomework(Number(b.dataset.id)));
    } catch (_) { renderEmpty("homeworkList", "Uy vazifalari hozircha yuklanmadi."); }
  }

  async function submitHomework(id) {
    const input = document.querySelector('.hw-answer[data-id="' + id + '"]');
    if (!input?.value.trim()) return alert("Javobni kiriting.");
    try {
      await api("/homework/" + id + "/submit?answer=" + encodeURIComponent(input.value.trim()), {method:"POST",timeout:60000});
      await loadHomework();
      showStatus("Uy vazifasi topshirildi.");
    } catch (e) { alert(e.message || "Uy vazifasini topshirib bo‘lmadi."); }
  }

  async function loadRanking() {
    $("rankingList").innerHTML = '<div class="item">Reyting yuklanmoqda...</div>';
    try {
      const list = await api("/students/ranking", {timeout:60000});
      const arr = Array.isArray(list) ? list : [];
      $("rankingList").innerHTML = arr.map(x => '<div class="item"><strong>#' + Number(x.rank || 0) + ' · ' + esc(x.full_name) + '</strong><small>XP: ' + Number(x.xp || 0) + ' · Level: ' + Number(x.level || 1) + ' · Coin: ' + Number(x.coins || 0) + '</small></div>').join("") || '<div class="item">Reyting bo‘sh.</div>';
    } catch (_) { renderEmpty("rankingList", "Reyting hozircha yuklanmadi."); }
  }

  async function loadRewards() {
    $("rewardsList").innerHTML = '<div class="card-grid-item">Mukofotlar yuklanmoqda...</div>';
    try {
      const data = await api("/students/rewards", {timeout:60000});
      const arr = Array.isArray(data.rewards) ? data.rewards : [];
      $("rewardsList").innerHTML = arr.map(x => '<div class="card-grid-item"><strong>' + esc(x.name) + '</strong><p>' + esc(x.description || "") + '</p><div class="price">🪙 ' + Number(x.coin_price || x.price || 0) + ' Coin</div><button class="primary-btn buy-reward" data-id="' + Number(x.id) + '" type="button">Sotib olish</button></div>').join("") || '<div class="card-grid-item">Hozircha mukofot yo‘q.</div>';
      document.querySelectorAll(".buy-reward").forEach(b => b.onclick = () => buyReward(Number(b.dataset.id)));
    } catch (_) { renderEmpty("rewardsList", "Mukofotlar hozircha yuklanmadi."); }
  }

  async function buyReward(id) {
    try { await api("/students/rewards/" + id + "/buy", {method:"POST",timeout:60000}); alert("Buyurtma yuborildi."); loadRewards(); loadHomeRewards(); }
    catch(e){ alert(e.message || "Mukofotni sotib olib bo‘lmadi."); }
  }

  async function loadBooks() {
    $("booksList").innerHTML = '<div class="card-grid-item">Kitoblar yuklanmoqda...</div>';
    try {
      const data = await api("/students/books", {timeout:60000});
      const arr = Array.isArray(data?.books) ? data.books : [];
      $("booksList").innerHTML = arr.map(x => '<div class="card-grid-item"><strong>' + esc(x.title || x.name) + '</strong><p>' + esc(x.description || "") + '</p><div class="price">🪙 ' + Number(x.coin_price || x.price || 0) + ' Coin</div><button class="primary-btn buy-book" data-id="' + Number(x.id) + '" type="button">Olish</button></div>').join("") || '<div class="card-grid-item">Hozircha kitob yo‘q.</div>';
      document.querySelectorAll(".buy-book").forEach(b => b.onclick = () => buyBook(Number(b.dataset.id)));
    } catch (_) { renderEmpty("booksList", "Kitoblar hozircha yuklanmadi."); }
  }

  async function buyBook(id) {
    try { await api("/students/books/" + id + "/buy", {method:"POST",timeout:60000}); alert("Buyurtma yuborildi."); loadBooks(); }
    catch(e){ alert(e.message || "Kitobni olib bo‘lmadi."); }
  }

  async function loadNotifications() {
    $("notificationsList").innerHTML = '<div class="item">Bildirishnomalar yuklanmoqda...</div>';
    try {
      const data = await api("/students/notifications", {timeout:60000});
      const arr = Array.isArray(data) ? data : (data.notifications || []);
      $("notificationsList").innerHTML = arr.map(notificationItem).join("") || '<div class="item">Bildirishnoma yo‘q.</div>';
    } catch (_) { renderEmpty("notificationsList", "Bildirishnomalar hozircha yuklanmadi."); }
  }

  async function markNotification(id) {
    try { await api("/students/notifications/" + id + "/read", {method:"PUT",timeout:60000}); loadNotifications(); loadHomeNotifications(); }
    catch (_) {}
  }

  async function loadPodcasts() {
    $("podcastsList").innerHTML = '<div class="card-grid-item">Podcastlar yuklanmoqda...</div>';
    try {
      const arr = await api("/students/podcasts", {timeout:60000});
      $("podcastsList").innerHTML = (Array.isArray(arr) ? arr : []).map(x => '<div class="card-grid-item"><strong>' + esc(x.title) + '</strong><p>' + esc(x.description || "") + '</p>' + (x.audio_url ? '<audio controls preload="none" src="' + esc(x.audio_url) + '"></audio>' : '<small>Audio mavjud emas.</small>') + '</div>').join("") || '<div class="card-grid-item">Podcast yo‘q.</div>';
    } catch (_) { renderEmpty("podcastsList", "Podcastlar hozircha yuklanmadi."); }
  }

  async function loadTrainings() {
    $("trainingsList").innerHTML = '<div class="item">Treninglar yuklanmoqda...</div>';
    try {
      const arr = await api("/students/trainings", {timeout:60000});
      $("trainingsList").innerHTML = (Array.isArray(arr) ? arr : []).map(x => '<div class="item"><strong>' + esc(x.title) + '</strong><small>' + esc(x.description || "") + '</small><small>📍 ' + esc(x.location || "—") + ' · ' + esc(fmtDate(x.start_at)) + '</small><button class="primary-btn register-training" data-id="' + Number(x.id) + '" type="button">' + (x.registered ? "Ro‘yxatdan o‘tilgan" : "Ro‘yxatdan o‘tish") + '</button></div>').join("") || '<div class="item">Trening yo‘q.</div>';
      document.querySelectorAll(".register-training").forEach(b => { if (!b.textContent.includes("o‘tilgan")) b.onclick = () => registerTraining(Number(b.dataset.id)); });
    } catch (_) { renderEmpty("trainingsList", "Treninglar hozircha yuklanmadi."); }
  }

  async function registerTraining(id) {
    try { await api("/students/trainings/" + id + "/register", {method:"POST",timeout:60000}); alert("Treningka ro‘yxatdan o‘tildi."); loadTrainings(); }
    catch(e){ alert(e.message || "Ro‘yxatdan o‘tib bo‘lmadi."); }
  }

  async function loadExams() {
    $("examsList").innerHTML = '<div class="item">Imtihonlar yuklanmoqda...</div>';
    try {
      const arr = await api("/students/exams", {timeout:60000});
      $("examsList").innerHTML = (Array.isArray(arr) ? arr : []).map(x => '<div class="item"><strong>' + esc(x.title) + '</strong><small>' + esc(x.description || "") + '</small><small>' + esc(fmtDate(x.start_at)) + ' · 📍 ' + esc(x.location || "—") + '</small><button class="primary-btn register-exam" data-id="' + Number(x.id) + '" type="button">' + (x.registered || x.is_registered ? "Ro‘yxatdan o‘tilgan" : "Ro‘yxatdan o‘tish") + '</button></div>').join("") || '<div class="item">Imtihon yo‘q.</div>';
      document.querySelectorAll(".register-exam").forEach(b => { if (!b.textContent.includes("o‘tilgan")) b.onclick = () => registerExam(Number(b.dataset.id)); });
    } catch (_) { renderEmpty("examsList", "Imtihonlar hozircha yuklanmadi."); }
  }

  async function registerExam(id) {
    try { await api("/students/exams/" + id + "/register", {method:"POST",timeout:60000}); alert("Imtihonga ro‘yxatdan o‘tildi."); loadExams(); }
    catch(e){ alert(e.message || "Ro‘yxatdan o‘tib bo‘lmadi."); }
  }

  async function loadOnlineTests() {
    $("onlineTestsList").innerHTML = '<div class="item">Online testlar yuklanmoqda...</div>';
    try {
      const data = await api("/online-exams/available?ts=" + Date.now(), {timeout:60000});
      const arr = Array.isArray(data.exams) ? data.exams : [];
      $("onlineTestsList").innerHTML = arr.map(x =>
        '<div class="item"><strong>📝 ' + esc(x.title || "Online Test") + '</strong><p>' + esc(x.description || "Online test") + '</p><small>⏱ ' + Number(x.time_limit_minutes || 0) + ' daqiqa · 🎯 ' + Number(x.pass_score || 0) + '% · Urinish ' + Number(x.attempts_used || 0) + '/' + Number(x.max_attempts || 0) + '</small>' +
        '<button class="primary-btn start-exam" data-id="' + Number(x.id) + '" type="button" ' + (x.can_start ? "" : "disabled") + '>' + (x.can_start ? "Testni boshlash" : "Urinish tugagan") + '</button></div>'
      ).join("") || '<div class="item"><strong>Hozircha faol online testlar mavjud emas.</strong></div>';
      document.querySelectorAll(".start-exam").forEach(b => b.onclick = () => startExam(Number(b.dataset.id), b));
    } catch (e) {
      $("onlineTestsList").innerHTML = '<div class="item"><strong>Online testlar hozircha yuklanmadi.</strong><small>Qayta ochib ko‘ring.</small></div>';
    }
  }

  async function startExam(id, button) {
    if (button) { button.disabled = true; button.textContent = "Boshlanmoqda..."; }
    try {
      const data = await api("/online-exams/" + id + "/start", {method:"POST",timeout:60000});
      if (!data.deadline_at || !Array.isArray(data.questions) || !data.questions.length) throw new Error("TEST_DATA");
      examState = {id:Number(data.exam_id || id), attemptId:Number(data.attempt_id), deadline:new Date(data.deadline_at), questions:data.questions, title:data.title || "Online Test", passScore:Number(data.pass_score || 0)};
      if (Number.isNaN(examState.deadline.getTime())) throw new Error("TEST_DEADLINE");
      showExamModal();
    } catch (e) {
      if (button) { button.disabled=false; button.textContent="Testni boshlash"; }
      alert(e.message === "TEST_DATA" || e.message === "TEST_DEADLINE" ? "Test ma’lumotlari to‘liq kelmadi. Qayta urinib ko‘ring." : (e.message || "Testni boshlab bo‘lmadi."));
    }
  }

  function showExamModal() {
    const modal = makeModal(examState.title);
    const body = modal.querySelector(".modal-body");
    body.innerHTML =
      '<div class="panel-head"><div><div class="eyebrow">TEST</div><h3>' + esc(examState.title) + '</h3></div><div class="timer" id="examTimer">00:00</div></div>' +
      examState.questions.map((q,i) => '<div class="question"><strong>' + (i+1) + '. ' + esc(q.question) + '</strong>' + (Array.isArray(q.options) ? q.options : []).map((o,j) => '<label class="option"><input type="radio" name="eq_'+Number(q.id)+'" value="'+j+'"> '+esc(o)+'</label>').join("") + '</div>').join("") +
      '<button class="primary-btn" id="submitExamBtn" type="button">Testni topshirish</button>';
    $("submitExamBtn").onclick = () => submitExam(modal, false);
    tickExam();
    examTimer = setInterval(tickExam, 1000);
  }

  function tickExam() {
    if (!examState) return;
    const left = Math.max(0, examState.deadline.getTime() - Date.now());
    const s = Math.floor(left/1000);
    const el = $("examTimer");
    if (el) el.textContent = String(Math.floor(s/60)).padStart(2,"0") + ":" + String(s%60).padStart(2,"0");
    if (left <= 0) {
      clearInterval(examTimer); examTimer=null;
      submitExam(document.querySelector(".modal-backdrop"), true);
    }
  }

  async function submitExam(modal, timeout) {
    if (!examState) return;
    const answers = {};
    examState.questions.forEach(q => {
      const el = modal?.querySelector('input[name="eq_'+Number(q.id)+'"]:checked');
      if (el) answers[String(q.id)] = Number(el.value);
    });
    const btn = modal?.querySelector("#submitExamBtn"); if (btn) { btn.disabled=true; btn.textContent="Yuborilmoqda..."; }
    try {
      const r = await api("/online-exams/" + examState.id + "/submit", {method:"POST",body:JSON.stringify({answers}),timeout:60000});
      clearInterval(examTimer); examTimer=null; examState=null;
      modal?.remove();
      alert((r.passed ? "✅ O‘tdingiz" : "❌ Test yakunlandi") + "\nNatija: " + Number(r.score) + "%");
      loadOnlineTests();
    } catch (e) {
      if (timeout) {
        alert("Test vaqti tugadi.");
        modal?.remove(); examState=null;
        clearInterval(examTimer); examTimer=null;
      } else {
        if (btn) { btn.disabled=false; btn.textContent="Testni topshirish"; }
        alert(e.message || "Testni topshirib bo‘lmadi.");
      }
    }
  }

  async function loadAi() {}
  async function checkAi() {
    const task=$("aiTask").value.trim(), answer=$("aiAnswer").value.trim();
    if (!task || !answer) return alert("Topshiriq va javobni kiriting.");
    $("aiCheckBtn").disabled=true; $("aiCheckBtn").textContent="Tekshirilmoqda...";
    try {
      const data=await api("/ai/homework/check",{method:"POST",body:JSON.stringify({task,answer}),timeout:60000});
      $("aiResult").innerHTML='<h3>Natija</h3><div class="item"><strong>'+Number(data.score||0)+'%</strong><small>'+esc(data.explanation||"")+'</small></div>' +
        '<div class="item"><strong>Xatolar</strong><p>'+esc((data.mistakes||[]).join("\n"))+'</p></div><div class="item"><strong>Tavsiya</strong><p>'+esc(data.recommendation||"")+'</p></div>';
    } catch(e) { $("aiResult").innerHTML='<div class="item"><strong>AI tekshiruvini hozir amalga oshirib bo‘lmadi.</strong><small>Keyinroq qayta urinib ko‘ring.</small></div>'; }
    finally { $("aiCheckBtn").disabled=false; $("aiCheckBtn").textContent="AI orqali tekshirish"; }
  }

  function makeModal(title) {
    const root=$("modalRoot");
    root.innerHTML='<div class="modal-backdrop"><div class="modal"><div class="modal-head"><h2>'+esc(title)+'</h2><button class="icon-btn close-modal" type="button">×</button></div><div class="modal-body"></div></div></div>';
    const modal=root.firstElementChild;
    modal.querySelector(".close-modal").onclick=()=>{ if(examState){clearInterval(examTimer);examTimer=null;examState=null;} modal.remove(); };
    modal.onclick=e=>{if(e.target===modal){ if(examState){clearInterval(examTimer);examTimer=null;examState=null;} modal.remove(); }};
    return modal.querySelector(".modal");
  }

  document.addEventListener("click", e => {
    const nav=e.target.closest(".nav-item"); if(nav) go(nav.dataset.view);
    const open=e.target.closest("[data-open]"); if(open) go(open.dataset.open);
    const c=e.target.closest("[data-course]"); if(c) openCourse(Number(c.dataset.course));
    const m=e.target.closest(".mark-read"); if(m) markNotification(Number(m.dataset.id));
  });

  $("backCoursesBtn").onclick=()=>go("courses");
  $("onlineTestsBtn").onclick=()=>go("online-tests");
  $("homeOnlineBtn").onclick=()=>go("online-tests");
  $("closeOnlineBtn").onclick=()=>go("home");
  $("refreshBtn").onclick=()=>location.reload();
  $("logoutBtn").onclick=()=>{localStorage.removeItem(tokenKey);localStorage.removeItem("user_role");location.href="../index.html";};
  $("aiCheckBtn").onclick=checkAi;
  window.__studentV2LoginHandler = loginFromPanel;

  // Keyboard + visibility handling is intentionally limited to test state.
  document.addEventListener("visibilitychange",()=>{ if(document.hidden && examState) showStatus("Test oynasidan chiqildi. Test davom etmoqda.", true); });

  init();
})();