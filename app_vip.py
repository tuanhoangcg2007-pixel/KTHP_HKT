import cv2
import os
import numpy as np

# ==========================================
# CẤU HÌNH MENU VIP THEO BẢNG GIÁ MỚI
# (Tên class tiếng Việt không dấu để hiển thị mượt trên OpenCV)
# ==========================================
PRICE_MENU = {
    'Com_trang': {'name': 'Com trang', 'price': 10000, 'vn_name': 'Cơm trắng'},
    'Dau_hu_sot_ca': {'name': 'Dau hu sot ca', 'price': 25000, 'vn_name': 'Đậu hũ sốt cà'},
    'Ca_hu_kho': {'name': 'Ca hu kho', 'price': 30000, 'vn_name': 'Cá hú kho'},
    'Thit_kho_trung': {'name': 'Thit kho trung', 'price': 30000, 'vn_name': 'Thịt kho trứng'},
    'Thit_kho': {'name': 'Thit kho', 'price': 25000, 'vn_name': 'Thịt kho'},
    'Canh_chua_co_ca': {'name': 'Canh chua co ca', 'price': 25000, 'vn_name': 'Canh chua có cá'},
    'Canh_chua_khong_ca': {'name': 'Canh chua khong ca', 'price': 10000, 'vn_name': 'Canh chua không cá'},
    'Suon_nuong': {'name': 'Suon nuong', 'price': 30000, 'vn_name': 'Sườn nướng'},
    'Canh_rau': {'name': 'Canh rau', 'price': 7000, 'vn_name': 'Canh rau'},
    'Rau_xao': {'name': 'Rau xao', 'price': 10000, 'vn_name': 'Rau xào'},
    'Trung_chien': {'name': 'Trung chien', 'price': 25000, 'vn_name': 'Trứng chiên'}
}

# ==========================================
# HÀM TẠO GIAO DIỆN HÓA ĐƠN & MÃ QR (DASHBOARD)
# ==========================================
def create_dashboard(detected_image, detected_items, total_price, qr_image_path='qr_bank.jpg'):
    """
    Hàm này tạo ra một bảng điều khiển gộp:
    [ Ảnh đã nhận diện (Trái) | Hóa đơn & QR Code (Phải) ]
    """
    # Kích thước khung giao diện: Cao 720, Rộng 1280
    bg_height, bg_width = 720, 1280
    dashboard = np.ones((bg_height, bg_width, 3), dtype=np.uint8) * 245  # Nền màu xám nhạt

    # 1. Xử lý ảnh nhận diện bên trái
    h, w = detected_image.shape[:2]
    # Resize ảnh nhận diện cho vừa khu vực bên trái (Khu vực: 800x720)
    scale = min(700/w, 700/h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_detected = cv2.resize(detected_image, (new_w, new_h))
    
    # Căn giữa ảnh bên trái
    y_offset = (bg_height - new_h) // 2
    x_offset = (750 - new_w) // 2
    dashboard[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_detected

    # Kẻ vạch phân cách
    cv2.line(dashboard, (770, 20), (770, 700), (200, 200, 200), 2)

    # 2. Xử lý in Hóa Đơn bên phải (Cột X = 800)
    text_x = 800
    cv2.putText(dashboard, "HOA DON THANH TOAN", (text_x + 40, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
    cv2.line(dashboard, (text_x, 80), (text_x + 450, 80), (0, 0, 0), 2)

    y_pos = 120
    if not detected_items:
        cv2.putText(dashboard, "Chua chon mon an", (text_x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        for item_key, count in detected_items.items():
            if item_key in PRICE_MENU:
                name = PRICE_MENU[item_key]['name']
                price = PRICE_MENU[item_key]['price']
                item_total = price * count
                # Ghi tên món
                cv2.putText(dashboard, f"{count}x {name}", (text_x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 1)
                # Ghi giá tiền căn lề phải
                cv2.putText(dashboard, f"{item_total:,} d", (text_x + 320, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                y_pos += 35

    # Dòng tổng tiền
    cv2.line(dashboard, (text_x, y_pos), (text_x + 450, y_pos), (0, 0, 0), 1)
    y_pos += 40
    cv2.putText(dashboard, "TONG TIEN:", (text_x, y_pos), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(dashboard, f"{total_price:,} VND", (text_x + 200, y_pos), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 2)

    # 3. Chèn ảnh QR Code xuống dưới hóa đơn
    y_qr_start = y_pos + 40
    if os.path.exists(qr_image_path):
        qr_img = cv2.imread(qr_image_path)
        # Thay đổi kích thước QR Code về 250x250
        qr_img = cv2.resize(qr_img, (250, 250))
        # Căn giữa mã QR trong khu vực bên phải
        qr_x_offset = text_x + 100
        dashboard[y_qr_start:y_qr_start+250, qr_x_offset:qr_x_offset+250] = qr_img
        
        # Ghi chú dưới QR
        cv2.putText(dashboard, "Quet ma QR de chuyen khoan", (text_x + 50, y_qr_start + 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 0, 0), 2)
    else:
        # Nếu chưa có file ảnh QR, tạo ô trống báo thiếu
        cv2.rectangle(dashboard, (text_x + 100, y_qr_start), (text_x + 350, y_qr_start + 250), (200, 200, 200), -1)
        cv2.putText(dashboard, "[THIEU ANH QR BANK]", (text_x + 120, y_qr_start + 125), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return dashboard

# ==========================================
# CHẠY NHẬN DIỆN VÀ TÍNH TIỀN (AI MODE)
# ==========================================
def process_vip_billing(image_path, model_path='best.pt'):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] Cài ultralytics trước nha bro: pip install ultralytics")
        return

    if not os.path.exists(model_path):
        print(f"[ERROR] Không thấy model '{model_path}'. Chép model vào đây đã!")
        return

    print("\n[AI] Đang nạp hệ thống thần kinh nhân tạo...")
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    
    if image is None:
        print("[ERROR] Không đọc được ảnh. Đổi tên đúng chưa?")
        return
        
    output_image = image.copy()
    results = model(image_path)[0]
    
    total_price = 0
    detected_items = {}

    for box in results.boxes:
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = xyxy
        
        class_id = int(box.cls[0].cpu().numpy())
        class_key = model.names[class_id]

        # Khớp với dữ liệu Menu
        if class_key in PRICE_MENU:
            display_name = PRICE_MENU[class_key]['name']
            price = PRICE_MENU[class_key]['price']
            
            total_price += price
            detected_items[class_key] = detected_items.get(class_key, 0) + 1

            # Vẽ khung và tên món lên ảnh góc (Màu xanh dương cho VIP)
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (255, 100, 0), 2)
            cv2.putText(output_image, f"{display_name}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)
        else:
            print(f"[CẢNH BÁO] Nhận diện được {class_key} nhưng chưa có trong Menu bảng giá!")

    # IN RA TERMINAL CÓ DẤU TIẾNG VIỆT CHO ĐẸP
    print("\n" + "★"*15 + " HÓA ĐƠN VIP CHI TIẾT " + "★"*15)
    for item_key, count in detected_items.items():
        vn_name = PRICE_MENU[item_key]['vn_name']
        price = PRICE_MENU[item_key]['price']
        print(f" 🍲 {vn_name}: {count} x {price:,} đ = {count*price:,} đ")
    print("="*50)
    print(f" 💰 TỔNG THANH TOÁN: {total_price:,} VNĐ")
    print("★"*50 + "\n")

    # Gọi hàm gộp tất cả vào Dashboard
    final_dashboard = create_dashboard(output_image, detected_items, total_price, qr_image_path='qr_bank.jpg')

    # Xuất ảnh và hiển thị
    cv2.imwrite('Dashboard_ThanhToan_VIP.jpg', final_dashboard)
    print(">> Đã xuất file thành phẩm: Dashboard_ThanhToan_VIP.jpg")
    
    cv2.imshow("He Thong Thanh Toan Tu Dong VIP - Bro Edition", final_dashboard)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # --- BRO THAY ĐỔI TÊN FILE ẢNH TEST TẠI ĐÂY ---
    HINH_ANH_TEST = 'image_cc9c48.jpg'  
    FILE_MODEL = 'best.pt'
    
    # Chạy thôi!
    process_vip_billing(HINH_ANH_TEST, FILE_MODEL)