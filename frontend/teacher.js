const API="https://axsikent-it-4.onrender.com";
const T={uz:{loginTitle:"O‘qituvchi paneliga kirish",loginText:"Kirish ma’lumotlaringizni kiriting. Yangi o‘qituvchini faqat administrator ro‘yxatdan o‘tkazadi.",phone:"Telefon raqam",password:"Parol",enter:"Kirish",adminOnly:"Yangi o‘qituvchi akkaunti administrator tomonidan yaratiladi.",dashboard:"Dashboard",students:"O‘quvchilar",lessons:"Darslar",quiz:"Quiz / Savollar",attendance:"Davomat",grades:"Baholar",courses:"Fanlar / Kurslar",support:"Texnik yordam",command:"TEACHER COMMAND CENTER",welcome:"Xush kelibsiz, o‘qituvchi",dashboardText:"O‘quvchilar, darslar, davomat va baholarni bir markazdan boshqaring.",operational:"System Operational",myStudents:"Mening o‘quvchilarim",myLessons:"Darslar",todayAttendance:"Bugungi davomat",pendingGrades:"Kutilayotgan baholar",quick:"Tezkor boshqaruv",markAttendance:"Davomat belgilash",gradeStudent:"O‘quvchiga baho qo‘yish",assignLesson:"Dars biriktirish",addQuiz:"Quiz savol qo‘shish",teacherInfo:"O‘qituvchi ma’lumoti",fullName:"Ism-familiya",subject:"Fan",studentsText:"Sizga biriktirilgan o‘quvchilarni boshqaring.",refresh:"Yangilash",loadingStudents:"O‘quvchilar yuklanmoqda...",lessonsText:"Dars materiallarini va o‘quvchilarga biriktirishni boshqaring.",student:"O‘quvchi",choose:"Tanlang",course:"Fan / Kurs",lessonTitle:"Dars nomi",lessonLink:"Video / material havolasi",assign:"Biriktirish",lesson:"Dars",quizText:"Darsga test savollarini joylang va to‘g‘ri javobni belgilang.",question:"Savol",correct:"To‘g‘ri javob",saveQuiz:"Quizni saqlash",attendanceText:"Har bir o‘quvchi uchun keldi / kelmadi holatini belgilang.",gradesText:"O‘quvchilarga baho va izoh qoldiring.",score:"Baho (0–100)",comment:"Izoh",saveGrade:"Bahoni saqlash",coursesText:"O‘qituvchi sifatida sizga biriktirilgan fanlar shu yerda.",subjectAssigned:"Faningiz administrator tomonidan biriktiriladi.",supportText:"Platforma bo‘yicha yordam kerak bo‘lsa, biz bilan bog‘laning.",call:"Qo‘ng‘iroq",footerText:"Zamonaviy ta’lim va kuchli kelajak sari.",creator:"Platforma yaratuvchisi"},ru:{loginTitle:"Вход в панель преподавателя",loginText:"Введите данные для входа. Нового преподавателя регистрирует только администратор.",phone:"Номер телефона",password:"Пароль",enter:"Войти",adminOnly:"Новый аккаунт преподавателя создаёт администратор.",dashboard:"Панель",students:"Ученики",lessons:"Уроки",quiz:"Тест / Вопросы",attendance:"Посещаемость",grades:"Оценки",courses:"Предметы / Курсы",support:"Поддержка",command:"TEACHER COMMAND CENTER",welcome:"Добро пожаловать, преподаватель",dashboardText:"Управляйте учениками, уроками, посещаемостью и оценками из одного центра.",operational:"Система работает",myStudents:"Мои ученики",myLessons:"Уроки",todayAttendance:"Посещаемость сегодня",pendingGrades:"Ожидающие оценки",quick:"Быстрые действия",markAttendance:"Отметить посещаемость",gradeStudent:"Поставить оценку",assignLesson:"Назначить урок",addQuiz:"Добавить вопрос",teacherInfo:"Данные преподавателя",fullName:"Имя и фамилия",subject:"Предмет",studentsText:"Управляйте назначенными вам учениками.",refresh:"Обновить",loadingStudents:"Загрузка учеников...",lessonsText:"Управляйте материалами и назначением уроков.",student:"Ученик",choose:"Выберите",course:"Предмет / Курс",lessonTitle:"Название урока",lessonLink:"Ссылка на видео / материал",assign:"Назначить",lesson:"Урок",quizText:"Добавляйте тестовые вопросы к уроку и отмечайте правильный ответ.",question:"Вопрос",correct:"Правильный ответ",saveQuiz:"Сохранить тест",attendanceText:"Отмечайте пришёл / не пришёл для каждого ученика.",gradesText:"Оставляйте оценки и комментарии ученикам.",score:"Оценка (0–100)",comment:"Комментарий",saveGrade:"Сохранить оценку",coursesText:"Предметы, назначенные вам администратором.",subjectAssigned:"Ваш предмет назначается администратором.",supportText:"Если нужна помощь с платформой, свяжитесь с нами.",call:"Позвонить",footerText:"Современное образование и сильное будущее.",creator:"Создатель платформы"},en:{loginTitle:"Teacher panel login",loginText:"Enter your credentials. New teachers can only be registered by an administrator.",phone:"Phone number",password:"Password",enter:"Sign in",adminOnly:"New teacher accounts are created by an administrator.",dashboard:"Dashboard",students:"Students",lessons:"Lessons",quiz:"Quiz / Questions",attendance:"Attendance",grades:"Grades",courses:"Subjects / Courses",support:"Technical support",command:"TEACHER COMMAND CENTER",welcome:"Welcome, teacher",dashboardText:"Manage students, lessons, attendance and grades from one command center.",operational:"System Operational",myStudents:"My students",myLessons:"Lessons",todayAttendance:"Today's attendance",pendingGrades:"Pending grades",quick:"Quick actions",markAttendance:"Mark attendance",gradeStudent:"Grade a student",assignLesson:"Assign lesson",addQuiz:"Add quiz question",teacherInfo:"Teacher information",fullName:"Full name",subject:"Subject",studentsText:"Manage the students assigned to you.",refresh:"Refresh",loadingStudents:"Loading students...",lessonsText:"Manage lesson materials and assignments.",student:"Student",choose:"Choose",course:"Subject / Course",lessonTitle:"Lesson title",lessonLink:"Video / material link",assign:"Assign",lesson:"Lesson",quizText:"Add quiz questions to a lesson and mark the correct answer.",question:"Question",correct:"Correct answer",saveQuiz:"Save quiz",attendanceText:"Mark each student as present or absent.",gradesText:"Leave grades and comments for students.",score:"Score (0–100)",comment:"Comment",saveGrade:"Save grade",coursesText:"Subjects assigned to you by the administrator.",subjectAssigned:"Your subject is assigned by the administrator.",supportText:"Contact us if you need help with the platform.",call:"Call",footerText:"Modern education and a stronger future.",creator:"Platform creator"}};
let lang=localStorage.getItem("teacher_lang")||"uz", token=localStorage.getItem("teacher_access_token"), teacher=null, students=[];
const $=id=>document.getElementById(id);
function tr(){document.querySelectorAll("[data-i18n]").forEach(e=>{const k=e.dataset.i18n;if(T[lang][k])e.textContent=T[lang][k]});document.documentElement.lang=lang}
function setLang(v){lang=v;localStorage.setItem("teacher_lang",v);tr();updateLanguagePickers();}
function updateLanguagePickers(){
  document.querySelectorAll(".language-picker").forEach(p=>{
    const b=p.querySelector(".language-trigger"); if(b)b.innerHTML=lang.toUpperCase()+" <span>⌄</span>";
    p.querySelectorAll("[data-lang]").forEach(x=>x.classList.toggle("selected",x.dataset.lang===lang));
  });
}
document.querySelectorAll(".language-picker").forEach(p=>{
  const trigger=p.querySelector(".language-trigger");
  trigger.addEventListener("click",e=>{e.stopPropagation();document.querySelectorAll(".language-picker.open").forEach(x=>{if(x!==p)x.classList.remove("open")});p.classList.toggle("open");});
  p.querySelectorAll("[data-lang]").forEach(x=>x.addEventListener("click",()=>{setLang(x.dataset.lang);p.classList.remove("open");}));
});
document.addEventListener("click",()=>document.querySelectorAll(".language-picker.open").forEach(x=>x.classList.remove("open")));
tr();updateLanguagePickers();
async function teacherLogin(e){
  e.preventDefault();
  const msg=$("teacherLoginMessage");
  const btn=document.querySelector('#teacherLoginForm button[type="submit"]');
  const phone=$("teacherPhone").value.trim();
  const password=$("teacherPassword").value;
  msg.textContent="";
  if(!phone||!password){msg.textContent="Telefon raqam va parolni kiriting.";return}
  if(btn){btn.disabled=true;btn.setAttribute("aria-busy","true")}
  try{
    const r=await fetch(API+"/teachers/login",{method:"POST",mode:"cors",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone,password})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(d.detail||"Telefon raqam yoki parol noto'g'ri");
    if(!d.access_token)throw Error("Kirish tasdiqlanmadi.");
    token=d.access_token;
    localStorage.setItem("teacher_access_token",token);
    if(d.teacher_id!=null)localStorage.setItem("teacher_id",d.teacher_id);
    $("teacherLogin").hidden=true;
    $("teacherApp").hidden=false;
    await loadTeacherData();
  }catch(err){
    msg.textContent=err.message||"Kirishda xatolik yuz berdi";
  }finally{
    if(btn){btn.disabled=false;btn.removeAttribute("aria-busy")}
  }
}
$("teacherLoginForm").addEventListener("submit",teacherLogin);
function logout(){localStorage.removeItem("teacher_access_token");localStorage.removeItem("teacher_id");location.reload()}
$("logoutBtn").addEventListener("click",logout);
async function refreshTeacherPanel(){
  if(!token)return;
  const b=$("teacherRefreshBtn"); if(b){b.disabled=true;b.classList.add("is-refreshing")}
  try{await boot()}finally{if(b){b.disabled=false;b.classList.remove("is-refreshing")}}
}
$("teacherRefreshBtn")?.addEventListener("click",refreshTeacherPanel);
$("teacherBrandLogo")?.addEventListener("click",refreshTeacherPanel);
$("teacherLoginLogo")?.addEventListener("click",()=>location.reload());
function nav(section){document.querySelectorAll(".side-item").forEach(b=>b.classList.toggle("active",b.dataset.section===section));document.querySelectorAll(".teacher-section").forEach(s=>s.classList.toggle("active",s.id==="section-"+section));if(section==="students"||section==="attendance"||section==="grades"||section==="dashboard")loadTeacherData()}
document.querySelectorAll(".side-item,[data-section]").forEach(b=>b.addEventListener("click",()=>nav(b.dataset.section)));
async function api(path,opt={}){const r=await fetch(API+path,{...opt,headers:{"Content-Type":"application/json","Authorization":"Bearer "+token,...(opt.headers||{})}});const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.detail||"Server xatosi");return d}
async function loadTeacherData(){try{const d=await api("/teachers/me/dashboard");teacher=d.teacher;students=d.students||[];$("teacherName").textContent=teacher.full_name;$("teacherSubject").textContent=teacher.subject;$("teacherAvatar").textContent=(teacher.full_name||"A").trim().charAt(0).toUpperCase();$("infoName").textContent=teacher.full_name;$("infoSubject").textContent=teacher.subject;$("infoPhone").textContent=teacher.phone;$("statStudents").textContent=students.length;$("statLessons").textContent=d.lessons_count??0;renderStudents();fillStudentSelects()}catch(e){if(e.message.includes("Token"))logout()}}
function renderStudents(){const c=$("studentsContent");if(!students.length){c.innerHTML='<div class="empty-state"><span>◎</span><strong>'+T[lang].studentsText+'</strong></div>';return}c.innerHTML='<div class="student-table">'+students.map(s=>'<div class="student-row"><div><strong>'+esc(s.full_name)+'</strong><small>'+esc(s.phone)+'</small></div><span class="subject-tag">'+esc(s.subject||teacher.subject)+'</span></div>').join("")+'</div>'}
function fillStudentSelects(){["lessonStudent","gradeStudent"].forEach(id=>{const el=$(id);if(!el)return;el.innerHTML='<option value="">'+T[lang].choose+'</option>'+students.map(s=>'<option value="'+s.id+'">'+esc(s.full_name)+'</option>').join("")})}
$("addQuizBtn").addEventListener("click",async()=>{try{const q=new URLSearchParams({lesson_id:$("quizLessonId").value,question:$("quizQuestion").value,option_a:$("quizA").value,option_b:$("quizB").value,option_c:$("quizC").value,option_d:$("quizD").value,correct_answer:$("quizCorrect").value});await api("/teachers/quiz?"+q.toString(),{method:"POST"});$("quizMessage").textContent="Quiz saqlandi."}catch(e){$("quizMessage").textContent=e.message}});
$("assignLessonBtn").addEventListener("click",async()=>{$("lessonMessage").textContent="";try{await api("/teachers/assign-lesson",{method:"POST",body:JSON.stringify({student_id:Number($("lessonStudent").value),course_id:Number($("lessonCourse").value),title:$("lessonTitle").value,video_url:$("lessonLink").value||null})});$("lessonMessage").textContent="Dars biriktirildi."}catch(e){$("lessonMessage").textContent=e.message}});
$("saveGradeBtn").addEventListener("click",async()=>{try{await api("/teachers/grades",{method:"POST",body:JSON.stringify({student_id:Number($("gradeStudent").value),score:Number($("gradeScore").value),comment:$("gradeComment").value||null})});$("gradeMessage").textContent="Baho saqlandi va o‘quvchiga ko‘rinadi."}catch(e){$("gradeMessage").textContent=e.message}});
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
async function boot(){ $("teacherLogin").hidden=true;$("teacherApp").hidden=false; if(!$("attendanceDate").value)$("attendanceDate").value=new Date().toISOString().slice(0,10);await loadTeacherData()}
if(token)boot();