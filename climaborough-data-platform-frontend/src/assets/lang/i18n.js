import { createI18n } from 'vue-i18n';

// Import translations
import en from './locales/en.json';
import fr from './locales/fr.json';
import it from './locales/it.json';
import lb from './locales/lb.json'; // Lëtzebuergesch (Luxembourgish)
import sl from './locales/sl.json'; // Slovenščina (Slovenian)
import el from './locales/el.json'; // Ελληνικά (Greek)
import pl from './locales/pl.json'; // Polski (Polish)
import sr from './locales/sr.json'; // Crnogorski (Montenegrin)
import cs from './locales/cs.json'; // Čeština (Czech)
import bs from './locales/bs.json'; // Bosanski (Bosnian)
import bg from './locales/bg.json'; // Български (Bulgarian)

const messages = {
    en,
    fr,
    it,
    lb, // Lëtzebuergesch (Luxembourgish)
    sl, // Slovenščina (Slovenian)
    el, // Ελληνικά (Greek)
    pl, // Polski (Polish)
    sr, // Crnogorski (Montenegrin)
    cs, // Čeština (Czech)
    bs, // Bosanski (Bosnian)
    bg  // Български (Bulgarian)
};

const i18n = createI18n({
    legacy: false,
    locale: 'en', // Set default locale
    fallbackLocale: 'en', // Set fallback locale
    messages,
});

export default i18n;
