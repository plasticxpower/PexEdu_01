const EXTERNAL_PATH_REGEX = /^[a-z][a-z\d+\-.]*:/i;

const BASE_URL = (() => {
  const raw = import.meta.env.BASE_URL ?? '/';
  return raw.endsWith('/') ? raw : raw + '/';
})();

export function resolveAssetPath(path: string | null | undefined): string {
  if (!path) {
    return '';
  }
  if (EXTERNAL_PATH_REGEX.test(path)) {
    return path;
  }
  const trimmed = path.replace(/^\/+/, '');
  return `${BASE_URL}${trimmed}`;
}

export const PLACEHOLDER_IMAGE = resolveAssetPath('assets/placeholder.svg');
export const WILD_BACKGROUND_IMAGE = resolveAssetPath(
  'assets/graphics/358029164_c765b876-ce8e-4f04-a88e-ba041d04ba39.svg'
);
