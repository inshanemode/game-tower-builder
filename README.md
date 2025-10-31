# 🏗️ Tower Builder Game

Game xây tháp với cơ chế vật lý và hệ thống độ khó tăng dần. Người chơi điều khiển các khối gỗ đang đu đưa và thả xuống để xây tháp cao nhất có thể.

![Tower Builder](https://img.shields.io/badge/Python-3.13-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green.svg)
![Firebase](https://img.shields.io/badge/Firebase-Realtime%20DB-orange.svg)

## 📋 Mục lục
- [Tính năng](#-tính-năng)
- [Cách chơi](#-cách-chơi)
- [Hệ thống điểm](#-hệ-thống-điểm)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt](#-cài-đặt)
- [Cấu hình Firebase](#-cấu-hình-firebase)
- [Chạy game](#-chạy-game)
- [Cơ chế game](#-cơ-chế-game)

## ✨ Tính năng

### Gameplay
- **Vật lý thực tế**: Khối gỗ đu đưa theo cơ học con lắc với độ hấp dẫn và lực tác động
- **Hệ thống độ khó**: 10 level được định nghĩa sẵn + vô hạn level với độ khó tăng dần
- **Hiệu ứng gió**: Xuất hiện từ level 4, tăng cường theo độ khó
- **Block shrinking**: Từ level 5+, block bị thu nhỏ 20px nếu đặt sai vị trí
- **Camera mượt mà**: Tự động theo dõi độ cao của tháp với smooth scrolling

### Hệ thống
- **Firebase Integration**: Đăng ký/đăng nhập tài khoản, bảng xếp hạng online
- **Local Leaderboard**: Lưu điểm offline nếu không có Firebase
- **Pause/Resume**: Tạm dừng game bất cứ lúc nào (phím ESC)
- **Perfect combo**: Chuỗi perfect tăng bonus điểm

### Âm thanh & Đồ họa
- **Nhạc nền**: Âm nhạc vòng lặp trong suốt game
- **Sound effects**: Âm thanh đặc biệt cho perfect block
- **2 Background**: Background khác nhau cho tầng dưới và tầng cao
- **4 Skin blocks**: Perfect và Normal với 4 màu ngẫu nhiên

## 🎮 Cách chơi

### Điều khiển
- **SPACE**: Thả block xuống tháp
- **ESC**: Tạm dừng game
- **Click chuột**: Tương tác với menu

### Mục tiêu
Xây tháp cao nhất có thể bằng cách đặt các block chính xác lên nhau. Mỗi block được đặt hoàn hảo sẽ tăng điểm và làm block tiếp theo rộng hơn.

### Tips
1. **Chờ đúng thời điểm**: Block đu đưa theo quy luật, tính toán vị trí trước khi thả
2. **Combo Perfect**: Đặt liên tiếp nhiều perfect block để nhận bonus x2, x3...
3. **Cẩn thận với gió**: Từ level 4 trở đi, gió sẽ đẩy block sang trái/phải
4. **Level 5+ khó hơn**: Block sẽ bị thu nhỏ nếu đặt sai vị trí

## 🎯 Hệ thống điểm

### Độ chính xác
- **Perfect** (offset ≤ 15px): 
  - +100 điểm
  - Block tăng rộng +10px
  - Tích lũy combo perfect
  
- **Good** (offset ≤ 25px):
  - +50 điểm
  - Giữ nguyên kích thước
  - Reset combo
  
- **Bad** (offset > 25px):
  - +25 điểm
  - **Từ level 5+**: Block bị thu nhỏ 20px (tối thiểu 40px)
  - Block giữ nguyên vị trí thả (không căn giữa)
  - Reset combo

### Combo Perfect
Đặt liên tiếp nhiều perfect block:
- 2 perfect: x2 bonus (200 điểm/block)
- 3 perfect: x3 bonus (300 điểm/block)
- 4+ perfect: x4 bonus (400 điểm/block)

## 📁 Cấu trúc dự án

```
towerbuilder/
├── towerbuilder/
│   ├── main.py                      # File game chính (2010 lines)
│   ├── login_screen.py              # Màn hình đăng nhập/đăng ký
│   ├── firebase_config.py           # ✅ Cấu hình Firebase sẵn (dùng chung)
│   ├── leaderboard.json             # Bảng xếp hạng local (backup)
│   └── assets/
│       ├── background1.png          # Background tầng dưới
│       ├── background2.png          # Background tầng cao (lặp lại)
│       ├── perfect1.png - perfect4.png   # 4 skin block perfect
│       ├── normal1.png - normal4.png     # 4 skin block normal
│       ├── basicsong.mp3            # Nhạc nền
│       ├── land.mp3                 # Âm thanh perfect
│       └── 23.mp3                   # Âm thanh khác
├── .gitignore
└── README.md                        # File này
```

## 🔧 Cài đặt

### Yêu cầu hệ thống
- Python 3.13.5+ (khuyến nghị 3.13)
- Windows/Linux/MacOS
- Kết nối internet (cho Firebase online leaderboard)

> **� Firebase đã được cấu hình sẵn!**
> - Game tải về đã có `firebase_config.py` với Firebase được setup
> - Người chơi chỉ cần cài thư viện và chơi ngay
> - **Leaderboard online dùng chung** - thi đấu với mọi người!

### Cài đặt đơn giản (3 bước)

1. **Clone repository**
```bash
git clone https://github.com/inshanemode/game-tower-builder.git
cd game-tower-builder
```

2. **Cài đặt thư viện**
```bash
# Tạo môi trường ảo (khuyến nghị)
python -m venv venv

# Kích hoạt môi trường
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install pygame pyrebase4
```

**Lưu ý**: Nếu gặp lỗi với pyrebase4:
```bash
pip install Pyrebase4
# Hoặc thử:
pip install pyrebase4 --upgrade
```

3. **Chạy game**
```bash
cd towerbuilder
python main.py
```

✅ **Game khởi động với Firebase online leaderboard!**
- Đăng ký tài khoản mới hoặc đăng nhập
- Điểm số tự động lưu lên cloud
- Xem bảng xếp hạng toàn cầu

---

### � Chế độ Offline (không cần Firebase)

Nếu **không có internet** hoặc chỉ muốn chơi offline:

```bash
# Chỉ cần cài pygame
pip install pygame

# Chạy game
python main.py
```

Game tự động chuyển sang **local leaderboard** khi:
- Không có internet
- Không cài pyrebase4
- Firebase bị lỗi

Điểm số lưu vào `leaderboard.json` thay vì cloud.

## 🔥 Về Firebase Configuration

> **✅ Firebase đã được cấu hình sẵn!**
> 
> Game này sử dụng **Firebase dùng chung** để tất cả người chơi có thể:
> - Thi đấu trên cùng bảng xếp hạng
> - Đăng ký/đăng nhập tài khoản
> - Lưu điểm online tự động
>
> **Bạn KHÔNG cần setup Firebase của riêng mình!**

### Cách Firebase hoạt động

1. **Download game** → File `firebase_config.py` đã có sẵn
2. **Cài pyrebase4** → `pip install pyrebase4`
3. **Chạy game** → Firebase kết nối tự động
4. **Đăng ký/Đăng nhập** → Bắt đầu chơi và lưu điểm

### Firebase Database Rules (đã setup)

```json
{
  "rules": {
    "leaderboard": {
      ".read": true,
      "$uid": {
        ".write": "$uid === auth.uid",
        ".validate": "newData.hasChildren(['username', 'score', 'timestamp'])"
      }
    }
  }
}
```

**Bảo mật:**
- ✅ Mọi người đọc được leaderboard
- ✅ Chỉ ghi vào UID của chính mình
- ✅ Không thể sửa điểm người khác
- ✅ Dữ liệu phải có đủ trường bắt buộc

---

### 🛠️ (Tùy chọn) Setup Firebase riêng

<details>
<summary>Click để xem hướng dẫn setup Firebase của riêng bạn</summary>

Nếu muốn tạo Firebase project riêng thay vì dùng chung:

#### Bước 1: Tạo Firebase Project
1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Tạo project mới
3. Vào **Project Settings** → **General**
4. Cuộn xuống **Your apps** → Chọn **Web app** (</> icon)
5. Copy `firebaseConfig` object

#### Bước 2: Bật Firebase Authentication
1. Vào **Authentication** → **Sign-in method**
2. Bật **Email/Password**

#### Bước 3: Bật Realtime Database
1. Vào **Realtime Database** → **Create Database**
2. Chọn region: **asia-southeast1** (Singapore)
3. Chọn **Start in test mode**

#### Bước 4: Cấu hình Database Rules
Paste rules phía trên vào **Rules** tab

#### Bước 5: Cập nhật config
Mở `towerbuilder/firebase_config.py` và thay thế bằng config của bạn:
```python
FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-project.firebaseapp.com",
    "databaseURL": "https://your-project.asia-southeast1.firebasedatabase.app",
    "projectId": "your-project",
    "storageBucket": "your-project.firebasestorage.app",
    "messagingSenderId": "123456789",
    "appId": "1:123456789:web:abcdef"
}
```

</details>

## 🚀 Chạy game

### Chạy game (Khuyến nghị - với Firebase) 🔥
```bash
cd towerbuilder
python main.py
```

**Khi khởi động:**
1. Màn hình đăng nhập xuất hiện
2. Đăng ký tài khoản mới (hoặc đăng nhập nếu đã có)
3. Bắt đầu chơi với **online leaderboard**
4. Điểm số tự động lưu lên cloud
5. Xem bảng xếp hạng toàn cầu

✅ **Firebase connection:** Tất cả người chơi dùng chung 1 database → thi đấu với nhau!

---

### Chạy Offline (không cần internet) ⚡
Nếu không có internet hoặc không cài pyrebase4:

```bash
cd towerbuilder
python main.py
```

**Terminal sẽ hiển thị:**
```
Firebase chưa được cấu hình. Chỉ dùng leaderboard local.
✓ Đã tải background2.png
✓ Đã bật nhạc nền
```

✅ Game chạy với local leaderboard (`leaderboard.json`)

---

### Debug & Troubleshooting

Kiểm tra terminal output để xem:
- ✅ `FIREBASE_ENABLED = True` → Online mode
- ⚠️ `Firebase chưa được cấu hình` → Offline mode
- ✓ Assets loading status
- ❌ Errors và warnings

### So sánh 2 chế độ

| Tính năng | Offline Mode | Online Mode (Firebase) |
|-----------|--------------|------------------------|
| Cài đặt | `pygame` | `pygame` + `pyrebase4` |
| Đăng nhập | Không | Có (Email/Password) |
| Leaderboard | Local JSON | **Global online + Local** |
| Username | "Guest" | Tên tài khoản đăng ký |
| Thi đấu | Một mình | **Với mọi người!** |
| Điểm số | Lưu máy | **Lưu cloud** |

## ⚙️ Cơ chế game

### Hệ thống độ khó (Difficulty System)

#### Level 1-10: Predefined
```python
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 250, "grav": 0.7},
    2: {"force_multiplier": 2.3, "rope_length": 250, "grav": 0.75},
    3: {"force_multiplier": 2.6, "rope_length": 220, "grav": 0.8},
    4: {"force_multiplier": 2.9, "rope_length": 220, "grav": 0.85},
    5: {"force_multiplier": 3.1, "rope_length": 200, "grav": 0.9},
    6: {"force_multiplier": 3.4, "rope_length": 200, "grav": 0.95},
    7: {"force_multiplier": 4.0, "rope_length": 200, "grav": 1.0},
    8: {"force_multiplier": 5.0, "rope_length": 180, "grav": 1.1},
    9: {"force_multiplier": 6.0, "rope_length": 180, "grav": 1.2},
    10: {"force_multiplier": 8.0, "rope_length": 180, "grav": 1.3}
}
```

#### Level 11+: Dynamic scaling
```python
force_multiplier = 8 + (level - 10)  # Tăng +1 mỗi level
rope_length = 180  # Giữ nguyên
grav = 1.3  # Giữ nguyên
```

**Ví dụ**:
- Level 11: force_multiplier = 9
- Level 15: force_multiplier = 13
- Level 20: force_multiplier = 18

### Hệ thống gió (Wind System)

#### Điều kiện kích hoạt
- Bắt đầu từ **Level 4** trở đi
- Chỉ tác động khi block đang **swinging** (đu đưa)

#### Cường độ gió
```python
wind_force = random.uniform(0.0005, 0.002)  # Ngẫu nhiên
wind_direction = random.choice([-1, 1])     # Trái (-1) hoặc phải (1)
```

#### Thời gian thay đổi (Dynamic interval)
```python
wind_change_interval = max(60, 180 - (level - 4) * 10)  # frames
```

**Bảng thời gian**:
| Level | Interval (frames) | Giây (~60 FPS) |
|-------|-------------------|----------------|
| 4     | 180               | 3.0s           |
| 6     | 160               | 2.7s           |
| 8     | 140               | 2.3s           |
| 10    | 120               | 2.0s           |
| 12    | 100               | 1.7s           |
| 14+   | 60 (min)          | 1.0s           |

### Block Shrinking (Level 5+)

#### Điều kiện
- Chỉ xảy ra khi **offset > 25px** (BAD placement)
- Chỉ áp dụng từ **Level 5** trở đi

#### Công thức
```python
SHRINK_AMOUNT = 20  # px
MIN_WIDTH = 40      # px

new_width = max(current_width - SHRINK_AMOUNT, MIN_WIDTH)
```

#### Hành vi
- Block bị thu nhỏ **20px** mỗi lần đặt sai
- Không nhỏ hơn **40px**
- **Giữ nguyên vị trí thả** (không căn giữa tự động)
- Block nghiêng về phía sai → khó hơn cho lần đặt tiếp theo

**Ví dụ**:
- Block 150px → đặt BAD → 130px
- Block 50px → đặt BAD → 40px (MIN)
- Block 40px → đặt BAD → 40px (không thu nhỏ thêm)

### Camera System

#### Smooth follow
```python
target_y = 512 - (tower.blocks[-1].ylast - tower.blocks[0].ylast) - 128
camera_offset += (target_y - camera_offset) * 0.1  # Lerp 10%
```

Camera di chuyển mượt mà theo block cao nhất, giữ block cuối ở vị trí cố định trên màn hình.

#### Parallax backgrounds
- **Background1**: Hiển thị 1 lần ở tầng đất
- **Background2**: Lặp lại vô hạn phía trên, tạo cảm giác cao vô tận

### Physics Engine

#### Pendulum motion (Con lắc)
```python
angle += angular_velocity
angular_velocity += force * force_multiplier

x = pivot_x + rope_length * sin(radians(angle))
y = pivot_y + rope_length * cos(radians(angle))
```

#### Gravity (Rơi tự do)
```python
velocity_y += grav  # Gia tốc trọng trường
ylast += velocity_y
```

## 🐛 Troubleshooting

### Lỗi thường gặp

#### `ModuleNotFoundError: No module named 'pygame'`
```bash
pip install pygame
```

#### `ModuleNotFoundError: No module named 'pyrebase'`
```bash
pip install pyrebase4
```

#### Firebase không hoạt động
- Kiểm tra `firebase_config.py` có đúng API keys không
- Kiểm tra Firebase Authentication đã bật Email/Password chưa
- Kiểm tra Database Rules có cho phép đọc/ghi chưa
- Game vẫn chạy được với local leaderboard nếu Firebase lỗi

#### Không có âm thanh
- Kiểm tra file `.mp3` trong `assets/` folder
- Kiểm tra volume máy tính
- Game vẫn chạy được không có âm thanh

#### Lỗi asset không tìm thấy
```
⚠ Không tìm thấy background1.png, tạo background mặc định
```
- Tải assets từ repository
- Đảm bảo folder structure đúng: `towerbuilder/assets/*.png`

## 📊 Database Schema

### Firebase Realtime Database
```json
{
  "leaderboard": {
    "user123": {
      "username": "PlayerName",
      "score": 1234,
      "timestamp": 1730332800
    },
    "user456": {
      "username": "AnotherPlayer",
      "score": 5678,
      "timestamp": 1730419200
    }
  }
}
```

### Local leaderboard.json
```json
[
  {
    "username": "Player1",
    "score": 1234,
    "timestamp": 1730332800
  },
  {
    "username": "Player2",
    "score": 5678,
    "timestamp": 1730419200
  }
]
```

## 🎨 Customization

### Thay đổi độ khó
Chỉnh sửa `DIFFICULTY_LEVELS` trong `main.py`:
```python
DIFFICULTY_LEVELS = {
    1: {"force_multiplier": 2.0, "rope_length": 250, "grav": 0.7},
    # ... thêm level hoặc điều chỉnh giá trị
}
```

### Thay đổi block shrinking
```python
SHRINK_AMOUNT = 20  # Tăng = khó hơn, giảm = dễ hơn
MIN_WIDTH = 40      # Kích thước nhỏ nhất
```

### Thay đổi cường độ gió
```python
wind_force = random.uniform(0.0005, 0.002)  # Tăng giá trị = gió mạnh hơn
```

### Thay đổi combo perfect
Chỉnh sửa trong `Block.drop()`:
```python
if offset <= 15:  # Perfect: thay 15 thành giá trị khác
    # ...
```

## 🤝 Contributing

Contributions are welcome! 

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Tạo Pull Request

## 📝 License

This project is for educational purposes.

## 👤 Author

- GitHub: [@inshanemode](https://github.com/inshanemode)
- Project: [game-tower-builder](https://github.com/inshanemode/game-tower-builder)

## 🙏 Acknowledgments

- Pygame community
- Firebase documentation
- Inspiration from classic tower building games

---

**Chúc bạn chơi vui vẻ! 🎮🏗️**

*Nếu gặp vấn đề, hãy tạo Issue trên GitHub hoặc liên hệ qua Discord.*
