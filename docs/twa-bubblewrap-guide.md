# Packaging PexEdu with Bubblewrap (Trusted Web Activity)

This guide covers the end-to-end flow for shipping the existing PexEdu PWA to the Google Play Store as an Android App Bundle (AAB) using a Trusted Web Activity (TWA).

## 1. Prerequisites

- PWA served over HTTPS at a production domain (e.g. `https://pexedu.example.com`).
- Node.js 18+ and npm.
- JDK 17 (Android Studio installs it automatically).
- Android Studio (latest stable) with Android SDK 34+.
- Google Play Console access with an existing app listing or the ability to create one.
- A signing keystore for Play releases (you can re-use an existing one or let Play App Signing manage it).

## 2. Verify the PWA

1. Build the production bundle:
   ```bash
   npm install
   npm run build
   ```
2. Deploy the contents of `dist/` to your HTTPS host.
3. Run [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview/) (Chrome DevTools → Lighthouse → Progressive Web App) against the live URL. Confirm:
   - The page is served over HTTPS.
   - The manifest (`https://your-domain/manifest.webmanifest`) passes installability checks (icons, name, start URL, etc.).
   - A service worker controls the page and provides a basic offline experience.

Only proceed once Lighthouse shows the PWA is installable.

## 3. Install Bubblewrap CLI

```bash
npm install -g @bubblewrap/cli
```

If you prefer `npx`, add it before each command instead of a global install.

## 4. Initialise the TWA Project

1. Pick an empty directory for the Android project (e.g. `android-twa/`).
2. Run:
   ```bash
   bubblewrap init --manifest=https://your-domain/manifest.webmanifest
   ```
3. Bubblewrap prompts for app details. Recommended answers:
   - **Application Id**: e.g. `com.yourcompany.pexedu`
   - **Launcher name**: `PexEdu`
   - **Host**: `pexedu.example.com`
   - **Sign With Play Signing**: `y` (unless you want to manage the keystore manually)
4. The command downloads icons and creates `twa-manifest.json` plus an Android project (`app/`).

> **Tip**: If you need to adjust metadata later (name, theme colours, etc.), edit `twa-manifest.json` and run `bubblewrap update`.

## 5. Configure Digital Asset Links

TWA requires a mutual trust relationship between the Android app and your domain.

1. After initialising, run:
   ```bash
   bubblewrap install
   bubblewrap update
   bubblewrap build
   ```
   The CLI prints a `Digital Asset Links` snippet similar to:
   ```json
   [
     {
       "relation": ["delegate_permission/common.handle_all_urls"],
       "target": {
         "namespace": "android_app",
         "package_name": "com.yourcompany.pexedu",
         "sha256_cert_fingerprints": ["AA:BB:CC:..."]
       }
     }
   ]
   ```
2. Host that JSON at `https://pexedu.example.com/.well-known/assetlinks.json`.
3. Deploy and verify the endpoint via:
   ```bash
   curl https://pexedu.example.com/.well-known/assetlinks.json
   ```

## 6. Android Studio & Signing

1. Open the generated Android project (`android-twa/`) in Android Studio.
2. Let Gradle sync. Make any branding tweaks (app name, colours, splash screen) directly in the project if needed.
3. Configure signing:
   - If you opted into Play App Signing, upload the generated signing key to the Play Console when prompted.
   - Otherwise, create or reference an existing keystore (`Build` → `Generate Signed Bundle / APK…`).

## 7. Build the App Bundle

From the project root (or via Android Studio):
```bash
./gradlew bundleRelease
```
The AAB appears at `app/build/outputs/bundle/release/app-release.aab`.

Run a quick smoke test:
```bash
adb install-multiple app/build/outputs/bundle/release/app-release.aab
```
The device should launch your live PWA in full-screen Chrome. If you see a fallback browser UI, double-check the Asset Links file and that the production domain is HTTPS.

## 8. Upload to Google Play

1. Log into the Play Console → create or select your app.
2. Fill in the store listing (graphics, description, categorisation, privacy policy).
3. Upload the AAB in the “Production” (or internal testing) track.
4. Complete content rating, data safety, and pricing sections.
5. Submit for review.

## 9. Ongoing Maintenance

- Update the PWA content as usual; users receive changes instantly because the Android shell always loads the live site.
- When changing the domain or significant manifest properties, regenerate the TWA project via `bubblewrap update`.
- Keep the Asset Links file in sync if you rotate signing keys.

That’s it—PexEdu is now ready for Google Play distribution through a Trusted Web Activity wrapper.
