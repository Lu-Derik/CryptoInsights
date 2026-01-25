// Auth 逻辑实现
let supabase;

// 将所有函数暴露到全局作用域
window.toggleAuthModal = function() {
    const modal = document.getElementById('authModal');
    if (!modal) return;
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
};

window.toggleAuthMode = function() {
    const title = document.getElementById('authTitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const toggleText = document.getElementById('authToggleText');
    if (!title || !submitBtn || !toggleText) return;
    
    const isLogin = title.innerText === '登录';

    title.innerText = isLogin ? '注册' : '登录';
    submitBtn.innerText = isLogin ? '立即注册' : '立即登录';
    toggleText.innerText = isLogin ? '已有账号？去登录' : '没有账号？去注册';
};

window.handleAuthSubmit = async function(event) {
    event.preventDefault();
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    const isLogin = document.getElementById('authTitle').innerText === '登录';
    const btn = document.getElementById('authSubmitBtn');

    btn.disabled = true;
    btn.innerText = '处理中...';

    try {
        let result;
        if (isLogin) {
            result = await supabase.auth.signInWithPassword({ email, password });
        } else {
            result = await supabase.auth.signUp({ email, password });
            if (!result.error) alert('注册成功！请查收确认邮件（如果开启了邮件验证）。');
        }

        if (result.error) throw result.error;
        if (isLogin) window.toggleAuthModal();
    } catch (error) {
        alert(error.message || '操作失败，请检查配置或网络');
    } finally {
        btn.disabled = false;
        btn.innerText = isLogin ? '立即登录' : '立即注册';
    }
};

window.handleSignOut = async function() {
    await supabase.auth.signOut();
    location.reload();
};

// 初始化
(function initSupabase() {
    try {
        if (typeof supabasejs !== 'undefined') {
            supabase = supabasejs.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
        } else if (typeof window.supabase !== 'undefined' && window.supabase.createClient) {
            supabase = window.supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
        } else {
            console.error("Supabase SDK not found. Make sure the script is loaded.");
            return;
        }

        // 监听 Auth 状态
        supabase.auth.onAuthStateChange((event, session) => {
            const user = session?.user;
            const authBtnContainer = document.getElementById('authBtnContainer');
            const userProfileContainer = document.getElementById('userProfileContainer');

            if (user) {
                if (authBtnContainer) authBtnContainer.classList.add('hidden');
                if (userProfileContainer) {
                    userProfileContainer.classList.remove('hidden');
                    const display = document.getElementById('userEmailDisplay');
                    if (display) display.innerText = user.email;
                }
            } else {
                if (authBtnContainer) authBtnContainer.classList.remove('hidden');
                if (userProfileContainer) userProfileContainer.classList.add('hidden');
            }
        });
    } catch (e) {
        console.error("Supabase client failed to initialize:", e);
    }
})();
