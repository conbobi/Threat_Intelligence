def get_master_advice(risk_score, is_file=False):
    """
    Trả về hướng dẫn khắc phục dựa trên điểm rủi ro.
    risk_score: số engine phát hiện độc hại (malicious).
    is_file: True nếu quét file, False nếu quét URL.
    """
    if is_file:
        if risk_score >= 2:
            return "⚠️ NGUY HIỂM TỘT ĐỘ: File này chứa mã độc!\n1. TUYỆT ĐỐI KHÔNG mở (click đúp) vào file này.\n2. Hãy xóa file ngay lập tức khỏi máy tính (Shift + Delete).\n3. Dùng phần mềm diệt virus quét toàn bộ ổ đĩa."
        elif risk_score == 1:
            return "⚠️ CẢNH BÁO: File có dấu hiệu khả nghi.\n1. Không nên chạy file này nếu không rõ nguồn gốc.\n2. Nên xóa đi cho an toàn."
        else:
            return "✅ AN TOÀN: File sạch, không phát hiện mã độc từ hơn 70 phần mềm diệt virus."
    else:
        if risk_score >= 2:
            return "⚠️ NGUY HIỂM CAO!\n1. Tuyệt đối KHÔNG truy cập đường dẫn này.\n2. Nếu đã lỡ bấm vào, hãy ngắt kết nối Internet ngay lập tức.\n3. Chạy phần mềm diệt virus quét toàn bộ máy tính.\n4. Đổi mật khẩu các tài khoản quan trọng (Email, Ngân hàng) từ một thiết bị khác."
        elif risk_score == 1:
            return "⚠️ CẢNH BÁO RỦI RO:\nCó 1 đơn vị bảo mật đánh giá đây là link xấu.\n1. Cẩn thận khi nhập thông tin cá nhân.\n2. Kiểm tra kỹ tên miền xem có bị giả mạo ký tự không (ví dụ: g00gle.com).\n3. Nên thoát ra nếu không thực sự cần thiết."
        else:
            return "✅ AN TOÀN:\nHiện tại chưa phát hiện mối đe dọa nào.\nTuy nhiên, hãy luôn duy trì thói quen cảnh giác, không cung cấp mật khẩu cho người lạ."