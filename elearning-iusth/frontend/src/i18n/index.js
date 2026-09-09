import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'
import en from './locales/en.json'

const STORAGE_KEY = 'lms-locale'
const storedLocale = localStorage.getItem(STORAGE_KEY)

const i18n = createI18n({
  legacy: false,
  locale: storedLocale === 'en' ? 'en' : 'fr',
  fallbackLocale: 'fr',
  messages: { fr, en },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
}

export default i18n
