const API_URL = "https://axsikent-it-backend.onrender.com";
const state = {
  token: localStorage.getItem("access_token") || "",
  student: null,
  courses: [],
  homework: [],
  submissions: [],
  ranking: [],
  rewards: [],
  books: [],
  rewardsStudent: {xp:0,coins:0,crystals:0,streak_days:0},
  currentSection: "home",
  controllers: new Map()
};

const $ = (id) => document.getElementById(id);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value){
  return String(value ?? "").replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch]));
}
function showToast(message){
  const node=$("toast"); node.textContent=message; node.classList.add("show");
  clearTimeout(showToast.timer); showToast.timer=setTimeout(()=>node.classList.remove("show"),2800);
}
function setLoginMessage(message="",ok=false){$("loginMessage").textContent=message;$("loginMessage").classList.toggle("ok",ok)}
function normalizePhone(raw){
  const digits=String(raw||"").replace(/\D/g,"");
  if(digits.length===9) return "998"+digits;
  if(digits.startsWith("8")&&digits.length===10) return "998"+digits.slice(1);
  return digits;
}
function setScreen(auth){
  $("loginScreen").hidden=!auth; $("dashboardScreen").hidden=auth;
}
function resetSession(){
  localStorage.removeItem("access_token"); localStorage.removeItem("user_role");
  state.token=""; state.student=null; setScreen(true);
}
async function api(path,{method="GET",body=null,query=null,signal=null}={}){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),20000);
  const externalSignal=signal;
  const abortExternal=()=>controller.abort();
  if(externalSignal){
    if(externalSignal.aborted) controller.abort();
    else externalSignal.addEventListener("abort",abortExternal,{once:true});
  }
  let url=API_URL+path;
  if(query){const qs=new URLSearchParams();Object.entries(query).forEach(([k,v])=>{if(v!==undefined&&v!==null)qs.set(k,v)});const s=qs.toString();if(s)url+=(url.includes("?")?"&":"?")+s}
  const headers={"Accept":"application/json"};
  const options={method,headers,cache:"no-store",signal:controller.signal};
  if(state.token) headers.Authorization="Bearer "+state.token;
  if(body!==null){headers["Content-Type"]="application/json";options.body=JSON.stringify(body)}
  try{
    const response=await fetch(url,options);
    const raw=await response.text();
    let data=null;
    try{data=raw?JSON.parse(raw):null}catch{data=raw}
    if(response.status===401){
      resetSession();
      throw new Error("SESSION_EXPIRED");
    }
    if(!response.ok){
      const detail=data?.detail || data?.message || "Amalni bajarib bo‘lmadi.";
      const err=new Error(detail); err.status=response.status; throw err;
    }
    return data;
  }catch(error){
    if(error?.name==="AbortError") throw new Error("TIMEOUT");
    if(error?.message==="Failed to fetch" || error?.name==="TypeError") {const err=new Error("NETWORK");throw err}
    throw error;
  }finally{
    clearTimeout(timer);
    if(externalSignal) externalSignal.removeEventListener("abort",abortExternal);
  }
}
function friendlyError(error){
  if(error?.message==="SESSION_EXPIRED") return "Sessiya tugagan. Qaytadan kiring.";
  if(error?.message==="TIMEOUT") return "Ulanish sekinlashdi. Qayta urinib ko‘ring.";
  if(error?.message==="NETWORK") return "Ulanish vaqtincha mavjud emas. Qayta urinib ko‘ring.";
  return error?.message || "Amalni bajarib bo‘lmadi. Qayta urinib ko‘ring.";
}
function renderLoading(container,text="Yuklanmoqda…"){if(container)container.innerHTML='<div class="loading-card">'+escapeHtml(text)+'</div>'}
function renderEmpty(container,text){if(container)container.innerHTML='<div class="empty-card">'+escapeHtml(text)+'</div>'}
function formatDate(value){
  if(!value)return "—";
  const d=new Date(value); if(Number.isNaN(d.getTime()))return String(value);
  return d.toLocaleDateString("uz-UZ",{day:"2-digit",month:"2-digit",year:"numeric"});
}
function setActiveNav(section){
  state.currentSection=section;
  $$(".nav-item[data-section]").forEach(btn=>btn.classList.toggle("active",btn.dataset.section===section));
  $$(".page-section").forEach(sec=>sec.hidden=sec.id!=="section-"+section);
  const active=$('[data-section="'+section+'"]');
  $("mobileSectionTitle").textContent=active?active.textContent.trim():section;
  $("sidebar").classList.remove("open");
  window.scrollTo({top:0,behavior:"smooth"});
}
function refreshTopProfile(){
  const name=state.student?.full_name||"O‘quvchi";
  $("topStudentName").textContent=name; $("welcomeName").textContent="Xush kelibsiz, "+name.split(" ")[0]+"! 👋";
  $("profileInitial").textContent=name.trim().charAt(0).toUpperCase()||"O";
}
function refreshBalances(){
  const g=state.rewardsStudent||{};
  $("topCoins").textContent=Number(g.coins||0);
  $("rewardsCoins").textContent=Number(g.coins||0);
  $("rewardsCrystals").textContent=Number(g.crystals||0);
  $("booksCoins").textContent=Number(g.coins||0);
}
async function loginStudent(phone,password){
  const button=$("loginButton"); button.classList.add("loading");button.disabled=true;setLoginMessage("");
  try{
    const data=await fetch(API_URL+"/students/login",{method:"POST",headers:{"Accept":"application/json","Content-Type":"application/json"},cache:"no-store",body:JSON.stringify({phone:normalizePhone(phone),password})}).then(async r=>{
      const raw=await r.text();let d={};try{d=raw?JSON.parse(raw):{}}catch{}
      if(!r.ok){throw new Error(d?.detail||"Telefon raqami yoki parol noto‘g‘ri")}
      return d;
    });
    if(!data?.access_token) throw new Error("Kirish uchun token olinmadi.");
    localStorage.setItem("access_token",data.access_token);localStorage.setItem("user_role","student");
    state.token=data.access_token;state.student={id:data.student_id,full_name:data.full_name,phone:phone,is_active:true};
    setScreen(false);refreshTopProfile();setLoginMessage("",true);showToast("Kabinet ochildi.");
    await bootstrap();
  }catch(error){setLoginMessage(error.message==="Failed to fetch"?"Ulanish vaqtincha mavjud emas. Qayta urinib ko‘ring.":(error.message||"Kirish amalga oshmadi."))}
  finally{button.classList.remove("loading");button.disabled=false}
}
async function loadStudentProfile(){
  const data=await api("/students/me"); state.student=data; refreshTopProfile(); return data;
}
async function loadCourses(){
  const data=await api("/students/courses");state.courses=Array.isArray(data)?data:[];renderCourses();renderHomeCourses();return state.courses;
}
function renderCourseCard(course){
  const progress=Math.max(0,Math.min(100,Number(course.progress)||0));
  return '<article class="course-card"><div class="course-head"><div class="course-icon">▣</div><div style="min-width:0;flex:1"><div class="course-name">'+escapeHtml(course.name||"Kurs")+'</div><div class="course-desc">'+escapeHtml(course.description||"Kurs davomida darslar va mashqlar mavjud.")+'</div></div><button class="mini-button primary" type="button" data-open-course="'+Number(course.id)+'">Ochish</button></div><div class="progress-track"><div class="progress-fill" style="width:'+progress+'%"></div></div><div class="course-meta"><span>Jarayon</span><strong>'+progress+'%</strong></div></article>';
}
function renderCourses(){
  const c=$("coursesContent");if(!state.courses.length){renderEmpty(c,"Hozircha sizga kurs biriktirilmagan.");return}
  c.innerHTML=state.courses.map(renderCourseCard).join("");
}
function renderHomeCourses(){
  const c=$("homeCourses");if(!state.courses.length){renderEmpty(c,"Hozircha kurs biriktirilmagan.");return}
  c.innerHTML=state.courses.slice(0,3).map(renderCourseCard).join("");
}
async function openCourse(courseId){
  const c=$("coursesContent");renderLoading(c,"Kurs tarkibi yuklanmoqda…");
  try{
    const modules=await api("/students/courses/"+courseId+"/modules");
    const course=state.courses.find(x=>Number(x.id)===Number(courseId));
    const header='<div class="panel-card" style="margin-bottom:12px"><div class="panel-head"><div><span class="eyebrow">KURS</span><h2>'+escapeHtml(course?.name||"Kurs")+'</h2></div><button class="ghost-button" type="button" data-reload="courses">← Kurslarga qaytish</button></div></div>';
    if(!Array.isArray(modules)||!modules.length){c.innerHTML=header+'<div class="empty-card">Bu kursda hozircha modul mavjud emas.</div>';return}
    c.innerHTML=header+modules.map((m,i)=>'<article class="module-card"><div class="module-top"><div><div class="eyebrow">MODUL '+(i+1)+'</div><div class="module-title">'+escapeHtml(m.title||"Modul")+'</div><div class="module-desc">'+escapeHtml(m.description||"")+'</div></div><strong>'+Math.max(0,Math.min(100,Number(m.progress)||0))+'%</strong></div><div class="progress-track"><div class="progress-fill" style="width:'+Math.max(0,Math.min(100,Number(m.progress)||0))+'%"></div></div><div class="lesson-list" id="module-lessons-'+m.id+'"><button class="lesson-item" type="button" data-open-module="'+courseId+'" data-module-id="'+m.id+'"><span>Darslarni ko‘rsatish</span><span>→</span></button></div></article>').join("");
  }catch(error){c.innerHTML='<div class="empty-card">'+escapeHtml(friendlyError(error))+'</div>'}
}
async function openModuleLessons(courseId,moduleId){
  const list=$("module-lessons-"+moduleId);renderLoading(list,"Darslar yuklanmoqda…");
  try{
    const lessons=await api("/students/courses/"+courseId+"/modules/"+moduleId+"/lessons");
    if(!lessons.length){renderEmpty(list,"Bu modulda hozircha dars yo‘q.");return}
    list.innerHTML=lessons.map(lesson=>'<button class="lesson-item '+(lesson.completed?"done":"")+'" type="button" data-open-lesson="'+courseId+'" data-module-id="'+moduleId+'" data-lesson-id="'+lesson.id+'"><span><b>'+escapeHtml(lesson.title||"Dars")+'</b><br><small>'+escapeHtml(lesson.completed?"Tugallangan":"Darsni ochish")+'</small></span><span class="status-dot '+(lesson.completed?"done":"")+'">'+(lesson.completed?"✓":"→")+'</span></button>').join("");
  }catch(error){renderEmpty(list,friendlyError(error))}
}
async function openLesson(courseId,moduleId,lessonId){
  const modal=$("modalRoot");modal.hidden=false;modal.innerHTML='<div class="modal-card"><div class="modal-head"><h2>Dars yuklanmoqda…</h2><button class="icon-button" data-close-modal type="button">✕</button></div></div>';
  try{
    const lessons=await api("/students/courses/"+courseId+"/modules/"+moduleId+"/lessons");
    const lesson=lessons.find(x=>Number(x.id)===Number(lessonId));
    if(!lesson)throw new Error("Dars topilmadi");
    modal.innerHTML='<div class="modal-card"><div class="modal-head"><div><span class="eyebrow">DARS</span><h2>'+escapeHtml(lesson.title||"Dars")+'</h2></div><button class="icon-button" data-close-modal type="button">✕</button></div><div class="modal-body"><div class="muted">'+escapeHtml(lesson.content||"Bu dars uchun matn kiritilmagan.")+'</div>'+(lesson.video_url?'<p><a href="'+escapeHtml(lesson.video_url)+'" target="_blank" rel="noopener noreferrer" class="text-button">Videoni ochish →</a></p>':"")+'<div class="modal-actions"><button class="primary-button" type="button" data-mark-read data-course="'+courseId+'" data-module="'+moduleId+'" data-lesson="'+lessonId+'">'+(lesson.completed?"Tugallangan":"Darsni o‘qilgan deb belgilash")+'</button></div></div></div>';
  }catch(error){modal.innerHTML='<div class="modal-card"><div class="modal-head"><h2>Darsni ochib bo‘lmadi</h2><button class="icon-button" data-close-modal type="button">✕</button></div><div class="modal-body"><p>'+escapeHtml(friendlyError(error))+'</p></div></div>'}
}
async function markRead(courseId,moduleId,lessonId){
  try{
    const result=await api("/students/courses/"+courseId+"/modules/"+moduleId+"/lessons/"+lessonId+"/read",{method:"POST"});
    showToast(result?.has_quiz?"Dars o‘qilgan. Yakuniy tekshiruv mavjud.":"Dars o‘qilgan deb belgilandi.");
    $("modalRoot").hidden=true;$("modalRoot").innerHTML="";
    await loadCourses();setActiveNav("courses");
  }catch(error){showToast(friendlyError(error))}
}
async function loadHomework(){
  const [items,subs]=await Promise.all([
    api("/homework/student"),
    api("/homework/student/submissions")
  ]);
  state.homework=Array.isArray(items)?items:[];state.submissions=Array.isArray(subs)?subs:[];
  renderHomework();renderHomeHomework();return state.homework;
}
function submissionFor(homeworkId){return state.submissions.find(s=>Number(s.homework_id)===Number(homeworkId))}
function homeworkStatus(hw,sub){
  if(sub?.status==="checked")return '<span class="status-badge">Baholandi '+Number(sub.score||0)+'/100</span>';
  if(sub?.status==="late")return '<span class="status-badge late">Kechikib yuborilgan</span>';
  if(sub?.status==="submitted")return '<span class="status-badge pending">Yuborilgan</span>';
  return '<span class="status-badge pending">Topshirilmagan</span>';
}
function renderHomework(){
  const c=$("homeworkContent");
  if(!state.homework.length){renderEmpty(c,"Hozircha uy vazifasi mavjud emas.");return}
  c.innerHTML=state.homework.map(hw=>{const sub=submissionFor(hw.id);return '<article class="homework-card"><div class="panel-head"><div><div class="homework-title">'+escapeHtml(hw.title||"Vazifa")+'</div><div class="homework-desc">'+escapeHtml(hw.description||"")+'</div></div>'+homeworkStatus(hw,sub)+'</div><div class="homework-row"><span>Muddati: '+formatDate(hw.deadline)+'</span><span>Holat: '+escapeHtml(hw.status||"active")+'</span></div><div class="homework-actions"><button class="mini-button primary" type="button" data-homework="'+hw.id+'">'+(sub?"Javobni ko‘rish":"Javob yuborish")+' →</button></div></article>'}).join("");
}
function renderHomeHomework(){
  const c=$("homeHomework");const list=state.homework.slice(0,4);
  if(!list.length){renderEmpty(c,"Hozircha uy vazifalari yo‘q.");return}
  c.innerHTML=list.map(hw=>{const sub=submissionFor(hw.id);return '<div class="homework-card"><div class="panel-head"><div><div class="homework-title">'+escapeHtml(hw.title)+'</div><div class="homework-desc">'+escapeHtml((hw.description||"").slice(0,120))+'</div></div>'+homeworkStatus(hw,sub)+'</div></div>'}).join("");
}
function openHomeworkModal(id){
  const hw=state.homework.find(x=>Number(x.id)===Number(id));if(!hw)return;
  const sub=submissionFor(id);const m=$("modalRoot");m.hidden=false;
  m.innerHTML='<div class="modal-card"><div class="modal-head"><div><span class="eyebrow">UY VAZIFASI</span><h2>'+escapeHtml(hw.title)+'</h2></div><button class="icon-button" data-close-modal type="button">✕</button></div><div class="modal-body"><p>'+escapeHtml(hw.description||"")+'</p><p>Muddati: <b>'+formatDate(hw.deadline)+'</b></p>'+ (sub?'<div class="notice-card">Sizning javobingiz: '+escapeHtml(sub.answer||"")+'<br>Holat: '+escapeHtml(sub.status||"submitted")+(sub.score!==null&&sub.score!==undefined?'<br>Baho: <b>'+Number(sub.score)+'/100</b>':'')+(sub.teacher_comment?'<br>Izoh: '+escapeHtml(sub.teacher_comment):"")+'</div>': '<label class="field"><span>Javobingiz</span><textarea id="homeworkAnswer" class="answer-area" placeholder="Javobingizni yozing..."></textarea></label><div class="modal-actions"><button class="primary-button" data-submit-homework="'+id+'" type="button">Javobni yuborish</button></div>')+'</div></div>';
}
async function submitHomework(id){
  const answer=$("homeworkAnswer")?.value?.trim();
  if(!answer){showToast("Javobni yozing.");return}
  try{
    await api("/homework/"+id+"/submit",{method:"POST",query:{answer}});
    showToast("Uy vazifasi yuborildi.");
    $("modalRoot").hidden=true;$("modalRoot").innerHTML="";
    await loadHomework();
  }catch(error){showToast(friendlyError(error))}
}
async function loadRewards(){
  const data=await api("/students/rewards");state.rewardsStudent=data?.student||state.rewardsStudent;state.rewards=Array.isArray(data?.rewards)?data.rewards:[];
  refreshBalances();renderRewards();return state.rewardsStudent;
}
function renderRewards(){
  const c=$("rewardsContent");if(!state.rewards.length){renderEmpty(c,"Hozircha mukofot mavjud emas.");return}
  c.innerHTML=state.rewards.map(p=>'<article class="product-card"><div class="product-image">'+(p.image_url?'<img src="'+escapeHtml(p.image_url)+'" alt="" style="width:100%;height:100%;object-fit:cover">':'🎁')+'</div><div class="product-body"><h3>'+escapeHtml(p.name||"Mukofot")+'</h3><p>'+escapeHtml(p.description||"")+'</p><div class="price-row"><span class="price">🪙 '+Number(p.coin_price||0)+'</span><span class="stock">'+Number(p.stock||0)+' dona</span></div><button class="primary-button" style="width:100%;margin-top:12px" type="button" data-buy-reward="'+p.id+'" '+(Number(p.stock||0)<=0||Number(state.rewardsStudent.coins||0)<Number(p.coin_price||0)?"disabled":"")+'>Buyurtma berish</button></div></article>').join("");
}
async function buyReward(id){
  try{const result=await api("/students/rewards/"+id+"/buy",{method:"POST"});state.rewardsStudent=result?.student||state.rewardsStudent;refreshBalances();renderRewards();showToast(result?.message||"Buyurtma qabul qilindi.");await loadNotifications()}
  catch(error){showToast(friendlyError(error))}
}
async function loadBooks(){
  const data=await api("/students/books");state.books=Array.isArray(data?.books)?data.books:[];refreshBalances();renderBooks();return state.books;
}
function renderBooks(){
  const c=$("booksContent");if(!state.books.length){renderEmpty(c,"Hozircha mavjud kitob yo‘q.");return}
  c.innerHTML=state.books.map(b=>'<article class="product-card"><div class="product-image">'+(b.image_url?'<img src="'+escapeHtml(b.image_url)+'" alt="" style="width:100%;height:100%;object-fit:cover">':'📚')+'</div><div class="product-body"><h3>'+escapeHtml(b.title||"Kitob")+'</h3><p>'+escapeHtml(b.description||"")+'</p><div class="price-row"><span class="price">🪙 '+Number(b.coin_price||0)+'</span><span class="stock">'+Number(b.stock||0)+' dona</span></div><button class="primary-button" style="width:100%;margin-top:12px" type="button" data-buy-book="'+b.id+'" '+(Number(b.stock||0)<=0||Number(state.rewardsStudent.coins||0)<Number(b.coin_price||0)?"disabled":"")+'>Buyurtma berish</button></div></article>').join("");
}
async function buyBook(id){
  try{const result=await api("/students/books/"+id+"/buy",{method:"POST"});state.rewardsStudent={...state.rewardsStudent,...(result?.student||{})};refreshBalances();renderBooks();showToast(result?.message||"Buyurtma qabul qilindi.");await loadNotifications()}
  catch(error){showToast(friendlyError(error))}
}
async function loadRanking(){
  const data=await api("/students/ranking");state.ranking=Array.isArray(data)?data:[];renderRanking();return state.ranking;
}
function renderRanking(){
  const c=$("rankingContent");if(!state.ranking.length){renderEmpty(c,"Reyting ma’lumoti mavjud emas.");return}
  c.innerHTML=state.ranking.map((row,i)=>'<div class="ranking-row"><div class="rank-no">#'+Number(row.rank||i+1)+'</div><div><div class="rank-name">'+escapeHtml(row.full_name||"O‘quvchi")+'</div><div class="rank-sub">Level '+Number(row.level||1)+' · 🪙 '+Number(row.coins||0)+'</div></div><div class="rank-score">'+Number(row.xp||0)+' XP</div></div>').join("");
}
async function loadNotifications(){
  try{
    const data=await api("/students/notifications");$("notificationBadge").hidden=!(Number(data?.unread||0)>0);$("notificationBadge").textContent=Number(data?.unread||0);renderNotifications(data?.notifications||[]);
    return data;
  }catch(error){renderEmpty($("notificationsContent"),friendlyError(error))}
}
function renderNotifications(items){
  const c=$("notificationsContent");if(!items.length){renderEmpty(c,"Bildirishnomalar yo‘q.");return}
  c.innerHTML=items.map(item=>'<article class="notification-item '+(item.is_read?"":"unread")+'"><div class="notification-title"><span>'+escapeHtml(item.title||"Bildirishnoma")+'</span>'+(!item.is_read?'<button class="mini-button" data-read-notification="'+item.id+'" type="button">O‘qildi</button>':"")+'</div><div class="notification-message">'+escapeHtml(item.message||"")+'</div><div class="notification-time">'+formatDate(item.created_at)+'</div></article>').join("");
}
async function markNotificationRead(id){
  try{await api("/students/notifications/"+id+"/read",{method:"PUT"});await loadNotifications()}catch(error){showToast(friendlyError(error))}
}
async function refreshDashboardStats(){
  try{
    const [g,ranking,subs]=await Promise.all([api("/students/rewards"),api("/students/ranking"),api("/homework/student/submissions")]);
    state.rewardsStudent=g?.student||state.rewardsStudent;state.ranking=Array.isArray(ranking)?ranking:state.ranking;state.submissions=Array.isArray(subs)?subs:state.submissions;
    const me=state.student?.id;const meRow=state.ranking.find(r=>Number(r.student_id)===Number(me));
    $("statXp").textContent=Number(state.rewardsStudent.xp||0);$("statRank").textContent=meRow?.rank?"#"+meRow.rank:"—";$("statHomework").textContent=state.submissions.filter(s=>s.status==="checked").length;$("statStreak").textContent=Number(state.rewardsStudent.streak_days||0)+" kun";
    refreshBalances();
  }catch(error){console.warn("dashboard stats:",friendlyError(error))}
}
async function bootstrap(){
  try{
    if(!state.token){setScreen(true);return}
    await loadStudentProfile();
    setScreen(false);
    await Promise.allSettled([loadCourses(),loadHomework(),refreshDashboardStats(),loadNotifications()]);
    renderHomeHomework();
  }catch(error){
    if(error?.message==="SESSION_EXPIRED"||error?.message.includes("token")||error?.message.includes("Student token")){resetSession();setLoginMessage("Sessiya tugagan. Qaytadan kiring.");return}
    setScreen(false);
    showToast(friendlyError(error));
  }
}
function openNotifications(){ $("notificationDrawer").hidden=false;loadNotifications() }
function closeNotifications(){ $("notificationDrawer").hidden=true }
function closeModal(){ $("modalRoot").hidden=true;$("modalRoot").innerHTML="" }

document.addEventListener("click",async (event)=>{
  const go=event.target.closest("[data-go]");if(go){setActiveNav(go.dataset.go);return}
  const nav=event.target.closest(".nav-item[data-section]");if(nav){setActiveNav(nav.dataset.section);return}
  const openCourseBtn=event.target.closest("[data-open-course]");if(openCourseBtn){setActiveNav("courses");openCourse(openCourseBtn.dataset.openCourse);return}
  const openModuleBtn=event.target.closest("[data-open-module]");if(openModuleBtn){openModuleLessons(openModuleBtn.dataset.openModule,openModuleBtn.dataset.moduleId);return}
  const openLessonBtn=event.target.closest("[data-open-lesson]");if(openLessonBtn){openLesson(openLessonBtn.dataset.openLesson,openLessonBtn.dataset.moduleId,openLessonBtn.dataset.lessonId);return}
  const readBtn=event.target.closest("[data-mark-read]");if(readBtn){markRead(readBtn.dataset.course,readBtn.dataset.module,readBtn.dataset.lesson);return}
  const hw=event.target.closest("[data-homework]");if(hw){openHomeworkModal(hw.dataset.homework);return}
  const submitHw=event.target.closest("[data-submit-homework]");if(submitHw){submitHomework(submitHw.dataset.submitHomework);return}
  const buyRewardBtn=event.target.closest("[data-buy-reward]");if(buyRewardBtn){buyReward(buyRewardBtn.dataset.buyReward);return}
  const buyBookBtn=event.target.closest("[data-buy-book]");if(buyBookBtn){buyBook(buyBookBtn.dataset.buyBook);return}
  const readNotif=event.target.closest("[data-read-notification]");if(readNotif){markNotificationRead(readNotif.dataset.readNotification);return}
  if(event.target.closest("[data-close-notifications]")){closeNotifications();return}
  if(event.target.closest("[data-close-modal]")||event.target=== $("modalRoot")){closeModal();return}
  const reload=event.target.closest("[data-reload]");if(reload){
    const target=reload.dataset.reload;
    if(target==="courses")loadCourses();
    if(target==="homework")loadHomework();
    return;
  }
});
$("loginForm").addEventListener("submit",event=>{event.preventDefault();loginStudent($("loginPhone").value,$("loginPassword").value)});
$("logoutButton").addEventListener("click",()=>{resetSession();setLoginMessage("Siz kabinetdan chiqdingiz.",true)});
$("notificationButton").addEventListener("click",openNotifications);
$("openSidebar").addEventListener("click",()=>$("sidebar").classList.add("open"));
$("closeSidebar").addEventListener("click",()=>$("sidebar").classList.remove("open"));
$("profileButton").addEventListener("click",()=>showToast(state.student?.full_name||"O‘quvchi"));
window.addEventListener("keydown",event=>{if(event.key==="Escape"){closeModal();closeNotifications();$("sidebar").classList.remove("open")}});

(async function init(){
  setScreen(!state.token);
  if(state.token) await bootstrap();
})();