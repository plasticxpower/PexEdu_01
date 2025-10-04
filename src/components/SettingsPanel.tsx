import type { AnimalGroup, GameSettings } from '../types';
import { resolveAssetPath } from '../utils/assets';

interface SettingsPanelProps {
  settings: GameSettings;
  onChange: (settings: GameSettings) => void;
  onStart: () => void;
  hasActiveGame: boolean;
  availableGroups: Array<{ group: AnimalGroup; count: number }>;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

const GRID_OPTIONS: GameSettings['gridSize'][] = [12, 18, 24];
const PLAYER_OPTIONS: GameSettings['playerCount'][] = [1, 2, 3, 4];

export function SettingsPanel({
  settings,
  onChange,
  onStart,
  hasActiveGame,
  availableGroups,
  translate,
}: SettingsPanelProps) {
  const handleGroupChange = (group: AnimalGroup) => {
    if (group === settings.group) {
      return;
    }
    onChange({ ...settings, group });
  };

  const handleGridSizeChange = (gridSize: GameSettings['gridSize']) => {
    if (gridSize === settings.gridSize) {
      return;
    }
    onChange({ ...settings, gridSize });
  };

  const handlePlayerCountChange = (playerCount: GameSettings['playerCount']) => {
    if (playerCount === settings.playerCount) {
      return;
    }
    onChange({ ...settings, playerCount });
  };

  const canStart = availableGroups.some(
    (option) => option.group === settings.group && option.count >= settings.gridSize / 2
  );

  const buttonClass = 'primary start-button' + (hasActiveGame ? ' start-button--active' : '');

  return (
    <section className="settings">
      <div className="settings__group">
        <h2>{translate('controls.groupLabel')}</h2>
        <div className="settings__options">
          {availableGroups.map((option) => {
            const disabled = option.count < settings.gridSize / 2;
            const selected = settings.group === option.group;
            const label = translate('groups.' + option.group);
            const iconSrc = resolveAssetPath(`assets/icons/${option.group}.png`);
            return (
              <button
                key={option.group}
                type="button"
                className={'pill pill--' + option.group + (selected ? ' selected' : '')}
                onClick={() => handleGroupChange(option.group)}
                disabled={!canStart && disabled}
                aria-pressed={selected}
              >
                <span className="pill__icon" aria-hidden="true">
                  <img src={iconSrc} alt="" loading="lazy" />
                </span>
                <span className="pill__label">{label}</span>
              </button>
            );
          })}
        </div>
      </div>
      <div className="settings__group">
        <h2>{translate('controls.gridLabel')}</h2>
        <div className="settings__options">
          {GRID_OPTIONS.map((option) => {
            const selected = settings.gridSize === option;
            return (
              <button
                key={option}
                type="button"
                className={'pill' + (selected ? ' selected' : '')}
                onClick={() => handleGridSizeChange(option)}
                aria-pressed={selected}
              >
                {translate('controls.gridOption', { count: option })}
              </button>
            );
          })}
        </div>
      </div>
      <div className="settings__group">
        <h2>{translate('controls.playersLabel')}</h2>
        <div className="settings__options">
          {PLAYER_OPTIONS.map((option) => {
            const selected = settings.playerCount === option;
            return (
              <button
                key={option}
                type="button"
                className={'pill' + (selected ? ' selected' : '')}
                onClick={() => handlePlayerCountChange(option)}
                aria-pressed={selected}
              >
                {translate('controls.playerCountOption', { count: option })}
              </button>
            );
          })}
        </div>
      </div>
      <div className="settings__actions">
        <button type="button" onClick={onStart} disabled={!canStart} className={buttonClass}>
          {translate(hasActiveGame ? 'controls.changeSetup' : 'controls.start')}
        </button>
      </div>
    </section>
  );
}
