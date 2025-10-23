#!/usr/bin/env node

/**
 * Non-interactive Bubblewrap bootstrapper.
 *
 * This script bridges the gap between the interactive `bubblewrap init`
 * command and an automated workflow. It reads the local PWA manifest and
 * assets, patches Bubblewrap's fetch calls so everything is resolved from
 * disk, and emits an Android TWA project under `android-twa/`.
 */

const path = require('path');
const fs = require('fs');
const fsp = fs.promises;

const Module = require('module');
const globalNodeModules = process.env.APPDATA
  ? path.join(process.env.APPDATA, 'npm', 'node_modules')
  : null;
if (globalNodeModules && !Module.globalPaths.includes(globalNodeModules)) {
  Module.globalPaths.push(globalNodeModules);
}
if (globalNodeModules && !module.paths.includes(globalNodeModules)) {
  module.paths.push(globalNodeModules);
}
if (globalNodeModules) {
  process.env.NODE_PATH = process.env.NODE_PATH
    ? `${process.env.NODE_PATH}${path.delimiter}${globalNodeModules}`
    : globalNodeModules;
  Module._initPaths();
}

const projectRoot = path.resolve(__dirname, '..');
const publicDir = path.join(projectRoot, 'public');
const outputDir = path.join(projectRoot, 'android-twa');

const {
  TwaManifest,
  TwaGenerator,
  BufferedLog,
  ConsoleLog,
} = require('@bubblewrap/core');

const shared = require('@bubblewrap/cli/dist/lib/cmds/shared');
const { fetchUtils } = require('@bubblewrap/core/dist/lib/FetchUtils');

class FakeResponse {
  constructor(buffer, { status = 200, headers = {} } = {}) {
    this._buffer = buffer;
    this.status = status;
    this._headers = new Map(
      Object.entries(headers).map(([key, value]) => [key.toLowerCase(), value]),
    );
  }

  async text() {
    return this._buffer.toString('utf-8');
  }

  async arrayBuffer() {
    const { buffer, byteOffset, byteLength } = this._buffer;
    return buffer.slice(byteOffset, byteOffset + byteLength);
  }

  get headers() {
    return {
      get: (name) => this._headers.get(String(name).toLowerCase()) ?? null,
    };
  }
}

async function main() {
  const host = 'plasticxpower.github.io';
  const basePath = '/PexEdu_01/';

  const manifestUrl = `https://${host}${basePath}manifest.webmanifest`;
  const iconUrl = `https://${host}${basePath}icons/icon-512x512.png`;
  const maskableIconUrl = `https://${host}${basePath}icons/icon-512x512-maskable.png`;

  const manifestPath = path.join(publicDir, 'manifest.webmanifest');
  const manifestJson = JSON.parse(await fsp.readFile(manifestPath, 'utf8'));

  await fsp.mkdir(outputDir, { recursive: true });

  const loadAsset = async (assetPath) => {
    const absolute = path.join(publicDir, assetPath);
    return fsp.readFile(absolute);
  };

  const originalFetch = fetchUtils.fetch.bind(fetchUtils);
  fetchUtils.fetch = async (input) => {
    const url = typeof input === 'string' ? input : input.toString();
    if (url === manifestUrl) {
      const manifestBuffer = Buffer.from(JSON.stringify(manifestJson));
      return new FakeResponse(manifestBuffer, {
        headers: { 'content-type': 'application/manifest+json' },
      });
    }
    if (url === iconUrl) {
      const buffer = await loadAsset('icons/icon-512x512.png');
      return new FakeResponse(buffer, { headers: { 'content-type': 'image/png' } });
    }
    if (url === maskableIconUrl) {
      const buffer = await loadAsset('icons/icon-512x512-maskable.png');
      return new FakeResponse(buffer, { headers: { 'content-type': 'image/png' } });
    }
    return originalFetch(url);
  };

  const twaManifest = TwaManifest.fromWebManifestJson(
    new URL(manifestUrl),
    manifestJson,
  );

  twaManifest.packageId = 'com.plasticxpower.pexedu';
  twaManifest.host = host;
  twaManifest.startUrl = `${basePath}?source=pwa`;
  twaManifest.name = 'PexEdu';
  twaManifest.launcherName = 'PexEdu';
  twaManifest.appVersionCode = 1;
  twaManifest.appVersionName = '1';
  twaManifest.iconUrl = iconUrl;
  twaManifest.maskableIconUrl = maskableIconUrl;
  twaManifest.monochromeIconUrl = undefined;
  twaManifest.orientation = 'portrait';
  twaManifest.enableNotifications = false;
  twaManifest.features = twaManifest.features || {};
  twaManifest.signingKey.path = path.join(outputDir, 'android.keystore');
  twaManifest.signingKey.alias = 'pexedu';
  twaManifest.generatorApp = 'bubblewrap-cli';
  twaManifest.webManifestUrl = new URL(manifestUrl);
  twaManifest.fullScopeUrl = new URL(basePath, `https://${host}`);
  twaManifest.shortcuts = [];
  twaManifest.enableSiteSettingsShortcut = true;

  await twaManifest.saveToFile(path.join(outputDir, 'twa-manifest.json'));

  const twaGenerator = new TwaGenerator();
  const log = new BufferedLog(new ConsoleLog('bubblewrap'));
  await twaGenerator.createTwaProject(outputDir, twaManifest, log, () => {});
  log.flush();

  await shared.generateManifestChecksumFile(
    path.join(outputDir, 'twa-manifest.json'),
    outputDir,
  );
}

main().catch((err) => {
  console.error('[bubblewrap] Failed to generate TWA project.');
  console.error(err);
  process.exitCode = 1;
});
