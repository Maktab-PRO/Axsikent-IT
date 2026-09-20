const API="https://axsikent-it-4.onrender.com";
const T={
uz:{loginTitle:"O‘qituvchi paneliga kirish",loginText:"Kirish ma’lumotlaringizni kiriting. Yangi o‘qituvchini faqat administrator ro‘yxatdan o‘tkazadi.",phone:"Telefon raqam",password:"Parol",enter:"Kirish",adminOnly:"Yangi o‘qituvchi akkaunti administrator tomonidan yaratiladi."},
ru:{loginTitle:"Вход в панель преподавателя",loginText:"Введите данные для входа. Нового преподавателя регистрирует только администратор.",phone:"Номер телефона",password:"Пароль",enter:"Войти",adminOnly:"Новый аккаунт преподавателя создаёт администратор."},
en:{loginTitle:"Teacher panel login",loginText:"Enter your credentials. New teachers can only be registered by an administrator.",phone:"Phone number",password:"Password",enter:"Sign in",adminOnly:"New teacher accounts are created by an administrator."}
};
let lang=localStorage.getItem("teacher_lang")||"uz";
const $=id=>document.getElementById(id);
function tr(){document.querySelectorAll("[data-i18n]").forEach(e=>{const k=e.dataset.i18n;if(T[lang][k])e.textContent=T[lang][k]});document.documentElement.lang=lang}
function setLang(v){lang=v;localStorage.setItem("teacher_lang",v);tr();updateLanguagePickers()}
function updateLanguagePickers(){document.querySelectorAll(".language-picker").forEach(p=>{const b=p.querySelector(".language-trigger");if(b)b.innerHTML=lang.toUpperCase()+" <span>⌄</span>";p.querySelectorAll("[data-lang]").forEach(x=>x.classList.toggle("selected",x.dataset.lang===lang))})}
document.querySelectorAll(".language-picker").forEach(p=>{
 const trigger=p.querySelector(".language-trigger");
 trigger.addEventListener("click",e=>{e.stopPropagation();document.querySelectorAll(".language-picker.open").forEach(x=>{if(x!==p)x.classList.remove("open")});p.classList.toggle("open")});
 p.querySelectorAll("[data-lang]").forEach(x=>x.addEventListener("click",()=>{setLang(x.dataset.lang);p.classList.remove("open")}))
});
document.addEventListener("click",()=>document.querySelectorAll(".language-picker.open").forEach(x=>x.classList.remove("open")));
tr();updateLanguagePickers();
async function teacherLogin(e){
 e.preventDefault();
 const msg=$("teacherLoginMessage"),btn=document.querySelector('#teacherLoginForm button[type="submit"]');
 const phone=$("teacherPhone").value.trim(),password=$("teacherPassword").value;
 msg.textContent="";
 if(!phone||!password){msg.textContent="Telefon raqam va parolni kiriting.";return}
 if(btn){btn.disabled=true;btn.setAttribute("aria-busy","true")}
 try{
  const r=await fetch(API+"/teachers/login",{method:"POST",mode:"cors",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone,password})});
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(d.detail||"Telefon raqam yoki parol noto'g'ri");
  if(!d.access_token)throw Error("Kirish tasdiqlanmadi.");
  localStorage.setItem("teacher_access_token",d.access_token);
  if(d.teacher_id!=null)localStorage.setItem("teacher_id",d.teacher_id);
  location.href="teacher.html";
 }catch(err){msg.textContent=err.message||"Kirishda xatolik yuz berdi"}
 finally{if(btn){btn.disabled=false;btn.removeAttribute("aria-busy")}}
}
$("teacherLoginForm").addEventListener("submit",teacherLogin);
$("teacherLoginLogo").addEventListener("click",()=>location.reload());
