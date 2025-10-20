# Hướng dẫn Setup Firebase cho Tower Builder Game

## Bước 1: Cài đặt thư viện

```bash
pip install pyrebase4
```

## Bước 2: Tạo Firebase Project

1. Vào https://console.firebase.google.com/
2. Nhấn "Add project" hoặc "Tạo dự án"
3. Đặt tên project (ví dụ: "tower-builder-game")
4. Bỏ chọn Google Analytics (không cần thiết)
5. Nhấn "Create project"

## Bước 3: Bật Authentication

1. Trong Firebase Console, chọn "Authentication" ở menu bên trái
2. Nhấn "Get started"
3. Chọn tab "Sign-in method"
4. Bật "Email/Password"
   - Click vào "Email/Password"
   - Bật toggle đầu tiên (Email/Password)
   - Nhấn "Save"

## Bước 4: Bật Realtime Database

1. Chọn "Realtime Database" ở menu bên trái
2. Nhấn "Create Database"
3. Chọn location (ví dụ: United States)
4. Chọn "Start in **test mode**" (để dễ test)
5. Nhấn "Enable"

### Cấu hình Security Rules (Quan trọng!)

Sau khi tạo database, vào tab "Rules" và thay bằng rules này:

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "auth != null",
        ".write": "auth != null && auth.uid == $uid"
      }
    },
    "scores": {
      "$uid": {
        ".read": true,
        ".write": "auth != null && auth.uid == $uid"
      }
    }
  }
}
```

Nhấn "Publish" để lưu.

## Bước 5: Lấy Firebase Config

1. Trong Firebase Console, nhấn vào icon bánh răng ⚙️ cạnh "Project Overview"
2. Chọn "Project settings"
3. Kéo xuống phần "Your apps"
4. Nhấn vào icon web `</>`
5. Đặt tên app (ví dụ: "Tower Builder")
6. **KHÔNG** cần chọn "Firebase Hosting"
7. Nhấn "Register app"
8. Copy đoạn config trong phần `firebaseConfig`

Ví dụ config sẽ trông như này:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "tower-builder-xxxxx.firebaseapp.com",
  databaseURL: "https://tower-builder-xxxxx.firebaseio.com",
  projectId: "tower-builder-xxxxx",
  storageBucket: "tower-builder-xxxxx.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:xxxxxxxxxxxxx"
};
```

## Bước 6: Cập nhật file `firebase_config.py`

Mở file `towerbuilder/firebase_config.py` và thay đổi đoạn config:

```python
firebaseConfig = {
    "apiKey": "YOUR_API_KEY_HERE",           # Thay bằng apiKey của bạn
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT.firebaseio.com",  # QUAN TRỌNG!
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID"
}
```

**LƯU Ý:** `databaseURL` rất quan trọng! Nếu thiếu sẽ bị lỗi.

## Bước 7: Chạy game

```bash
python towerbuilder/test.py
```

## Troubleshooting (Xử lý lỗi)

### Lỗi: "Module 'pyrebase4' not found"
```bash
pip install pyrebase4
```

### Lỗi: "Failed to find service account credentials"
- Kiểm tra lại config trong `firebase_config.py`
- Đảm bảo đã copy đúng tất cả các trường

### Lỗi: "Permission denied"
- Vào Firebase Console > Realtime Database > Rules
- Đổi rules như hướng dẫn ở Bước 4

### Lỗi: "Email already exists"
- Email đã được đăng ký
- Dùng email khác hoặc đăng nhập với email đó

### Game vẫn chạy nhưng không có Firebase
- Nếu Firebase chưa setup, game vẫn hoạt động bình thường
- Chỉ có leaderboard local
- Không có chức năng login

## Tính năng đã thêm

✅ **Đăng ký/Đăng nhập:** Email + Password
✅ **Leaderboard Online:** Xem top 10 toàn cầu
✅ **Leaderboard Local:** Xem điểm trên máy
✅ **Tự động lưu điểm:** Sau mỗi game
✅ **Hiển thị username:** Trên leaderboard và menu

## Demo Usage

1. Chạy game
2. Chọn "Dang nhap" → Đăng ký tài khoản mới
3. Chơi game
4. Điểm tự động lưu lên Firebase
5. Xem "Bang xep hang" → Chuyển tab "Online" để xem top toàn cầu

---

**Lưu ý bảo mật:**
- Không share file `firebase_config.py` lên GitHub public
- Thêm vào `.gitignore`:
  ```
  towerbuilder/firebase_config.py
  ```
