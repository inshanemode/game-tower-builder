# Firebase configuration (local file)
# IMPORTANT: Do NOT commit this file to version control. It contains keys for your Firebase project.

import pyrebase

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyA91OGzY8mD6-SaA_zXY-VjcJTLnxJEyvs",
    "authDomain": "tower-builder-58d24.firebaseapp.com",
    "databaseURL": "https://tower-builder-58d24-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "tower-builder-58d24",
    "storageBucket": "tower-builder-58d24.firebasestorage.app",
    "messagingSenderId": "959524496583",
    "appId": "1:959524496583:web:3c276a3e87293ba68c4ae2",
    "measurementId": "G-LJTRFB5CLD",
}

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

class FirebaseAuth:
    def __init__(self):
        self.current_user = None
        self.user_id = None
        self.username = None
    
    def is_username_taken(self, username, user_token=None):
        """Kiểm tra xem username đã được dùng chưa trong /usernames"""
        try:
            snapshot = db.child("usernames").child(username).get(user_token)
            return snapshot.val() is not None
        except Exception as e:
            print(f"Lỗi kiểm tra username trùng: {e}")
            return False

    def register(self, email, password, username):
        """Đăng ký user mới với username duy nhất"""
        try:
            # Bước 1: Tạo tài khoản Firebase bằng email & mật khẩu
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            user_token = user['idToken']

            # Bước 2: Kiểm tra username có bị trùng không
            if self.is_username_taken(username, user_token):
                return False, "Tên người dùng đã tồn tại!"

            # Bước 3: Lưu thông tin vào /users
            db.child("users").child(user_id).set({
                "username": username,
                "email": email
            }, user_token)

            # Bước 4: Ghi username vào /usernames để đánh dấu đã dùng
            db.child("usernames").child(username).set(user_id, user_token)

            # Cập nhật session
            self.current_user = user
            self.user_id = user_id
            self.username = username

            return True, "Đăng ký thành công!"

        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                return False, "Email đã tồn tại!"
            elif "WEAK_PASSWORD" in error_msg:
                return False, "Mật khẩu quá yếu (tối thiểu 6 ký tự)!"
            elif "INVALID_EMAIL" in error_msg:
                return False, "Email không hợp lệ!"
            return False, f"Đăng ký thất bại: {error_msg}"
    
    def login(self, email, password):
        """Đăng nhập"""
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            self.current_user = user
            self.user_id = user['localId']
            
            # Lấy token để truy cập database
            user_token = user['idToken']
            
            # Lấy username từ database với token
            try:
                user_data = db.child("users").child(self.user_id).get(user_token)
                if user_data.val():
                    self.username = user_data.val().get('username', email.split('@')[0])
                else:
                    self.username = email.split('@')[0]
            except:
                # Nếu lỗi khi lấy username, dùng email làm username
                self.username = email.split('@')[0]
            
            return True, f"Chào mừng {self.username}!"
        except Exception as e:
            error_msg = str(e)
            if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                return False, "Email hoặc mật khẩu không đúng!"
            elif "EMAIL_NOT_FOUND" in error_msg:
                return False, "Email không tồn tại!"
            elif "TOO_MANY_ATTEMPTS" in error_msg:
                return False, "Quá nhiều lần thử! Vui lòng thử lại sau."
            return False, "Đăng nhập thất bại!"
    
    def logout(self):
        """Đăng xuất"""
        self.current_user = None
        self.user_id = None
        self.username = None
    
    def is_logged_in(self):
        """Kiểm tra đã đăng nhập chưa"""
        return self.current_user is not None
    
    def save_score(self, score, level, mode="infinite"):
        """Lưu điểm lên Firebase theo mode (infinite/time_attack/...)"""
        if not self.is_logged_in():
            return False, "Chưa đăng nhập!"
        
        try:
            # Lấy token hiện tại
            user_token = self.current_user.get('idToken')
            
            # Lấy điểm cao nhất hiện tại của mode này
            user_scores = db.child("scores").child(self.user_id).child(mode).get(user_token)
            current_best = 0
            if user_scores.val():
                current_best = user_scores.val().get('best_score', 0)
            
            # Chỉ cập nhật nếu điểm mới cao hơn
            if score > current_best:
                db.child("scores").child(self.user_id).child(mode).set({
                    "username": self.username,
                    "best_score": score,
                    "best_level": level,
                    "timestamp": {".sv": "timestamp"}
                }, user_token)
                return True, "Kỷ lục mới!"
            return True, "Điểm đã lưu!"
        except Exception as e:
            return False, f"Lỗi lưu điểm: {str(e)}"
    
    def get_leaderboard(self, limit=10, mode="infinite"):
        """Lấy bảng xếp hạng từ Firebase theo mode"""
        if not self.is_logged_in():
            return []  # Không đăng nhập → không load

        try:
            user_token = self.current_user['idToken']
            # Đọc toàn bộ /scores — được phép nhờ rule mới
            scores = db.child("scores").get(user_token)
            leaderboard = []
            if scores.val():
                for user_id, user_data in scores.val().items():
                    # Lọc theo mode
                    if mode in user_data:
                        mode_data = user_data[mode]
                        leaderboard.append({
                            'username': mode_data.get('username', 'Anonymous'),
                            'score': mode_data.get('best_score', 0),
                            'level': mode_data.get('best_level', 0)
                        })
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            return leaderboard[:limit]
        except Exception as e:
            print(f"Lỗi tải leaderboard: {e}")
            return []
    
# Tạo instance global
firebase_auth = FirebaseAuth()