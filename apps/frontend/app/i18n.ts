import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "../public/locales/en/translations.json";
import de from "../public/locales/de/translations.json";

i18n.use(initReactI18next).init({
  fallbackLng: "en",
  debug: import.meta.env.DEV,
  resources: {
    en: { translation: en },
    de: { translation: de },
  },
  react: {
    useSuspense: true,
  },

  interpolation: {
    escapeValue: false,
  },
  initImmediate: false,
});

export default i18n;
