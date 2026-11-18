# Publishing Fat Cat Todo on Google Play

Everything code-side is ready (v1.4.0): Google Play Billing for Pro, optional Firebase Analytics, English default, signed release builds in GitHub Actions. The steps below need **your** Google / GitHub accounts.

## A. GitHub secrets (once) – lets Actions build the signed release `.aab`
Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `KEYSTORE_BASE64` | contents of `KEYSTORE_BASE64.txt` (one long line) |
| `KEYSTORE_PASSWORD` | from `passwords.txt` |
| `KEY_ALIAS` | `fatcat-upload` |
| `KEY_PASSWORD` | from `passwords.txt` |
| `GOOGLE_SERVICES_JSON` | full text of `google-services.json` (step B) |

⚠️ Back up `fatcat-upload.jks` + passwords somewhere safe (password manager / Drive). It is your **upload key**. With Play App Signing, Google keeps the real signing key; a lost upload key can be reset through Play support, but it takes days.

After adding secrets, push any commit to `main` → the GitHub Release contains **FatCatTodo-release.aab** (upload this to Play) and FatCatTodo-debug.apk (for testing).

## B. Firebase Analytics (free)
1. https://console.firebase.google.com → **Add project** “Fat Cat Todo” (Google Analytics: on).
2. **Add app → Android**, package name **`com.fatcat.todo`**, nickname “Fat Cat Todo”.
3. Download **google-services.json** → paste its text into the `GOOGLE_SERVICES_JSON` secret (or send it to Claude to commit).
4. Dashboards: Firebase → Analytics → Dashboard / Events / Retention. Events the app sends:
   `task_add`, `task_complete`, `day_complete`, `task_move`, `task_delete`, `task_edit`, `repeat_set`, `reminder_set`, `theme_preview`, `theme_change`, `paywall_view`, `purchase_start`, `purchase_success`, `purchase_cancel`, `purchase_pending`, `purchase_error`, `restore_purchases`, `onboarding_complete`, `setting_change`, `analytics_opt_in/out`, `app_open_fatcat` + automatic `screen_view`, `first_open`, `session_start`.
   User properties: `app_language`, `app_theme`, `is_pro`, `dark_mode`.
5. Tip: in Firebase → Analytics → Custom definitions, register `list`, `plan`, `theme` as custom dimensions to break reports down by them.

## C. Google Play Console
1. Developer account (US$25 one-time): https://play.google.com/console/signup — personal accounts created after Nov 2023 must run a **closed test with ≥12 testers for 14 days** before production.
2. **Create app**: name “Fat Cat Todo”, default language **English (United States)**, App, Free (with in-app purchases).
3. **Setup → App integrity**: use Play App Signing (default).
4. **Testing → Internal testing → Create release** → upload `FatCatTodo-release.aab` → add yourself as tester → install from the opt-in link. (Billing products can only be created after the first AAB with the BILLING permission is uploaded.)
5. **Monetize → Products**: create the three products in `store/listing.md` with exactly those IDs and prices, then **Activate**. Add your Gmail under **Settings → License testing** to buy without being charged.
6. **Store presence → Main store listing**: text + images from `store/` (icon, feature graphic, 6 screenshots). Add **Vietnamese** (and other) translations if you want.
7. **Policy → App content**: Privacy policy URL (below), Ads: **No**, App access: all features available without login, Content rating questionnaire (Utility/Productivity → likely “Everyone”), Target audience: 13+, **Data safety**: answers in `store/listing.md`.
8. Closed testing (12 testers × 14 days) → **Production → Create release** → roll out.

Privacy policy: https://github.com/trantrung84/fatcat-todo/blob/main/PRIVACY.md
Terms: https://github.com/trantrung84/fatcat-todo/blob/main/TERMS.md
→ Edit `PRIVACY.md` section 8 and put your real support email before submitting.

## D. Testing purchases
- Debug APK (from GitHub Release) can't buy — billing only works for apps installed **from Play** (internal/closed test track) and signed with the upload key.
- In debug builds the hidden test unlock still works: tap **Version** 7× in Settings → About. It is disabled in release builds.

## E. Each new version
Bump `versionCode` (+1) and `versionName` in `android/app/build.gradle`, push to `main`, upload the new `.aab` from the GitHub Release.
