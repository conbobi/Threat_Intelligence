    const sb = window.supabase.createClient(
        "https://ddljfrzszcjtsenlgfqj.supabase.co",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkbGpmcnpzemNqdHNlbmxnZnFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzMzI5OTcsImV4cCI6MjA4NjkwODk5N30.id1F3yrnPEixcQIlq0knPOqPURdC9jSGhWbRcUzlwK8"
    );

     // No supabase direct call, we use our API
    let currentUser = null;

    // Load user info (from header_menu.js, but we need to know if logged in)
    async function loadUser() {
        // Giả sử header_menu.js đã có window.currentUser, nếu không thì gọi API /auth/status
        try {
            const response = await fetch('/auth/status'); // cần có route này
            const data = await response.json();
            if (data.logged_in) {
                currentUser = { id: data.user_id };
                const authArea = document.getElementById("authArea");
                authArea.innerHTML = `
                    <div class="d-flex align-items-center gap-3">
                        <a href="/history" class="menu-link" style="color: #3b82f6; background: rgba(59, 130, 246, 0.1);">
                            <i class="bi bi-clock-history"></i>
                            <span>Lịch sử</span>
                        </a>
                        <div class="position-relative d-flex align-items-center">
                            <i class="bi bi-person-circle fs-4 text-white" id="userIcon" style="cursor:pointer;"></i>
                            <div id="userTooltip" style="display:none; position:absolute; top:40px; right:0; background:#1e293b; padding:10px 15px; border-radius:8px; box-shadow:0 5px 15px rgba(0,0,0,0.5); white-space:nowrap; z-index:999;">
                                <div style="font-size:13px;">${data.email}</div>
                                <div onclick="confirmLogout()" style="cursor:pointer; font-size:13px; margin-top:6px;">Thoát</div>
                            </div>
                        </div>
                    </div>
                `;
                const icon = document.getElementById("userIcon");
                const tooltip = document.getElementById("userTooltip");
                if (icon && tooltip) {
                    icon.onmouseenter = () => tooltip.style.display = "block";
                    icon.onmouseleave = () => tooltip.style.display = "none";
                    tooltip.onmouseenter = () => tooltip.style.display = "block";
                    tooltip.onmouseleave = () => tooltip.style.display = "none";
                }
            } else {
                document.getElementById("authArea").innerHTML = `<a href="/auth/login" class="btn btn-outline-light" style="padding: 6px 12px; border-radius: 6px;">Đăng nhập</a>`;
            }
        } catch (err) {
            console.error("Failed to load user status", err);
        }
    }

    function confirmLogout() {
        if (confirm("Bạn có chắc chắn muốn thoát không?")) {
            logout();
        }
    }

    async function logout() {
        await fetch('/auth/logout', { method: 'POST' });
        location.reload();
    }

// static/js/history.js
async function loadHistory() {
    const spinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('historyContainer');
    spinner.style.display = 'block';
    container.innerHTML = '';

    try {
        console.log('Fetching /history/api...');
        const response = await fetch('/history/api');
        console.log('Response status:', response.status);

        if (response.status === 401) {
            spinner.style.display = 'none';
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-lock"></i>
                    <p class="text-secondary">Vui lòng <a href="/auth/login">đăng nhập</a> để xem lịch sử quét.</p>
                </div>
            `;
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Data received:', data);

        spinner.style.display = 'none';
        if (data.error) {
            container.innerHTML = `<div class="alert alert-danger">Lỗi: ${data.error}</div>`;
            return;
        }

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-inbox"></i>
                    <p class="text-secondary">Chưa có lịch sử quét</p>
                </div>
            `;
            return;
        }

        displayHistory(data);
    } catch (err) {
        console.error('Error loading history:', err);
        spinner.style.display = 'none';
        container.innerHTML = `<div class="alert alert-danger">Lỗi kết nối server: ${err.message}</div>`;
    }
}

// Các hàm còn lại giữ nguyên như trước (displayHistory, getStatusClass, formatStatus, escapeHtml, attachFilterListeners)

function attachFilterListeners() {
    const filterType = document.getElementById('filterType');
    const filterStatus = document.getElementById('filterStatus');
    if (filterType && filterStatus) {
        const refresh = () => {
            if (window.allHistoryData && window.allHistoryData.length > 0) {
                displayHistory(window.allHistoryData);
            } else {
                loadHistory();
            }
        };
        filterType.addEventListener('change', refresh);
        filterStatus.addEventListener('change', refresh);
    }
}

// Lưu allHistoryData để filter
window.allHistoryData = [];

function displayHistory(historyData) {
    window.allHistoryData = historyData;
    const filterType = document.getElementById('filterType').value;
    const filterStatus = document.getElementById('filterStatus').value;

    let filteredData = historyData;
    if (filterType) {
        filteredData = filteredData.filter(item => item.scan_type === filterType);
    }
    if (filterStatus) {
        filteredData = filteredData.filter(item => item.result_status === filterStatus);
    }

    const container = document.getElementById('historyContainer');
    if (filteredData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-search"></i>
                <p class="text-secondary">Không tìm thấy kết quả</p>
            </div>
        `;
        return;
    }

    let html = '';
    filteredData.forEach(item => {
        const statusClass = getStatusClass(item.result_status);
        const typeIcon = item.scan_type === 'url' ? '🔗' : '📁';
        const dateTime = new Date(item.created_at).toLocaleString('vi-VN');

        html += `
            <div class="history-item">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1">
                        <div class="mb-2">
                            <span class="type-badge">${typeIcon} ${item.scan_type === 'url' ? 'URL' : 'File'}</span>
                            <span class="status-badge ${statusClass} ms-2">${formatStatus(item.result_status)}</span>
                        </div>
                        <div style="word-break: break-all; margin-top: 8px;">
                            <strong>${escapeHtml(item.target)}</strong>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="time-text">${dateTime}</div>
                        <small class="text-warning" style="font-size: 0.8rem;">Điểm rủi ro: ${item.risk_score}/96</small>
                    </div>
                </div>
                ${item.advice ? `
                    <details class="mt-2" style="cursor: pointer;">
                        <summary class="text-info" style="font-size: 0.9rem;">📋 Chi tiết</summary>
                        <div class="detail-section mt-2">${escapeHtml(item.advice).replace(/\n/g, '<br>')}</div>
                    </details>
                ` : ''}
            </div>
        `;
    });

    container.innerHTML = html;
}

// Hàm formatStatus, getStatusClass, escapeHtml giữ nguyên

// Khởi tạo
loadHistory();
attachFilterListeners();

    function getStatusClass(status) {
        if (status === 'DOC_HAI') return 'DOC_HAI';
        if (status === 'CANH_BAO') return 'CANH_BAO';
        if (status === 'AN_TOAN') return 'AN_TOAN';
        return 'KHONG_XAC_DINH';
    }

    function formatStatus(status) {
        if (status === 'DOC_HAI') return '🔴 ĐỘC HẠI';
        if (status === 'CANH_BAO') return '🟡 CẢNH BÁO';
        if (status === 'AN_TOAN') return '🟢 AN TOÀN';
        return '⚪ CHƯA XÁC ĐỊNH';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Re-filter when filter changes
    function attachFilterListeners() {
        const refresh = () => {
            if (allHistoryData.length > 0) {
                displayHistory(allHistoryData);
            } else {
                loadHistory(); // fallback
            }
        };
        document.getElementById('filterType').addEventListener('change', refresh);
        document.getElementById('filterStatus').addEventListener('change', refresh);
    }

    // Initialize
    loadUser().then(() => {
        if (currentUser) {
            loadHistory();
            attachFilterListeners();
        }
    });

    sb.auth.onAuthStateChange(() => {
        loadUser();
    });