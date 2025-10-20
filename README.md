# Tower Builder Game - Online Leaderboard Edition 🏗️

Game xếp tháp với hệ thống đăng nhập và bảng xếp hạng online!

## ✨ Tính năng

### Game Core
- ⚡ 10 cấp độ khó tăng dần
- 🌪️ Hiệu ứng gió từ level 4
- 🎯 Hệ thống combo khi đặt chính xác
- 📊 Điểm số và level tracking
- 🎮 Controls đơn giản (Space để thả, P để pause)

### Online Features (NEW!)
- 👤 **Đăng ký/Đăng nhập** với email
- 🌍 **Leaderboard Online** - Xem top 10 toàn cầu
- 💾 **Tự động lưu điểm** lên cloud
- 🏆 **So sánh với người chơi khác**
- 📱 **Leaderboard Local** - Vẫn lưu điểm offline

## 🚀 Cài đặt

### Yêu cầu
- Python 3.7+
- Pygame
- Pyrebase4 (cho Firebase)

### Cài đặt dependencies

```bash
pip install pygame
pip install pyrebase4
```

### Chạy game (không cần Firebase)

```bash
python towerbuilder/test.py
```

Game vẫn chạy bình thường nếu chưa setup Firebase. Bạn vẫn có thể:
- Chơi game đầy đủ
- Xem leaderboard local
- Lưu điểm trên máy

## 🔥 Setup Firebase (Optional - cho Online Leaderboard)

Xem hướng dẫn chi tiết trong file [SETUP_FIREBASE.md](SETUP_FIREBASE.md)

### Quick Setup:
1. Tạo project Firebase (miễn phí)
2. Bật Authentication (Email/Password)
3. Bật Realtime Database
4. Copy config vào `firebase_config.py`
5. Chạy game và đăng nhập!

## 🎮 Cách chơi

### Menu chính
- **Choi**: Bắt đầu game
- **Bang xep hang**: Xem điểm cao
  - Tab Local: Điểm trên máy
  - Tab Online: Top 10 toàn cầu (cần đăng nhập)
- **Dang nhap/Dang xuat**: Quản lý tài khoản
- **Thoat**: Thoát game

### Trong game
- **SPACE**: Thả khối
- **P/ESC**: Tạm dừng
- **Mục tiêu**: Xếp khối chồng lên nhau càng cao càng tốt

### Hệ thống điểm
- **Perfect (offset ≤ 15px)**: 100 điểm + tăng width khối
- **Good (offset ≤ 25px)**: 50 điểm
- **OK (offset > 25px)**: 25 điểm
- **Combo**: Nhân điểm khi đặt Perfect liên tiếp

### Độ khó
- Level 1-3: Cơ bản, không có gió
- Level 4+: Xuất hiện gió (càng cao càng mạnh)
- Level 5+: Khối bị cắt nếu đặt không chuẩn
- Level 10: Khó nhất!

## 📁 Cấu trúc Project

```
game-tower-builder/
├── towerbuilder/
│   ├── test.py                      # File chính của game
│   ├── firebase_config.py           # Config Firebase (không commit)
│   ├── firebase_config.template.py  # Template config
│   ├── login_screen.py              # UI đăng nhập/đăng ký
│   ├── leaderboard.txt              # Leaderboard local
│   └── assets/
│       ├── background.png
│       └── block.png
├── SETUP_FIREBASE.md                # Hướng dẫn setup Firebase
├── README.md                        # File này
└── .gitignore
```

## 🔒 Bảo mật

- ❌ **KHÔNG** commit file `firebase_config.py` lên GitHub
- ✅ File đã được thêm vào `.gitignore`
- ✅ Dùng Firebase Security Rules để bảo vệ data
- ✅ Mỗi user chỉ có thể chỉnh sửa điểm của mình

## 🐛 Troubleshooting

### Game không chạy
```bash
# Cài lại pygame
pip install --upgrade pygame
```

### Lỗi Firebase
- Kiểm tra `firebase_config.py` đã điền đúng thông tin
- Xem chi tiết trong [SETUP_FIREBASE.md](SETUP_FIREBASE.md)

### Muốn chơi offline
- Game tự động chạy offline nếu Firebase chưa setup
- Chỉ mất tính năng online leaderboard

## 📝 License

Free to use for educational purposes.

## 👨‍💻 Development

### Thêm tính năng mới
1. Fork repository
2. Tạo branch mới
3. Code và test
4. Submit pull request

### Structure
- `test.py`: Game logic chính
- `firebase_config.py`: Firebase integration
- `login_screen.py`: Login/Register UI

## 🎓 Dành cho Teacher

Nếu bạn là giáo viên muốn dùng project này:

1. **Setup Firebase cho class:**
   - Tạo 1 Firebase project chung
   - Share config với học sinh
   - Học sinh có thể thi đấu với nhau

2. **Hoặc mỗi học sinh tự setup:**
   - Mỗi người tạo Firebase project riêng
   - Học cách deploy cloud service

3. **Không muốn Firebase:**
   - Bỏ qua phần Firebase
   - Game vẫn hoạt động bình thường với local leaderboard

## 📮 Contact

Nếu có vấn đề, tạo Issue trên GitHub!

---

**Have fun building towers! 🏗️🎮**
