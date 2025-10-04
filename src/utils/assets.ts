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
  if (path.startsWith(BASE_URL)) {
    return path;
  }
  const baseWithoutSlashes = BASE_URL.replace(/^\/+|\/+$/g, '');
  if (baseWithoutSlashes) {
    if (path.startsWith(`/${baseWithoutSlashes}`)) {
      return path;
    }
    if (path.startsWith(baseWithoutSlashes)) {
      return `/${path}`;
    }
  }
  const trimmed = path.replace(/^\/+/, '');
  return `${BASE_URL}${trimmed}`;
}

export const PLACEHOLDER_IMAGE = resolveAssetPath('assets/placeholder.svg');
