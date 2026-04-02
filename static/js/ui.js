const SUPABASE_URL = "https://ddljfrzszcjtsenlgfqj.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_zgt2WTj2O9YRT40dBSRmLg_Z9-snboj";

const sbUi = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

document.addEventListener("DOMContentLoaded", async () => {
    await loadUserHeader();

    sbUi.auth.onAuthStateChange(() => {
        loadUserHeader();
    });
});

async function loadUserHeader() {
    const authArea = document.getElementById("authArea");
    if (!authArea) return;

    try {
        const {
            data: { user }
        } = await sbUi.auth.getUser();

        if (!user) {
            authArea.innerHTML = `
                <a href="/auth/login" class="btn btn-outline-light">Đăng nhập</a>
            `;
            return;
        }

        authArea.innerHTML = `
            <div class="d-flex align-items-center gap-3">
                <a href="/history" class="menu-link">
                    <i class="bi bi-clock-history"></i>
                    <span>Lịch sử</span>
                </a>

                <div class="position-relative d-flex align-items-center">
                    <i class="bi bi-person-circle fs-4 text-white"
                        id="userIcon"
                        style="cursor:pointer;">
                    </i>

                    <div id="userTooltip"
                        style="
                            display:none;
                            position:absolute;
                            top:40px;
                            right:0;
                            background:#1e293b;
                            padding:10px 15px;
                            border-radius:8px;
                            box-shadow:0 5px 15px rgba(0,0,0,0.5);
                            white-space:nowrap;
                            z-index:999;
                        ">
                        <div style="font-size:13px;">${user.email}</div>

                        <div id="logoutAction"
                             style="cursor:pointer; font-size:13px; margin-top:6px;">
                             Thoát
                        </div>
                    </div>
                </div>
            </div>
        `;

        bindUserTooltipEvents();
    } catch (err) {
        console.error("Load user header error:", err);
    }
}

function bindUserTooltipEvents() {
    const icon = document.getElementById("userIcon");
    const tooltip = document.getElementById("userTooltip");
    const logoutAction = document.getElementById("logoutAction");

    if (!icon || !tooltip) return;

    icon.addEventListener("mouseenter", () => {
        tooltip.style.display = "block";
    });

    icon.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
    });

    tooltip.addEventListener("mouseenter", () => {
        tooltip.style.display = "block";
    });

    tooltip.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
    });

    if (logoutAction) {
        logoutAction.addEventListener("click", confirmLogout);
    }
}

function confirmLogout() {
    const ok = confirm("Bạn có chắc chắn muốn thoát không?");
    if (ok) {
        logoutUser();
    }
}

async function logoutUser() {
    try {
        await sbUi.auth.signOut();
    } catch (err) {
        console.error("Logout error:", err);
    } finally {
        localStorage.clear();
        window.location.href = "/auth/logout";
    }
}

function showIntroductionModal(event) {
    if (event) event.preventDefault();
    alert("Giới thiệu hệ thống - Hãy xem trang chủ để biết thêm chi tiết");
}