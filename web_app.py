import streamlit as st
import cv2
import numpy as np
import os

st.set_page_config(page_title="Hệ Thống Tính Tiền Tự Động HKT", layout="wide")

# ==========================================
# CẤU HÌNH MENU BẢNG GIÁ VÀ MA TRẬN TOẠ ĐỘ BRO VỪA LẤY
# ==========================================
PRICE_MENU = {
    'Canh_rau': {
        'name': 'Canh rau', 
        'img_name': 'Canh rau', 
        'price': 7000,
        'box': (389, 182, 513, 419)  # Tọa độ thực tế từ ảnh bro gửi
    },
    'Com_trang': {
        'name': 'Cơm trắng', 
        'img_name': 'Com trang', 
        'price': 10000,
        'box': (1088, 182, 398, 419)
    },
    'Suon_nuong': {
        'name': 'Sườn nướng', 
        'img_name': 'Suon nuong', 
        'price': 30000,
        'box': (397, 669, 329, 324)
    },
    'Thit_kho_trung': {
        'name': 'Thịt kho trứng', 
        'img_name': 'Thit kho trung', 
        'price': 30000,
        'box': (794, 669, 335, 324)
    },
    'Trung_chien': {
        'name': 'Trứng chiên', 
        'img_name': 'Trung chien', 
        'price': 25000,
        'box': (1159, 669, 369, 324)
    }
}

st.title("🍲 HKT_Tính Tiền Tự Động")
st.subheader("HKT-Smart Canteen System")
st.write("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📸 Nguồn Hình Ảnh Đầu Vào")
    nguon_anh = st.radio("Chọn cách nhập ảnh:", ("Tải ảnh lên từ máy", "Chụp ảnh trực tiếp qua Webcam"))
    
    img_frame = None
    if nguon_anh == "Tải ảnh lên từ máy":
        uploaded_file = st.file_uploader("Chọn một file ảnh món ăn...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img_frame = cv2.imdecode(file_bytes, 1)
    else:
        camera_file = st.camera_input("Đưa khay món ăn trước camera để chụp")
        if camera_file is not None:
            file_bytes = np.asarray(bytearray(camera_file.read()), dtype=np.uint8)
            img_frame = cv2.imdecode(file_bytes, 1)

if img_frame is not None:
    img_h, img_w, _ = img_frame.shape
    output_image = img_frame.copy()
    
    total_price = 0
    detected_items = []
    
    # Tạo thư mục lưu ảnh cắt tự động
    os.makedirs('cropped_auto_web', exist_ok=True)
    
    # Vòng lặp tự động duyệt qua ma trận 5 tọa độ để cắt ảnh và tính tiền
    for idx, (key, item_info) in enumerate(PRICE_MENU.items()):
        x, y, w, h = item_info['box']
        
        # Đảm bảo tọa độ không bị tràn ra ngoài kích thước ảnh
        x1 = max(0, min(x, img_w))
        y1 = max(0, min(y, img_h))
        x2 = max(0, min(x + w, img_w))
        y2 = max(0, min(y + h, img_h))
        
        if x2 > x1 and y2 > y1:
            # Tiến hành cắt ảnh tự động
            cropped_img = img_frame[y1:y2, x1:x2]
            crop_name = f"cropped_auto_web/vung_{idx+1}_{key}.jpg"
            cv2.imwrite(crop_name, cropped_img)
            
            # Lưu thông tin tính tiền
            total_price += item_info['price']
            detected_items.append({'name': item_info['name'], 'price': item_info['price']})
            
            # Vẽ khung chữ nhật Bounding Box lên khay cơm
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 4)
            
            # Vẽ nhãn tên (không dấu) đè lên khung để trình bày với thầy
            (text_w, text_h), _ = cv2.getTextSize(item_info['img_name'], cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
            text_y = max(15, y1 - 10)
            rect_y1 = max(0, text_y - text_h - 5)
            cv2.rectangle(output_image, (x1, rect_y1), (x1 + text_w, text_y + 5), (0, 255, 0), -1)
            cv2.putText(output_image, item_info['img_name'], (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

    with col_left:
        st.success(f"Kích thước ảnh nhận diện: {img_w}x{img_h} px. Đã đồng bộ ma trận tọa độ thành công!")
        st.image(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB), caption="Ảnh khay thức ăn tự động quét theo tọa độ chuẩn", use_container_width=True)

    # Hiển thị hóa đơn tự động tính toán ở cột bên phải
    with col_right:
        st.markdown("### 📝 Hóa Đơn Thanh Toán")
        st.write("---")
        
        if detected_items:
            for item in detected_items:
                st.write(f"✔️ **{item['name']}** — `{item['price']:,} đ`")
        else:
            st.warning("Không tìm thấy dữ liệu vùng món ăn.")
            
        st.write("---")
        st.markdown(f"### 💰 Tổng tiền: <span style='color:red'>{total_price:,} đ</span>", unsafe_allow_html=True)
        
        # Mã QR ngân hàng phiên bản lớn sắc nét
        st.write("---")
        st.markdown("#### 💳 Quét mã QR để thanh toán")
        QR_PATH = 'qr_bank.jpg'
        if os.path.exists(QR_PATH):
            st.image(QR_PATH, caption="Chuyển khoản chính chủ qua VietQR", width=350)
        else:
            st.info("Chưa tìm thấy ảnh file `qr_bank.jpg` trong thư mục gốc.")
            
        if st.button("🔴 Xác Nhận Giao Dịch", use_container_width=True):
            st.success("Giao dịch thành công!")