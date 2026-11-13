import { useEffect, useState } from "react";
import { Check, CreditCard, Loader2 } from "lucide-react";
import { Badge, Button, SectionHeader } from "./ui";
import { type Lang, type TFn } from "../lib/i18n";

const API_URL = "http://127.0.0.1:8000/api/payments/pricing";

export function PricingTab({ t, lang, locked }: { t: TFn; lang: Lang; locked: boolean }) {
  const [region, setRegion] = useState<"iran" | "global">("iran");
  const [isYearly, setIsYearly] = useState(true);
  const [pricing, setPricing] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}?region=${region}`)
      .then((res) => res.json())
      .then((data) => { setPricing(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [region]);

  const plans = [
    { id: "basic", name: "پایه", desc: "برای شروع کار و تعمیرکاران پاره‌وقت", features: ["۲۰ اسکن در ماه", "دیتابیس عمومی کدهای خطا", "تاریخچه ۳۰ روزه"] },
    { id: "pro", name: "حرفه‌ای", desc: "برای تعمیرکاران فعال و مغازه‌ها", features: ["اسکن نامحدود بردها", "دیتابیس کامل قطعات جایگزین", "پشتیبانی اولویت‌دار"], popular: true },
    { id: "enterprise", name: "سازمانی", desc: "برای تعمیرگاه‌های بزرگ و تیم‌ها", features: ["چند اکانت (Multi-user)", "دسترسی به API", "گزارش‌های تحلیلی پیشرفته"] }
  ];

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-slate-500" /></div>;
  if (!pricing) return <div className="text-center text-rose-400 p-8">خطا در دریافت قیمت‌ها از سرور</div>;

  return (
    <div className="space-y-8">
      <SectionHeader icon={CreditCard} title="پلن‌های اشتراک" subtitle="بهترین پلن را برای رشد کسب‌وکار خود انتخاب کنید." tag={<Badge tone="emerald" dot>پرداخت با تتر (USDT)</Badge>} />
      <div className="flex flex-col sm:flex-row justify-center items-center gap-6 mb-8">
        <div className="flex bg-white/[0.04] p-1 rounded-xl border border-white/10">
          <button onClick={() => setRegion("iran")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${region === "iran" ? "bg-[var(--brand)] text-[#04120d] shadow-lg" : "text-slate-400 hover:text-slate-200"}`}>🇮🇷 ویژه ایران</button>
          <button onClick={() => setRegion("global")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${region === "global" ? "bg-[var(--brand)] text-[#04120d] shadow-lg" : "text-slate-400 hover:text-slate-200"}`}>🌍 بین‌المللی</button>
        </div>
        <div className="flex items-center gap-3">
          <span className={!isYearly ? "text-slate-200 text-sm" : "text-slate-500 text-sm"}>ماهانه</span>
          <button onClick={() => setIsYearly(!isYearly)} className={`w-12 h-6 rounded-full p-1 transition-colors ${isYearly ? "bg-[var(--brand)]" : "bg-white/10"}`}>
            <div className={`w-4 h-4 rounded-full bg-white transition-transform ${isYearly ? "translate-x-6" : "translate-x-0"}`} />
          </button>
          <div className="flex items-center gap-2"><span className={isYearly ? "text-slate-200 text-sm" : "text-slate-500 text-sm"}>سالانه</span><Badge tone="amber" className="text-[10px]">۲ ماه تخفیف</Badge></div>
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const price = isYearly ? pricing[plan.id].yearly : pricing[plan.id].monthly;
          return (
            <div key={plan.id} className={`panel relative flex flex-col p-6 ${plan.popular ? "border-[var(--brand)] shadow-[0_0_30px_-10px_var(--brand)]" : ""}`}>
              {plan.popular && <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[var(--brand)] text-[#04120d] text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap">پیشنهاد ویژه</div>}
              <h3 className="text-xl font-bold text-slate-100">{plan.name}</h3>
              <p className="text-sm text-slate-400 mt-1 mb-6 h-10">{plan.desc}</p>
              <div className="mb-6 flex items-baseline gap-1"><span className="text-4xl font-bold text-[var(--brand)]">{price}</span><span className="text-sm font-medium text-slate-400">USDT</span><span className="text-xs text-slate-500">/ {isYearly ? "سال" : "ماه"}</span></div>
              <ul className="space-y-4 mb-8 flex-1">
                {plan.features.map((f) => (<li key={f} className="flex items-start gap-2 text-sm text-slate-300"><Check className="w-4 h-4 text-[var(--brand)] shrink-0 mt-0.5" /><span>{f}</span></li>))}
              </ul>
              <Button variant={plan.popular ? "primary" : "ghost"} className="w-full" disabled={locked}>انتخاب و پرداخت</Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
