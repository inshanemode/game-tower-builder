# -*- coding: utf-8 -*-
"""
Test Firebase connection
Chạy file này để kiểm tra Firebase đã được cấu hình đúng chưa
"""

try:
    from firebase_config import firebase_auth
    print("✅ Firebase config đã được import thành công!")
    
    # Test connection
    try:
        leaderboard = firebase_auth.get_leaderboard(1)
        print("✅ Kết nối Firebase thành công!")
        print(f"   Số lượng scores trong leaderboard: {len(leaderboard)}")
        
        if leaderboard:
            print(f"   Top 1: {leaderboard[0]['username']} - {leaderboard[0]['score']} điểm")
        else:
            print("   (Chưa có điểm nào trong database)")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối Firebase:")
        print(f"   {str(e)}")
        print("\n💡 Kiểm tra:")
        print("   - Config trong firebase_config.py đã đúng chưa?")
        print("   - Đã bật Realtime Database chưa?")
        print("   - Đã setup Security Rules chưa?")
        print("   - Xem chi tiết trong SETUP_FIREBASE.md")
        
except ImportError as e:
    print("❌ Không tìm thấy file firebase_config.py")
    print("\n💡 Các bước cần làm:")
    print("   1. Copy file firebase_config.template.py thành firebase_config.py")
    print("   2. Điền thông tin Firebase của bạn vào file đó")
    print("   3. Hoặc xem hướng dẫn chi tiết trong SETUP_FIREBASE.md")
    print(f"\nLỗi chi tiết: {str(e)}")

print("\n" + "="*60)
print("Nhấn Enter để thoát...")
input()
