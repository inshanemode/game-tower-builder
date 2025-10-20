# -*- coding: utf-8 -*-
# TEMPLATE FILE - Copy this to firebase_config.py and fill in your Firebase credentials

import pyrebase

# Lấy config từ Firebase Console > Project Settings > Your apps > Web app
# Xem hướng dẫn chi tiết trong file SETUP_FIREBASE.md

firebaseConfig = {
    "apiKey": "YOUR_API_KEY_HERE",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    # NOTE: Realtime Database URL is required by pyrebase. Use the region-specific URL shown in
    # your Firebase console (e.g., https://YOUR_PROJECT-default-rtdb.asia-southeast1.firebasedatabase.app)
    "databaseURL": "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID",
    # measurementId is optional for web; pyrebase doesn't use it
    "measurementId": "YOUR_MEASUREMENT_ID"
}


firebase = pyrebase.initialize_app(firebaseConfig)
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
            
            # Lưu username vào database
            db.child("users").child(self.user_id).set({
                "username": username,
                "email": email
            })
            return True, "Đăng ký thành công!"
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                return False, "Email đã tồn tại!"
            elif "WEAK_PASSWORD" in error_msg:
                return False, "Mật khẩu quá yếu (tối thiểu 6 ký tự)!"
            return False, f"Lỗi: {error_msg}"
    
    def login(self, email, password):
        """Đăng nhập"""
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            self.current_user = user
            self.user_id = user['localId']
            
            # Lấy username từ database
            user_data = db.child("users").child(self.user_id).get()
            if user_data.val():
                self.username = user_data.val().get('username', email.split('@')[0])
            else:
                self.username = email.split('@')[0]
            
            return True, f"Chào mừng {self.username}!"
        except Exception as e:
            error_msg = str(e)
            if "INVALID_PASSWORD" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
                return False, "Email hoặc mật khẩu không đúng!"
            return False, f"Lỗi: {error_msg}"
    
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
            # Lấy điểm cao nhất hiện tại
            user_scores = db.child("scores").child(self.user_id).get()
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
                })
                return True, "Kỷ lục mới!"
            return True, "Điểm đã lưu!"
        except Exception as e:
            return False, f"Lỗi lưu điểm: {str(e)}"
    
    def get_leaderboard(self, limit=10):
        """Lấy bảng xếp hạng"""
        try:
            scores = db.child("scores").order_by_child("best_score").limit_to_last(limit).get()
            
            leaderboard = []
            if scores.val():
                for user_id, data in scores.val().items():
                    leaderboard.append({
                        'username': data.get('username', 'Anonymous'),
                        'score': data.get('best_score', 0),
                        'level': data.get('best_level', 0)
                    })
            
            # Sắp xếp giảm dần
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            return leaderboard
        except Exception as e:
            print(f"Lỗi tải leaderboard: {e}")
            return []

# Tạo instance global
firebase_auth = FirebaseAuth()
