// Hiển thị kết quả
function showResult(data) {
    let statusClass = "AN_TOAN";
    let displayStatus = data.status;

    if (data.status === "ĐỘC HẠI" || data.status === "DOC_HAI") {
        statusClass = "DOC_HAI";
        displayStatus = "ĐỘC HẠI";
    }
    if (data.status === "CẢNH BÁO" || data.status === "CANH_BAO") {
        statusClass = "CANH_BAO";
        displayStatus = "CẢNH BÁO";
    }
    if (data.status === "KHONG_XAC_DINH") {
        statusClass = "KHONG_XAC_DINH";
        displayStatus = "CHƯA RÕ";
    }

    document.getElementById('finalStatus').className = `status-badge ${statusClass}`;
    document.getElementById('finalStatus').innerText = displayStatus;
    document.getElementById('adviceText').innerHTML = data.advice || data.error;
    document.getElementById('scanTime').innerText = data.time || "0";

    const ul = document.getElementById('detailsList');
    ul.innerHTML = '';
    if (data.details) {
        data.details.forEach(item => {
            let li = document.createElement('li');
            li.innerHTML = item;
            li.className = "mb-2";
            ul.appendChild(li);
        });
    }
    document.getElementById('resultArea').style.display = 'block';
}

// Lưu lịch sử quét
async function saveHistory(type, input, data) {
    try {
        const tableName = window.currentUser ? "lich_su_quet" : "da_quet";
        const insertData = {
            loai_quet: type,
            doi_tuong: input,
            ket_qua: data.status,
            du_lieu_chi_tiet: data,
            diem_rui_ro: data.risk_score || 0,
            huong_dan_khac_phuc: data.advice || ""
        };
        if (window.currentUser) {
            insertData.ma_nguoi_dung = window.currentUser.id;
        }
        const { error } = await window.sb.from(tableName).insert([insertData]);
        if (error) console.error("Lỗi lưu history:", error);
        else console.log(`Đã lưu vào ${tableName}`);
    } catch (err) {
        console.error("Exception saveHistory:", err);
    }
}

// Biến chống spam
let isScanning = false;

// Quét URL
window.startUrlScan = async function () {
    if (isScanning) return;
    isScanning = true;

    if (!window.isAuthReady) {
        alert("Đang tải thông tin đăng nhập, vui lòng thử lại!");
        isScanning = false;
        return;
    }

    const url = document.getElementById('urlInput').value;
    if (!url) {
        alert('Vui lòng nhập link!');
        isScanning = false;
        return;
    }

    document.getElementById('urlSpinner').style.display = 'inline-block';
    document.getElementById('scanUrlBtn').disabled = true;
    document.getElementById('resultArea').style.display = 'none';

    try {
        const response = await fetch('/api/scan/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            showResult(data);
            await saveHistory("url", url, data);
        }
    } catch (error) {
        alert('Lỗi kết nối Server!');
    } finally {
        document.getElementById('urlSpinner').style.display = 'none';
        document.getElementById('scanUrlBtn').disabled = false;
        isScanning = false;
    }
};

// Quét File
window.startFileScan = async function () {
    if (isScanning) return;
    isScanning = true;

    if (!window.isAuthReady) {
        alert("Đang tải thông tin đăng nhập!");
        isScanning = false;
        return;
    }

    const fileInput = document.getElementById('fileInput');
    if (fileInput.files.length === 0) {
        alert('Vui lòng chọn 1 tệp tin!');
        isScanning = false;
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById('fileSpinner').style.display = 'inline-block';
    document.getElementById('scanFileBtn').disabled = true;
    document.getElementById('resultArea').style.display = 'none';

    try {
        const response = await fetch('/api/scan/file', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            showResult(data);
            await saveHistory("file", file.name, data);
        }
    } catch (error) {
        alert('Lỗi tải file lên Server!');
    } finally {
        document.getElementById('fileSpinner').style.display = 'none';
        document.getElementById('scanFileBtn').disabled = false;
        isScanning = false;
    }
};