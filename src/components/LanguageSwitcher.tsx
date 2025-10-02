import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const LANGS = [
  { code: 'en', label: 'English', icon: '/assets/flags/en.svg' },
  { code: 'cs', label: 'Česky', icon: '/assets/flags/cs.svg' },
];

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith('cs') ? 'cs' : 'en';
  const [open, setOpen] = useState(false);

  const toggleOpen = () => {
    setOpen((value) => !value);
  };

  const handleSelect = (code: string) => {
    i18n.changeLanguage(code);
    setOpen(false);
  };

  const currentLang = LANGS.find((item) => item.code === current) ?? LANGS[0];

  return (
    <div
      className={'language-switcher' + (open ? ' is-open' : '')}
      tabIndex={-1}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node)) {
          setOpen(false);
        }
      }}
    >
      <button
        type="button"
        className="language-switcher__toggle"
        onClick={toggleOpen}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <img
          src={currentLang.icon}
          alt=""
          className="language-switcher__icon"
          aria-hidden="true"
        />
        <span>{currentLang.label}</span>
        <span className="language-switcher__chevron" aria-hidden="true">
          ▾
        </span>
      </button>
      <ul className="language-switcher__menu" role="listbox">
        {LANGS.map((lang) => (
          <li key={lang.code}>
            <button
              type="button"
              className={current === lang.code ? 'is-active' : ''}
              role="option"
              aria-selected={current === lang.code}
              onClick={() => handleSelect(lang.code)}
            >
              <img
                src={lang.icon}
                alt=""
                className="language-switcher__icon"
                aria-hidden="true"
              />
              <span>{lang.label}</span>
            </button>
          </li>
        ))}
      </ul>
      <span className="visually-hidden">{t('controls.language')}</span>
    </div>
  );
}
