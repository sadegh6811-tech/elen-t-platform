import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useRouter } from '../context/RouterContext';
import { Cpu, Phone, Mail, MapPin } from 'lucide-react';

export const Footer: React.FC = () => {
  const { t } = useLanguage();
  const { navigate } = useRouter();

  return (
    <footer className="w-full bg-[#08080f] border-t border-white/10 mt-auto transition-colors">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          
          {/* Column 1: About Elen */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#00d4d4]/20 border border-[#00d4d4]/40 flex items-center justify-center text-[#00d4d4]">
                <Cpu className="w-4 h-4" />
              </div>
              <span className="text-xl font-extrabold text-[#00d4d4] tracking-tight">
                {t.common.brandElen}
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-sm">
              {t.footer.aboutText}
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-slate-200 tracking-wide uppercase">
              {t.footer.quickLinks}
            </h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>
                <button
                  onClick={() => navigate('#/')}
                  className="hover:text-[#00d4d4] transition-colors cursor-pointer"
                >
                  {t.nav.home}
                </button>
              </li>
              <li>
                <button
                  onClick={() => navigate('#/scan')}
                  className="hover:text-[#00d4d4] transition-colors cursor-pointer"
                >
                  {t.nav.scan}
                </button>
              </li>
              <li>
                <button
                  onClick={() => navigate('#/results')}
                  className="hover:text-[#00d4d4] transition-colors cursor-pointer"
                >
                  {t.nav.results}
                </button>
              </li>
              <li>
                <button
                  onClick={() => navigate('#/dashboard')}
                  className="hover:text-[#00d4d4] transition-colors cursor-pointer"
                >
                  {t.nav.dashboard}
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Contact */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-slate-200 tracking-wide uppercase">
              {t.footer.contact}
            </h4>
            <div className="space-y-2.5 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-[#00d4d4] shrink-0" />
                <span>{t.footer.phone}</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-[#00d4d4] shrink-0" />
                <span>{t.footer.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#00d4d4] shrink-0" />
                <span>{t.footer.location}</span>
              </div>
            </div>
          </div>

        </div>

        {/* Bottom bar with 2026 Copyright */}
        <div className="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>{t.footer.copyright}</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span className="text-[11px] px-2 py-0.5 rounded bg-white/5 border border-white/10 font-mono text-[#00d4d4]">
              v1.0.0-skeleton
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
