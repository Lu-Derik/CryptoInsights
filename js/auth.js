// Auth 逻辑实现
let supabase;

try {
    supabase = supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
} catch (e) {
    console.error("Supabase client failed to initialize. Check config.js.");
}

// 切换模态框
function toggleAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
}

// 切换登录/注册表单
function toggleAuthMode() {
    const title = document.getElementById('authTitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const toggleText = document.getElementById('authToggleText');
    const isLogin = title.innerText === '登录';

    title.innerText = isLogin ? '注册' : '登录';
    submitBtn.innerText = isLogin ? '立即注册' : '立即登录';
    toggleText.innerText = isLogin ? '已有账号？去登录' : '没有账号？去注册';
}

// 处理表单提交
async function handleAuthSubmit(event) {
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
        if (isLogin) toggleAuthModal();
    } catch (error) {
        alert(error.message || '操作失败，请检查配置或网络');
    } finally {
        btn.disabled = false;
        btn.innerText = isLogin ? '立即登录' : '立即注册';
    }
}

// 注销
async function handleSignOut() {
    await supabase.auth.signOut();
    location.reload();
}

// 监听 Auth 状态
if (supabase) {
    supabase.auth.onAuthStateChange((event, session) => {
        const user = session?.user;
        const authBtnContainer = document.getElementById('authBtnContainer');
        const userProfileContainer = document.getElementById('userProfileContainer');

        if (user) {
            // 已登录
            if (authBtnContainer) authBtnContainer.classList.add('hidden');
            if (userProfileContainer) {
                userProfileContainer.classList.remove('hidden');
                document.getElementById('userEmailDisplay').innerText = user.email;
            }
        } else {
            // 未登录
            if (authBtnContainer) authBtnContainer.classList.remove('hidden');
            if (userProfileContainer) userProfileContainer.classList.add('hidden');
        }
    });
}
