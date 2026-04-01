const SUPABASE_URL = "https://ddljfrzszcjtsenlgfqj.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_zgt2WTj2O9YRT40dBSRmLg_Z9-snboj";

const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const GOOGLE_LOGIN_FLAG = "pending_google_oauth";

document.addEventListener("DOMContentLoaded", async () => {
    const path = window.location.pathname;
    const isAuthPage = path === "/auth/login" || path === "/auth/register";

    if (!isAuthPage) return;

    const hasOAuthHint =
        window.location.search.includes("code=") ||
        window.location.hash.includes("access_token") ||
        localStorage.getItem(GOOGLE_LOGIN_FLAG) === "1";

    if (!hasOAuthHint) return;

    await handleGoogleSession();
});

async function loginWithGoogle() {
    try {
        const redirectTo = window.location.pathname === "/auth/register"
            ? `${window.location.origin}/auth/register`
            : `${window.location.origin}/auth/login`;

        localStorage.setItem(GOOGLE_LOGIN_FLAG, "1");

        const { error } = await sb.auth.signInWithOAuth({
            provider: "google",
            options: {
                redirectTo
            }
        });

        if (error) {
            localStorage.removeItem(GOOGLE_LOGIN_FLAG);
            alert("Đăng nhập Google thất bại: " + error.message);
        }
    } catch (err) {
        localStorage.removeItem(GOOGLE_LOGIN_FLAG);
        console.error("Google login error:", err);
        alert("Có lỗi khi đăng nhập Google");
    }
}

async function handleGoogleSession() {
    try {
        const { data, error } = await sb.auth.getSession();

        if (error) {
            console.error("getSession error:", error);
            localStorage.removeItem(GOOGLE_LOGIN_FLAG);
            return;
        }

        const sbSession = data?.session;
        if (!sbSession || !sbSession.user) {
            localStorage.removeItem(GOOGLE_LOGIN_FLAG);
            return;
        }

        const user = sbSession.user;
        const email = user.email || "";
        const fullName =
            user.user_metadata?.full_name ||
            user.user_metadata?.name ||
            "";
        const defaultUsername = email ? email.split("@")[0] : "user";

        const { data: existingProfile, error: selectError } = await sb
            .from("profiles")
            .select("*")
            .eq("id", user.id)
            .maybeSingle();

        if (selectError) {
            console.error("Lỗi kiểm tra profile:", selectError);
            localStorage.removeItem(GOOGLE_LOGIN_FLAG);
            return;
        }

        let finalUsername = defaultUsername;
        let finalRole = "USER";

        if (!existingProfile) {
            const { data: insertedProfile, error: insertError } = await sb
                .from("profiles")
                .insert([{
                    id: user.id,
                    email: email,
                    username: defaultUsername,
                    full_name: fullName,
                    role: "USER",
                    status: "ACTIVE"
                }])
                .select()
                .single();

            if (insertError) {
                console.error("Lỗi tạo profile:", insertError);
                localStorage.removeItem(GOOGLE_LOGIN_FLAG);
                return;
            }

            finalUsername = insertedProfile?.username || defaultUsername;
            finalRole = insertedProfile?.role || "USER";
        } else {
            finalUsername = existingProfile.username || defaultUsername;
            finalRole = existingProfile.role || "USER";
        }

        const syncRes = await fetch("/auth/sync-session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: user.id,
                email: email,
                username: finalUsername,
                role: finalRole
            })
        });

        const syncData = await syncRes.json();

        if (!syncRes.ok) {
            console.error("Sync session failed:", syncData);
            localStorage.removeItem(GOOGLE_LOGIN_FLAG);
            alert(syncData.message || "Không thể đồng bộ phiên đăng nhập");
            return;
        }

        localStorage.removeItem(GOOGLE_LOGIN_FLAG);

        if (window.location.search || window.location.hash) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }

        window.location.href = syncData.redirect || "/";
    } catch (err) {
        console.error("handleGoogleSession error:", err);
        localStorage.removeItem(GOOGLE_LOGIN_FLAG);
        alert("Có lỗi khi xử lý đăng nhập Google");
    }
}

async function login() {
    const email = document.getElementById("email")?.value?.trim();
    const password = document.getElementById("password")?.value?.trim();

    if (!email || !password) {
        alert("Vui lòng nhập email và mật khẩu");
        return;
    }

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Đăng nhập thất bại");
            return;
        }

        window.location.href = data.redirect || "/";
    } catch (err) {
        console.error("Login error:", err);
        alert("Có lỗi khi đăng nhập");
    }
}

async function register() {
    const username = document.getElementById("username")?.value?.trim();
    const email = document.getElementById("email")?.value?.trim();
    const password = document.getElementById("password")?.value?.trim();
    const confirmPassword = document.getElementById("confirmPassword")?.value?.trim();

    if (!username || !email || !password || !confirmPassword) {
        alert("Vui lòng nhập đầy đủ thông tin");
        return;
    }

    if (password !== confirmPassword) {
        alert("Mật khẩu xác nhận không khớp");
        return;
    }

    try {
        const res = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Đăng ký thất bại");
            return;
        }

        alert(data.message || "Đăng ký thành công");
        window.location.href = "/auth/login";
    } catch (err) {
        console.error("Register error:", err);
        alert("Có lỗi khi đăng ký");
    }
}

async function logoutSupabaseSession() {
    try {
        await sb.auth.signOut();
    } catch (err) {
        console.error("Supabase logout error:", err);
    } finally {
        localStorage.removeItem(GOOGLE_LOGIN_FLAG);
        window.location.href = "/auth/logout";
    }
}