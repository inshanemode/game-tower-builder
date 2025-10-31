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
    
    def register(self, email, password, username):
        """Đăng ký user mới"""
        try:
            user = auth.create_user_with_email_and_password(email, password)
            self.current_user = user
            self.user_id = user['localId']
            self.username = username
            
            # Lưu username vào database với token
            user_token = user['idToken']
            db.child("users").child(self.user_id).set({
                "username": username,
                "email": email
            }, user_token)
            return True, "Đăng ký thành công!"
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                return False, "Email đã tồn tại!"
            elif "WEAK_PASSWORD" in error_msg:
                return False, "Mật khẩu quá yếu (tối thiểu 6 ký tự)!"
            elif "INVALID_EMAIL" in error_msg:
                return False, "Email không hợp lệ!"
            return False, f"Đăng ký thất bại!"
    
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
    
    def save_score(self, score, level):
        """Lưu điểm lên Firebase"""
        if not self.is_logged_in():
            return False, "Chưa đăng nhập!"
        
        try:
            # Lấy token hiện tại
            user_token = self.current_user.get('idToken')
            
            # Lấy điểm cao nhất hiện tại
            user_scores = db.child("scores").child(self.user_id).get(user_token)
            current_best = 0
            if user_scores.val():
                current_best = user_scores.val().get('best_score', 0)
            
            # Chỉ cập nhật nếu điểm mới cao hơn
            if score > current_best:
                db.child("scores").child(self.user_id).set({
                    "username": self.username,
                    "best_score": score,
                    "best_level": level,
                    "timestamp": {".sv": "timestamp"}
                }, user_token)
                return True, "Kỷ lục mới!"
            return True, "Điểm đã lưu!"
        except Exception as e:
            return False, f"Lỗi lưu điểm: {str(e)}"
    
    def get_leaderboard(self, limit=10):
        """Lấy bảng xếp hạng"""
        try:
            # Lấy token nếu đã đăng nhập
            user_token = None
            if self.is_logged_in() and self.current_user:
                user_token = self.current_user.get('idToken')
            
            # Lấy tất cả scores (không dùng orderBy để tránh lỗi index)
            if user_token:
                scores = db.child("scores").get(user_token)
            else:
                # Nếu chưa đăng nhập, không thể lấy leaderboard online
                print("Cần đăng nhập để xem leaderboard online")
                return []
            
            leaderboard = []
            if scores.val():
                for user_id, data in scores.val().items():
                    leaderboard.append({
                        'username': data.get('username', 'Anonymous'),
                        'score': data.get('best_score', 0),
                        'level': data.get('best_level', 0)
                    })
            
            # Sắp xếp giảm dần và lấy top limit
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            return leaderboard[:limit]
        except Exception as e:
            print(f"Lỗi tải leaderboard: {e}")
            return []

# Tạo instance global
firebase_auth = FirebaseAuth()
