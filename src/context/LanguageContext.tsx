import React, { createContext, useContext, useEffect, useState, useTransition } from 'react';
import { translations, TranslationSchema } from '../translations';
import { Language } from '../types';

declare global {
  interface Window {
    __elen_lang?: Language;
  }
}

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  toggleLang: () => void;
  t: TranslationSchema;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = 'elen_lang';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as Language;
      if (stored === 'fa' || stored === 'en') {
        return stored;
      }
    } catch {
      // fallback
    }
    return 'fa';
  });

  const [, startTransition] = useTransition();

  const applyLanguageEffects = (currentLang: Language) => {
    // 1. dir
    document.documentElement.dir = currentLang === 'fa' ? 'rtl' : 'ltr';
    // 2. lang attribute
    document.documentElement.lang = currentLang;
    // 3. font
    if (currentLang === 'fa') {
      document.documentElement.style.fontFamily = "'Vazirmatn', system-ui, -apple-system, sans-serif";
    } else {
      document.documentElement.style.fontFamily = "'Inter', system-ui, -apple-system, sans-serif";
    }
    // 4. window global
    window.__elen_lang = currentLang;
    // 5. custom event
    try {
      window.dispatchEvent(new CustomEvent('elen_lang', { detail: { lang: currentLang } }));
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    applyLanguageEffects(lang);
  }, [lang]);

  const setLang = (newLang: Language) => {
    try {
      localStorage.setItem(STORAGE_KEY, newLang);
    } catch {
      // ignore
    }
    applyLanguageEffects(newLang);
    startTransition(() => {
      setLangState(newLang);
    });
  };

  const toggleLang = () => {
    const nextLang = lang === 'fa' ? 'en' : 'fa';
    setLang(nextLang);
  };

  return (
    <LanguageContext.Provider
      value={{
        lang,
        setLang,
        toggleLang,
        t: translations[lang] as unknown as TranslationSchema
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
