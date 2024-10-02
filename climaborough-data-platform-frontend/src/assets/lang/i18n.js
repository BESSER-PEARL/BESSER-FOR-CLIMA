import { createI18n } from 'vue-i18n';

// Import translations
import en from './locales/en.json';
import fr from './locales/fr.json';
import it from './locales/it.json';
// Add more languages as needed

const messages = {
    en,
    fr,
    it
    // Add more languages as needed
};

const i18n = createI18n({
    legacy: false,
    locale: 'en', // Set default locale
    fallbackLocale: 'en', // Set fallback locale
    messages,
});

export default i18n;
