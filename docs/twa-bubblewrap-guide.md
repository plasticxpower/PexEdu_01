# Packaging PexEdu with Bubblewrap (Trusted Web Activity)

This guide explains how to ship the PexEdu PWA (`https://plasticxpower.github.io/PexEdu_01/`) to the Google Play Store as an Android App Bundle (AAB) using a Trusted Web Activity (TWA).

## 1. Prerequisites

- Production PWA deployed at `https://plasticxpower.github.io/PexEdu_01/` (or a custom domain pointing to the same build).
- Node.js 18+ and npm.
- Local `@bubblewrap/cli` dependency (already listed in `devDependencies`).
- JDK 17 and Android SDK 34+ (install via Android Studio).
- Google Play Console access for the PexEdu listing.
- A Play-signing compatible upload keystore (new or existing).

## 2. Verify the PWA

```bash
npm install
npm run build
```

Deploy `dist/` to production and run Lighthouse (Chrome DevTools → Lighthouse → Progressive Web App) against the live URL. Only continue once the installability checks pass (HTTPS, manifest, service worker, offline).

## 3. Generate / Refresh the TWA wrapper

```bash
npm run bubblewrap:init
```

The script performs a non-interactive `bubblewrap init`:

- Reads `public/manifest.webmanifest` and icon assets from disk.
- Regenerates `android-twa/` with:
  - Application Id: `com.plasticxpower.pexedu`
  - Host: `plasticxpower.github.io`
  - Start URL: `/PexEdu_01/?source=pwa`
  - Launcher + maskable icons from `public/icons/`
- Writes `android-twa/twa-manifest.json` and `android-twa/manifest-checksum.txt`.

Re-run the script whenever manifest values, colours, or icons change.

## 4. Provision the signing key

The manifest expects a keystore at `android-twa/android.keystore` with alias `pexedu`. Create it (or reuse an existing upload key):

```bash
keytool -genkeypair ^
  -alias pexedu ^
  -keyalg RSA ^
  -keysize 2048 ^
  -validity 9125 ^
  -keystore android-twa/android.keystore ^
  -storepass "<strong-password>" ^
  -keypass "<strong-password>" ^
  -dname "CN=PexEdu, OU=Apps, O=PlasticXPower, C=CZ"
```

> Keep the password safe. You will need it for both local builds and the Play Console.

If Play App Signing manages the final release key, upload this keystore as the *upload key* during Play onboarding.

## 5. Publish the Digital Asset Links file

After the keystore exists, derive the SHA‑256 fingerprint:

```bash
npx bubblewrap fingerprint ^
  --manifest=android-twa/twa-manifest.json ^
  --signingKeyPath=android-twa/android.keystore ^
  --signingKeyAlias=pexedu ^
  --signingKeyPassword="<strong-password>"
```

Bubblewrap prints the JSON for `assetlinks.json`. Deploy it with the site:

```bash
mkdir -p public/.well-known
cat > public/.well-known/assetlinks.json <<'JSON'
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.plasticxpower.pexedu",
      "sha256_cert_fingerprints": [
        "AA:BB:CC:..."
      ]
    }
  }
]
JSON
```

Replace the placeholder fingerprint with the value printed by Bubblewrap. After deployment, verify:

```bash
curl https://plasticxpower.github.io/PexEdu_01/.well-known/assetlinks.json
```

If you migrate to a custom domain, host the same JSON at `https://<your-domain>/.well-known/assetlinks.json`.

## 6. Build the Android App Bundle

1. Open `android-twa/` in Android Studio (Electric Eel or newer).
2. Allow Gradle sync; install any requested SDK platforms or build tools.
3. Configure the release signing config to use `android.keystore` (or Play’s upload key).
4. Build the bundle:

   ```bash
   cd android-twa
   ./gradlew bundleRelease
   ```

   Output: `android-twa/app/build/outputs/bundle/release/app-release.aab`.

5. Optional device smoke test (requires Chrome 115+):

   ```bash
   adb install-multiple app/build/outputs/bundle/release/app-release.aab
   ```

   The app should launch full-screen without Chrome UI; if it falls back to a custom tab, re-check `assetlinks.json` and HTTPS.

## 7. Submit to Google Play

1. Create or select the PexEdu listing in Play Console.
2. Upload store listing assets: screenshots, feature graphics, descriptions, privacy policy URL.
3. Upload `app-release.aab` to the *Internal Testing* track first (recommended).
4. Complete Data Safety, Content Rating, Target Audience, and Pricing sections.
5. After internal QA, promote the build to Production and submit for review.

## 8. Maintenance checklist

- Keep the PWA installable (manifest, service worker, HTTPS).
- Re-run `npm run bubblewrap:init` whenever manifest details/icons change to refresh `android-twa/`.
- Regenerate `assetlinks.json` if the signing certificate rotates.
- The Android shell always loads the live PWA, so content updates do not require Play resubmissions unless permissions change.

Following these steps keeps the Bubblewrap wrapper aligned with the live PWA and prepares release artefacts suitable for Google Play.
