export type Lang = "en" | "fa";

export type Dict = {
  errRequired: string;
  errShort: string;
  errMatch: string;
  strengthWeak: string;
  strengthFair: string;
  strengthStrong: string;
  stage1: string;
  stage2: string;
  stage3: string;
  grantedTitle: string;
  grantedSub: string;
  grantedHandle: string;
  grantedExpiry: string;
  terminate: string;
  eyebrow: string;
  working: string;
  railOnline: string;
  railNode: string;
  railLat: string;
  railTls: string;
  railScale: string;
  railBrand: string;
  langToggle: string;
  footerLegal: string;
  footerCopy: string;
  titleLogin: string;
  titleRegister: string;
  subLogin: string;
  subRegister: string;
  labelName: string;
  phName: string;
  labelUser: string;
  phUser: string;
  phUserNew: string;
  labelPass: string;
  recover: string;
  phPass: string;
  phPassNew: string;
  hidePass: string;
  showPass: string;
  strength: string;
  labelConfirm: string;
  phConfirm: string;
  remember: string;
  ctaLogin: string;
  ctaRegister: string;
  divider: string;
  passkey: string;
  hardware: string;
  toggleLogin: string;
  toggleRegister: string;
};

export const dict: Record<Lang, Dict> = {
  en: {
    errRequired: "Required",
    errShort: "Min 8 chars",
    errMatch: "Mismatch",
    strengthWeak: "WEAK",
    strengthFair: "FAIR",
    strengthStrong: "STRONG",
    stage1: "Verifying identity",
    stage2: "Establishing uplink",
    stage3: "Decrypting payload",
    grantedTitle: "Access granted",
    grantedSub: "Welcome to the orbital compute network.",
    grantedHandle: "HANDLE",
    grantedExpiry: "EXPIRES 24H",
    terminate: "TERMINATE SESSION",
    eyebrow: "SECURE ACCESS TERMINAL",
    working: "PROCESSING...",
    railOnline: "ONLINE",
    railNode: "NODE: 07",
    railLat: "LAT: 34.05N",
    railTls: "TLS: 1.3",
    railScale: "SCALE",
    railBrand: "ELEN SYSTEM",
    langToggle: "Toggle language",
    footerLegal: "Authorized access only. All activity is monitored.",
    footerCopy: "© 2026 ELEN CORP. ALL RIGHTS RESERVED.",
    titleLogin: "Welcome back",
    titleRegister: "Create account",
    subLogin: "Enter your credentials to access the terminal.",
    subRegister: "Join the orbital compute network.",
    labelName: "NAME",
    phName: "Your name",
    labelUser: "HANDLE",
    phUser: "Enter handle",
    phUserNew: "Choose handle",
    labelPass: "PASSCODE",
    recover: "Recover",
    phPass: "Enter passcode",
    phPassNew: "Create passcode",
    hidePass: "Hide password",
    showPass: "Show password",
    strength: "STRENGTH",
    labelConfirm: "CONFIRM",
    phConfirm: "Repeat passcode",
    remember: "Remember this terminal",
    ctaLogin: "INITIALIZE SEQUENCE",
    ctaRegister: "REGISTER",
    divider: "OR CONTINUE WITH",
    passkey: "Passkey",
    hardware: "Hardware key",
    toggleLogin: "LOGIN",
    toggleRegister: "REGISTER",
  },
  fa: {
    errRequired: "الزامی",
    errShort: "حداقل ۸ کاراکتر",
    errMatch: "مطابقت ندارد",
    strengthWeak: "ضعیف",
    strengthFair: "متوسط",
    strengthStrong: "قوی",
    stage1: "بررسی هویت",
    stage2: "برقراری اتصال",
    stage3: "رمزگشایی داده‌ها",
    grantedTitle: "دسترسی داده شد",
    grantedSub: "به شبکه محاسبات مداری خوش آمدید.",
    grantedHandle: "نام کاربری",
    grantedExpiry: "انقضا: ۲۴ ساعت",
    terminate: "پایان جلسه",
    eyebrow: "ترمینال دسترسی امن",
    working: "در حال پردازش...",
    railOnline: "آنلاین",
    railNode: "گره: ۰۷",
    railLat: "عرض: ۳۴.۰۵ شمالی",
    railTls: "TLS: ۱.۳",
    railScale: "مقیاس",
    railBrand: "سیستم الن",
    langToggle: "تغییر زبان",
    footerLegal: "دسترسی فقط مجاز است. تمام فعالیت‌ها رصد می‌شوند.",
    footerCopy: "© ۲۰۲۶ شرکت الن. تمام حقوق محفوظ است.",
    titleLogin: "خوش آمدید",
    titleRegister: "ایجاد حساب",
    subLogin: "برای دسترسی به ترمینال، اطلاعات خود را وارد کنید.",
    subRegister: "به شبکه محاسبات مداری بپیوندید.",
    labelName: "نام",
    phName: "نام شما",
    labelUser: "نام کاربری",
    phUser: "نام کاربری را وارد کنید",
    phUserNew: "نام کاربری انتخاب کنید",
    labelPass: "رمز عبور",
    recover: "بازیابی",
    phPass: "رمز عبور را وارد کنید",
    phPassNew: "رمز عبور ایجاد کنید",
    hidePass: "مخفی کردن رمز",
    showPass: "نمایش رمز",
    strength: "قدرت",
    labelConfirm: "تایید",
    phConfirm: "تکرار رمز عبور",
    remember: "این ترمینال را به خاطر بسپار",
    ctaLogin: "آغاز فرآیند",
    ctaRegister: "ثبت نام",
    divider: "یا ادامه دهید با",
    passkey: "کلید عبور",
    hardware: "کلید سخت‌افزاری",
    toggleLogin: "ورود",
    toggleRegister: "ثبت نام",
  },
};

export const wordmark: Record<Lang, { orbital: string; est: string }> = {
  en: { orbital: "ORBITAL COMPUTE", est: "EST. 2026" },
  fa: { orbital: "محاسبات مداری", est: "تاسیس ۲۰۲۶" },
};
