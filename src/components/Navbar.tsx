import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useRouter } from '../context/RouterContext';
import { Cpu, Menu, X, LogIn, ChevronDown, CheckCircle2, LogOut } from 'lucide-react';

export const Navbar: React.FC<{ onLogout?: () => void }> = ({ onLogout }) => {
  const { lang, toggleLang, t } = useLanguage();
  const { route, navigate } = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const token = localStorage.getItem("elen_token");
  const shopName = localStorage.getItem("elen_shop_name") || "تعمیرگاه من";

  const navLinks = [
    { label: t.nav.home, hash: '#/', active: route === 'home' },
    { label: t.nav.scan, hash: '#/scan', active: route === 'scan' },
    { label: t.nav.dashboard, hash: '#/dashboard', active: route === 'dashboard' },
    { label: lang === 'fa' ? 'اشتراک' : 'Pricing', hash: '#/pricing', active: route === 'pricing' },
  ];

  const handleNavClick = (hash: string) => { navigate(hash); setMobileMenuOpen(false); };

  return (
    <>
      <header className="sticky top-0 z-50 w-full bg-[#0a0a12]/90 backdrop-blur-md border-b border-white/10 transition-colors">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => handleNavClick('#/')} className="flex items-center gap-2 group text-left cursor-pointer">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#00d4d4]/20 to-[#00d4d4]/40 border border-[#00d4d4]/50 flex items-center justify-center text-[#00d4d4] shadow-[0_0_15px_rgba(0,212,212,0.3)] transition-transform group-hover:scale-105">
                <Cpu className="w-5 h-5 text-[#00d4d4]" />
              </div>
              <span className="text-[20px] font-extrabold tracking-tight text-[#00d4d4]">Elen-d</span>
            </button>
            <nav className="hidden md:flex items-center gap-1 mx-6">
              {navLinks.map((item) => (
                <button key={item.hash} onClick={() => handleNavClick(item.hash)} className={`px-3.5 py-1.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${item.active ? 'bg-white/10 text-[#00d4d4] shadow-sm' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={toggleLang} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#12121f] border border-white/15 text-xs font-bold text-slate-200 hover:border-[#00d4d4]/60 hover:text-[#00d4d4] transition-all cursor-pointer">
              <span className={lang === 'fa' ? 'text-[#00d4d4] font-black' : 'text-slate-400'}>FA</span>
              <span className="text-white/20">|</span>
              <span className={lang === 'en' ? 'text-[#00d4d4] font-black' : 'text-slate-400'}>EN</span>
            </button>
            
            {token ? (
              <div className="relative">
                <button onClick={() => setUserDropdownOpen(!userDropdownOpen)} className="flex items-center gap-2 py-1.5 px-3 rounded-xl bg-[#12121f] border border-white/10 text-xs font-medium text-slate-200 hover:border-white/30 transition-all cursor-pointer">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-[#ff8c42] to-[#00d4d4] flex items-center justify-center text-black font-bold text-[10px]">{shopName.charAt(0)}</div>
                  <span className="hidden sm:inline font-semibold">{shopName}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>
                {userDropdownOpen && (
                  <div className={`absolute top-full mt-2 w-48 bg-[#12121f] border border-white/15 rounded-xl shadow-2xl p-2 z-50 text-xs ${lang === 'fa' ? 'left-0' : 'right-0'}`}>
                    <div className="px-3 py-2 border-b border-white/10 mb-1">
                      <p className="font-bold text-slate-100">{shopName}</p>
                    </div>
                    <button onClick={() => { if(onLogout) onLogout(); setUserDropdownOpen(false); }} className="w-full text-left rtl:text-right px-3 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer flex items-center gap-2">
                      <LogOut className="w-3.5 h-3.5" /> {t.nav.logout}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button onClick={() => navigate('#/dashboard')} className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#00d4d4] hover:bg-[#00d4d4]/90 text-black font-semibold text-xs transition-colors cursor-pointer">
                <LogIn className="w-3.5 h-3.5" /><span>{t.nav.login}</span>
              </button>
            )}
            
            <button onClick={() => setMobileMenuOpen(true)} aria-label="Toggle Menu" className="md:hidden p-2 rounded-xl bg-[#12121f] border border-white/10 text-slate-300 hover:text-white cursor-pointer">
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity" onClick={() => setMobileMenuOpen(false)} />
          <div className={`relative w-4/5 max-w-xs bg-[#12121f] border-white/10 h-full p-6 flex flex-col justify-between shadow-2xl z-10 ${lang === 'fa' ? 'mr-auto border-l' : 'ml-auto border-r'}`}>
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-[#00d4d4]/20 border border-[#00d4d4]/40 flex items-center justify-center text-[#00d4d4]"><Cpu className="w-4 h-4" /></div>
                  <span className="text-lg font-bold text-[#00d4d4]">Elen-d</span>
                </div>
                <button onClick={() => setMobileMenuOpen(false)} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 cursor-pointer"><X className="w-5 h-5" /></button>
              </div>
              <nav className="mt-6 flex flex-col gap-2">
                {navLinks.map((item) => (
                  <button key={item.hash} onClick={() => handleNavClick(item.hash)} className={`flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-colors text-right rtl:text-right ltr:text-left cursor-pointer ${item.active ? 'bg-[#00d4d4]/15 text-[#00d4d4] border border-[#00d4d4]/30' : 'text-slate-300 hover:bg-white/5'}`}>
                    <span>{item.label}</span>
                    {item.active && <CheckCircle2 className="w-4 h-4 text-[#00d4d4]" />}
                  </button>
                ))}
              </nav>
            </div>
            <div className="pt-4 border-t border-white/10 flex flex-col gap-3">
              <button onClick={toggleLang} className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-200 text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer">
                <span>{t.nav.switchLanguageLabel}</span><span className="text-[#00d4d4] font-bold">({lang.toUpperCase()})</span>
              </button>
              {token && onLogout && (
                <button onClick={() => { onLogout(); setMobileMenuOpen(false); }} className="w-full py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-medium cursor-pointer">{t.nav.logout}</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
