import type { AnimalGroup, GameSettings } from '../types';

interface SettingsPanelProps {
  settings: GameSettings;
  onChange: (settings: GameSettings) => void;
  onStart: () => void;
  onRestart: () => void;
  isRunning: boolean;
  isComplete: boolean;
  hasActiveGame: boolean;
  availableGroups: Array<{ group: AnimalGroup; count: number }>;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

const GRID_OPTIONS: GameSettings['gridSize'][] = [12, 18, 24];

export function SettingsPanel({
  settings,
  onChange,
  onStart,
  onRestart,
  isRunning,
  isComplete,
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

  const canStart = availableGroups.some(
    (option) => option.group === settings.group && option.count >= settings.gridSize / 2
  );

  return (
    <section className="settings">
      <div className="settings__group">
        <h2>{translate('controls.groupLabel')}</h2>
        <div className="settings__options">
          {availableGroups.map((option) => {
            const disabled = option.count < settings.gridSize / 2;
            const selected = settings.group === option.group;
            return (
              <button
                key={option.group}
                type="button"
                className={'pill' + (selected ? ' selected' : '')}
                onClick={() => handleGroupChange(option.group)}
                disabled={!canStart && disabled}
                aria-pressed={selected}
              >
                <span>{translate('groups.' + option.group)}</span>
                <span className="pill__meta">
                  {translate('controls.availableCount', { count: option.count })}
                </span>
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
      <div className="settings__actions">
        <button type="button" onClick={onStart} disabled={!canStart} className="primary">
          {translate(hasActiveGame ? 'controls.changeSetup' : 'controls.start')}
        </button>
        <button type="button" onClick={onRestart} disabled={!hasActiveGame}>
          {translate('controls.restart')}
        </button>
        <div className="settings__hint">
          {isRunning
            ? translate('status.inProgress')
            : isComplete
            ? translate('status.completed')
            : translate('status.idle')}
        </div>
      </div>
    </section>
  );
}
