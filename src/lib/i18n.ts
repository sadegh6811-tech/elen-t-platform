export type Lang = "en" | "fa";

export const dict = {
  en: {
    logo: "Elen-k Health OS", online: "Backend Connected: ONLINE", offline: "Backend: DEMO MODE",
    badge: "Symbolic Discovery Engine v2.0", title1: "Discover the Hidden Laws of", title2: "Health & Science.",
    subtitle: "Powered by Elen-t Hybrid Architecture.",
    desc: "Feed raw experimental data. Our orchestrator selects the optimal engine and returns interpretable, closed-form equations.",
    cta: "Start Discovery", docs: "Read Docs", stats: [["99.8%", "Peak R²"], ["3", "Engines"], ["<3s", "Avg. Runtime"]],
    dashTitle: "Discovery Console", dashSub: "Upload a dataset, choose a domain, and let the orchestrator do the rest.",
    input: "Input Data", domain: "Domain",
    domains: { 
      physics_all: "Physics (All Dimensions)",
      biology: "Biology (DNA)", 
      drug: "Drug Discovery (High-Dim)",
      chemistry: "Chemistry (Quantum)",
      finance: "Finance (Time Series)"
    },
    placeholder: "Paste JSON or CSV data here...\n\nX0,X1,y\n1.0,2.0,5.5", drop: "Drop a .json or .csv file, or click to browse",
    loaded: "Loaded", run: "Run Engine", loading: "Orchestrator is analyzing data...", results: "Results",
    awaiting: "Awaiting input. Run the engine to reveal discovered laws.",
    engine: "Engine Used", r2: "R² Score", formula: "Discovered Formula", runtime: "Runtime",
    copy: "Copy", copied: "Copied", footer: "© 2026 Elen-k Health OS. All rights reserved.",
    links: ["Documentation", "API Reference", "JOSS Paper"], sample: "Load sample",
  },
  fa: {
    logo: "Elen-k Health OS", online: "اتصال به سرور: آنلاین", offline: "سرور: حالت نمایشی",
    badge: "موتور کشف نمادین نسخه ۲٫۰", title1: "کشف قوانین پنهان", title2: "سلامت و علم.",
    subtitle: "با اتکا به معماری ترکیبی Elen-t.",
    desc: "داده‌های خام آزمایشگاهی را وارد کنید. ارکستراتور بهترین موتور را انتخاب کرده و معادلات صریح و تفسیرپذیر ارائه می‌دهد.",
    cta: "شروع کشف", docs: "مستندات", stats: [["۹۹٫۸٪", "بیشترین R²"], ["۳", "موتور"], ["<۳ث", "زمان میانگین"]],
    dashTitle: "کنسول کشف", dashSub: "داده را بارگذاری کنید، حوزه را انتخاب کنید و بقیه را به ارکستراتور بسپارید.",
    input: "داده ورودی", domain: "حوزه",
    domains: { 
      physics_all: "فیزیک (تمام ابعاد)",
      biology: "زیست‌شناسی (DNA)", 
      drug: "کشف دارو (پربعد)",
      chemistry: "شیمی (کوانتومی)",
      finance: "مالی (سری زمانی)"
    },
    placeholder: "داده JSON یا CSV را اینجا وارد کنید...\n\nX0,X1,y\n1.0,2.0,5.5", drop: "فایل .json یا .csv را رها کنید یا برای انتخاب کلیک کنید",
    loaded: "بارگذاری شد", run: "اجرای موتور", loading: "ارکستراتور در حال تحلیل داده است...", results: "نتایج",
    awaiting: "در انتظار ورودی. موتور را اجرا کنید تا قوانین کشف‌شده نمایش داده شوند.",
    engine: "موتور استفاده‌شده", r2: "امتیاز R²", formula: "فرمول کشف‌شده", runtime: "زمان اجرا",
    copy: "کپی", copied: "کپی شد", footer: "© ۲۰۲۶ Elen-k Health OS. تمامی حقوق محفوظ است.",
    links: ["مستندات", "مرجع API", "مقاله JOSS"], sample: "داده نمونه",
  },
} as const;

export type Dict = typeof dict.en | typeof dict.fa;
