# Fat Cat Todo – Android (Capacitor)

**v1.1.0** — giao diện mới theo bộ mockup Mochi Cat (viền nâu, mèo tam thể), thanh điều hướng dưới (Hôm nay · Lịch · Timeline · Someday · Khác), nút + nổi, và **10 theme màu** (Mochi đào + 9 bảng màu) chọn trong *Khác ▸ Theme màu* hoặc nút bảng màu trên đầu trang.

## Cấu trúc
- `src/index.src.html` – mã nguồn giao diện + logic (một file).
- `src/sprites/*.png` – 10 tư thế mèo cắt từ sprite atlas; `src/fonts/` – Baloo 2 + Nunito (SIL OFL).
- `build.py` – gộp font + ảnh mèo vào `www/index.html` (chạy `python3 build.py`, cần Pillow) sau mỗi lần sửa `src/`.
- `www/index.html` – bản đã build, mở trực tiếp bằng Chrome để xem trước.

Ứng dụng to-do + thói quen với chú mèo béo Mochi, dựng theo *Fat Cat Todo Product Spec V1* (phạm vi MVP).

## 1. Xem trước bằng HTML (không cần cài gì)
Mở `www/index.html` bằng Chrome → F12 → bật **Device toolbar** (Ctrl+Shift+M) → chọn một máy Android (vd. Pixel 7).
Dữ liệu lưu trong localStorage của trình duyệt. Nhắc nhở trên bản web chỉ chạy khi tab đang mở (bản APK dùng thông báo hệ thống thật).

## 2. Build APK trên máy của bạn
Yêu cầu: Node.js 20+, Android Studio (kèm Android SDK 36), JDK 21 (đi kèm Android Studio).

```bash
npm install
npx cap sync android
npx cap open android      # mở bằng Android Studio → Build ▸ Build APK(s)
# hoặc dòng lệnh:
cd android && ./gradlew assembleDebug    # Windows: gradlew.bat assembleDebug
```
APK nằm ở `android/app/build/outputs/apk/debug/app-debug.apk` → chép sang điện thoại và cài (bật "Cài ứng dụng không rõ nguồn gốc").

Mỗi khi sửa `www/index.html`, chạy lại `npx cap sync android` rồi build.

## 3. Build APK tự động bằng GitHub (không cần Android Studio)
1. Tạo repo GitHub mới, đẩy toàn bộ thư mục này lên nhánh `main`.
2. Vào tab **Actions** → workflow *Build Android APK* sẽ tự chạy (~5–8 phút).
3. Mở lần chạy đó → mục **Artifacts** → tải `fatcat-todo-apk` (file zip chứa APK).

## 4. Bản phát hành (Google Play / phân phối chính thức)
Tạo keystore một lần và **giữ kỹ** (mất là không cập nhật app được):
```bash
keytool -genkey -v -keystore release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias fatcat
```
- Android Studio: *Build ▸ Generate Signed App Bundle / APK*. Google Play yêu cầu **.aab** (`./gradlew bundleRelease`).
- GitHub Actions: thêm 4 secrets `KEYSTORE_BASE64` (`base64 -w0 release.jks`), `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD` → workflow tự build thêm APK release đã ký.
- Tăng `versionCode` trong `android/app/build.gradle` cho mỗi lần phát hành.

## Thông tin kỹ thuật
- appId: `com.fatcat.todo` (đổi trong `capacitor.config.json` + `android/app/build.gradle` trước khi phát hành lần đầu nếu cần).
- Capacitor 8, minSdk 24 (Android 7+), target/compile SDK 36.
- Plugin: local-notifications (nhắc việc + báo cáo buổi sáng, lên lịch 14 ngày tới, tự làm mới khi mở app), haptics, app (nút Back), status-bar, splash-screen, filesystem + share (xuất JSON).
- Dữ liệu chỉ lưu trên máy (offline-first), không quảng cáo, không analytics.
