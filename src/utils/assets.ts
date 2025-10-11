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

type ResponsiveFormat = 'avif' | 'webp';

interface ResponsiveAssetSource {
  type: string;
  srcSet: string;
}

export interface ResponsiveAsset {
  fallback: string;
  sources: ResponsiveAssetSource[];
}

interface ResponsiveAssetOptions {
  widths?: number[];
  formats?: ResponsiveFormat[];
}

const DEFAULT_WIDTHS = [400, 800, 1200];
const DEFAULT_FORMATS: ResponsiveFormat[] = ['avif', 'webp'];

export function buildResponsiveAsset(
  assetPath: string | null | undefined,
  options?: ResponsiveAssetOptions
): ResponsiveAsset | null {
  if (!assetPath) {
    return null;
  }

  const extensionMatch = assetPath.match(/\.([a-z0-9]+)$/i);
  if (!extensionMatch) {
    return null;
  }

  const extension = extensionMatch[1].toLowerCase();
  if (!['jpg', 'jpeg', 'png', 'webp'].includes(extension)) {
    return null;
  }

  const basePath = assetPath.slice(0, -(extension.length + 1));
  const widths = (options?.widths ?? DEFAULT_WIDTHS).filter((value) => value > 0);
  const formats = options?.formats ?? DEFAULT_FORMATS;

  const sources: ResponsiveAssetSource[] = formats
    .map((format) => {
      const srcSet = widths
        .map((width) => `${resolveAssetPath(`${basePath}-${width}w.${format}`)} ${width}w`)
        .join(', ');
      if (!srcSet) {
        return null;
      }
      return {
        type: `image/${format}`,
        srcSet,
      };
    })
    .filter((source): source is ResponsiveAssetSource => Boolean(source));

  return {
    fallback: resolveAssetPath(assetPath),
    sources,
  };
}
