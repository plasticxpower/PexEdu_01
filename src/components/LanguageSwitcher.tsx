import { useTranslation } from 'react-i18next';

const LANGS = [
  { code: 'en', label: 'English' },
  { code: 'cs', label: 'Česky' },
];

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith('cs') ? 'cs' : 'en';

  return (
    <div className="language-switcher" role="group" aria-label={t('controls.language')}>
      {LANGS.map((lang) => (
        <button
          key={lang.code}
          type="button"
          className={current === lang.code ? 'active' : ''}
          onClick={() => i18n.changeLanguage(lang.code)}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
