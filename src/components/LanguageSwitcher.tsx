import { useId, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { resolveAssetPath } from '../utils/assets';

const LANGS = [
  { code: 'en', label: 'English', icon: resolveAssetPath('assets/flags/en.svg') },
  { code: 'cs', label: 'Česky', icon: resolveAssetPath('assets/flags/cs.svg') },
];
const CHEVRON_SYMBOL = '\u25BE';

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith('cs') ? 'cs' : 'en';
  const [open, setOpen] = useState(false);
  const menuId = useId();

  const toggleOpen = () => {
    setOpen((value) => !value);
  };

  const handleSelect = (code: string) => {
    i18n.changeLanguage(code);
    setOpen(false);
  };

  const currentLang = LANGS.find((item) => item.code === current) ?? LANGS[0];
  const languageLabel = t('controls.language');
  const toggleLabel = `${languageLabel}: ${currentLang.label}`;

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
        aria-expanded={open}
        aria-controls={menuId}
        aria-label={toggleLabel}
      >
        <img
          src={currentLang.icon}
          alt=""
          className="language-switcher__icon"
          aria-hidden="true"
          width={24}
          height={16}
          decoding="async"
        />
        <span>{currentLang.label}</span>
        <span className="language-switcher__chevron" aria-hidden="true">{CHEVRON_SYMBOL}</span>
      </button>
      <ul id={menuId} className="language-switcher__menu" aria-label={languageLabel}>
        {LANGS.map((lang) => (
          <li key={lang.code}>
            <button
              type="button"
              className={current === lang.code ? 'is-active' : ''}
              aria-pressed={current === lang.code}
              onClick={() => handleSelect(lang.code)}
            >
              <img
                src={lang.icon}
                alt=""
                className="language-switcher__icon"
                aria-hidden="true"
                width={24}
                height={16}
                decoding="async"
              />
              <span>{lang.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
