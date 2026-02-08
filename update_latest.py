import os
import re
import json

def get_summary_from_md(date_str):
    md_path = f"{date_str}.md"
    if not os.path.exists(md_path):
        return ["暂无摘要信息"]
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 提取前三个摘要作为精选
    summaries = re.findall(r'\*\*摘要\*\*：(.*?)(?=\n|$)', content)
    if not summaries:
        # 兼容旧格式或不同符号
        summaries = re.findall(r'\*\*摘要\*\*:(.*?)(?=\n|$)', content)
    
    if summaries:
        # 只取前三个，并限制字数
        selected = []
        for s in summaries[:3]:
            s = s.strip()
            if len(s) > 80:
                s = s[:77] + "..."
            selected.append(s)
        return selected
    return ["暂无摘要信息"]

def update_latest():
    content_dir = 'content'
    all_indices = []

    # 递归查找 content 目录下所有的 index.html
    for root, dirs, files in os.walk(content_dir):
        if 'index.html' in files:
            # 获取相对路径，例如 content/2026/01/24/index.html
            rel_path = os.path.relpath(os.path.join(root, 'index.html'))
            all_indices.append(rel_path)

    if not all_indices:
        print("No index.html files found in content/ directory.")
        return

    # 按路径排序（路径本身包含 YYYY/MM/DD 结构，所以字母序即为日期序）
    all_indices.sort(reverse=True) # 最新的在前
    
    entries = []
    for path in all_indices:
        date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', path)
        if date_match:
            date_str = "-".join(date_match.groups())
            url = '/' + path.replace('\\', '/')
            summary = get_summary_from_md(date_str)
            entries.append({"date": date_str, "url": url, "summaries": summary})

    if not entries:
        print("No entries found.")
        return

    latest_entry = entries[0]
    past_entries = entries[1:]
    print(f"Detected {len(entries)} entries. Latest: {latest_entry['date']}")

    # 生成通用的 Auth 模态框和脚本引用
    def get_auth_assets(base_path="./"):
        return f'''
    <!-- Image Fallback Script -->
    <script>
        function handleImageError(img) {{
            console.warn('Image failed to load:', img.src);
            const fallbackUrls = [
                'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1622790698141-94e30457ef12?auto=format&fit=crop&w=800&q=80'
            ];
            if (img.dataset.triedFallback) {{
                img.src = 'https://via.placeholder.com/800x450/1a1a1a/ffffff?text=Image+Unavailable';
                return;
            }}
            img.dataset.triedFallback = 'true';
            img.src = fallbackUrls[Math.floor(Math.random() * fallbackUrls.length)];
        }}
    </script>
    <!-- Supabase SDK -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script src="{base_path}js/config.js"></script>
    <script src="{base_path}js/auth.js"></script>

    <!-- Auth Modal -->
    <div id="authModal" class="hidden fixed inset-0 z-[100] items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="w-full max-w-md bento-card p-8 relative overflow-hidden">
            <button onclick="toggleAuthModal()" class="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>
            <div class="text-center mb-8">
                <div class="w-16 h-16 bg-orange-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <i class="fa-solid fa-shield-halved text-orange-500 text-3xl"></i>
                </div>
                <h2 id="authTitle" class="text-2xl font-black tracking-tight">登录</h2>
                <p class="text-gray-500 text-sm mt-2">加入 Crypto Insights，解锁更多深度内容</p>
            </div>
            <form onsubmit="handleAuthSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">邮箱地址</label>
                    <input id="authEmail" type="email" required placeholder="name@example.com" class="w-full bg-black/20 dark:bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:border-orange-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">密码</label>
                    <input id="authPassword" type="password" required placeholder="••••••••" class="w-full bg-black/20 dark:bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:border-orange-500 outline-none transition-colors">
                </div>
                <button id="authSubmitBtn" type="submit" class="w-full bg-orange-500 hover:bg-orange-600 text-black font-bold py-3 rounded-xl transition-all active:scale-95">立即登录</button>
            </form>
            <div class="mt-6 text-center">
                <button id="authToggleText" onclick="toggleAuthMode()" class="text-xs text-gray-500 hover:text-orange-500 transition-colors">没有账号？去注册</button>
            </div>
        </div>
    </div>
    '''

    # 更新所有页面的内容（添加 onerror 到所有图片）
    def inject_image_handlers(content):
        # 为没有 onerror 的 img 标签添加 onerror 处理器
        content = re.sub(r'<img\s+(?![^>]*onerror=)([^>]+)>', r'<img \1 onerror="handleImageError(this)">', content)
        return content

    # 生成导航栏 HTML (用于 Portal 和所有页面)
    def generate_nav_html(current_date=None, is_portal=False):
        portal_link_class = "flex items-center gap-3 text-sm font-semibold text-orange-500 bg-orange-500/10 p-2 rounded-xl" if is_portal else "flex items-center gap-3 text-sm text-gray-400 p-2 hover:text-orange-500 dark:hover:text-white transition-colors"
        
        # 日期条目 (最近 8 天)
        display_entries = entries[:8]
        recent_items = []
        for entry in display_entries:
            active_class = "flex items-center gap-3 text-sm font-semibold text-orange-500 bg-orange-500/10 p-2 rounded-xl" if current_date == entry['date'] else "flex items-center gap-3 text-sm text-gray-400 p-2 hover:text-orange-500 dark:hover:text-white transition-colors"
            recent_items.append(f'''
                <a href="{entry['url']}" class="{active_class}">
                    <i class="fa-solid fa-calendar-day"></i> {entry['date'].replace('-', '.')}
                </a>
            ''')
        
        # 将最近 8 天做成折叠结构 (2层)
        # 如果当前日期在最近 8 天内，默认展开
        is_recent_active = any(e['date'] == current_date for e in display_entries)
        recent_section = f'''
            <details class="group/recent" {"open" if is_recent_active else ""}>
                <summary class="flex items-center justify-between text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 cursor-pointer hover:text-orange-500 transition-colors list-none">
                    <span class="flex items-center gap-2">
                        <i class="fa-solid fa-clock-rotate-left"></i> Recent Updates
                    </span>
                    <i class="fa-solid fa-chevron-right text-[10px] transition-transform group-open/recent:rotate-90"></i>
                </summary>
                <div class="space-y-1 mb-4">
                    {" ".join(recent_items)}
                </div>
            </details>
        '''
        
        # 基础导航项 (Portal)
        portal_item = f'''
            <a href="/" class="{portal_link_class}">
                <i class="fa-solid fa-house"></i> Portal
            </a>
        '''

        # History 区域 (8天以前的所有条目)
        # ... (此处逻辑保持不变)
        
        # History 区域 (8天以前的所有条目)
        history_section = ""
        if len(entries) > 8:
            import datetime
            history_entries = entries[8:]
            history_data = {}
            for entry in history_entries: 
                date_obj = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
                y = str(date_obj.year)
                m = str(date_obj.month).zfill(2)
                # 获取该日期属于当月的第几周
                first_day = date_obj.replace(day=1)
                dom = date_obj.day
                adjusted_dom = dom + first_day.weekday()
                week_num = int((adjusted_dom - 1) / 7) + 1
                w = f"第{week_num}周"
                
                if y not in history_data: history_data[y] = {}
                if m not in history_data[y]: history_data[y][m] = {}
                if w not in history_data[y][m]: history_data[y][m][w] = []
                history_data[y][m][w].append(entry)
            
            # 对年份、月份、周进行倒序排序
            sorted_years = sorted(history_data.keys(), reverse=True)
            years_html = []
            for year in sorted_years:
                months = history_data[year]
                sorted_months = sorted(months.keys(), reverse=True)
                months_html = []
                for month in sorted_months:
                    weeks = months[month]
                    sorted_weeks = sorted(weeks.keys(), reverse=True)
                    weeks_html = []
                    for week in sorted_weeks:
                        days = weeks[week]
                        days_html = []
                        for day_entry in days:
                            days_html.append(f'''
                                <a href="{day_entry['url']}" class="block text-[11px] text-gray-500 hover:text-orange-500 py-1 border-l border-white/5 pl-3 -ml-[1px]">
                                    {day_entry['date']}
                                </a>
                            ''')
                        weeks_html.append(f'''
                            <details class="group/week ml-2">
                                <summary class="flex items-center justify-between text-[11px] text-gray-500 p-1 cursor-pointer hover:text-orange-500 dark:hover:text-white list-none">
                                    <span>{week}</span>
                                    <i class="fa-solid fa-chevron-right text-[7px] transition-transform group-open/week:rotate-90"></i>
                                </summary>
                                <div class="pl-2 mt-1 space-y-1">{" ".join(days_html)}</div>
                            </details>
                        ''')
                    months_html.append(f'''<details class="group/month ml-2"><summary class="flex items-center justify-between text-[12px] text-gray-400 p-1 cursor-pointer hover:text-orange-500 dark:hover:text-white list-none"><span>{month}月</span><i class="fa-solid fa-chevron-right text-[8px] transition-transform group-open/month:rotate-90"></i></summary><div class="pl-2 mt-1 space-y-1">{" ".join(weeks_html)}</div></details>''')
                years_html.append(f'''<details class="group/year"><summary class="flex items-center justify-between text-sm text-gray-300 p-2 cursor-pointer hover:text-orange-500 dark:hover:text-white list-none"><span class="flex items-center gap-2"><i class="fa-solid fa-folder text-xs text-orange-500/50"></i> {year}年</span><i class="fa-solid fa-chevron-right text-[10px] transition-transform group-open/year:rotate-90"></i></summary><div class="pl-2 mt-1 space-y-1">{" ".join(months_html)}</div></details>''')
            
            history_section = f'''
            <div class="mt-8 pt-6 border-t border-white/5">
                <p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">History Archive</p>
                <div class="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar space-y-1">
                    {" ".join(years_html)}
                </div>
            </div>'''
        
        # 用户 Auth UI (登录按钮和用户信息)
        auth_ui = f'''
        <div class="mt-6 pt-6 border-t border-white/5">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Account</p>
            <div id="authBtnContainer">
                <button onclick="toggleAuthModal()" class="w-full flex items-center gap-3 text-sm text-gray-400 p-2 hover:text-orange-500 dark:hover:text-white transition-colors">
                    <i class="fa-solid fa-user-plus"></i> 登录 / 注册
                </button>
            </div>
            <div id="userProfileContainer" class="hidden space-y-3">
                <div class="flex items-center gap-3 p-2 rounded-xl bg-orange-500/5 border border-orange-500/10">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-red-500 flex items-center justify-center text-[10px] text-white font-bold">VIP</div>
                    <div class="overflow-hidden">
                        <p id="userEmailDisplay" class="text-[10px] font-medium truncate text-gray-400"></p>
                    </div>
                </div>
                <button onclick="handleSignOut()" class="w-full flex items-center gap-3 text-sm text-red-500/70 p-2 hover:text-red-500 transition-colors">
                    <i class="fa-solid fa-right-from-bracket"></i> 注销退出
                </button>
            </div>
        </div>
        '''

        return f'''
        <div class="space-y-2">
            <div class="mb-6">
                <p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Navigation</p>
                <div class="space-y-1">
                    {portal_item}
                </div>
            </div>
            {recent_section}
            {history_section}
            {auth_ui}
        </div>
        '''

    # 生成侧边栏 HTML
    def generate_sidebar_html(current_date=None):
        return f'''<!-- Sidebar -->
    <aside class="hidden lg:flex flex-col w-64 p-6 sidebar sticky top-0 h-screen">
        <a href="/" class="flex items-center gap-3 mb-10 hover:opacity-80 transition-opacity">
            <div class="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <i class="fa-solid fa-bolt text-black"></i>
            </div>
            <span class="font-extrabold text-xl tracking-tighter">INSIGHT</span>
        </a>
        <nav class="space-y-6">
            {generate_nav_html(current_date)}
        </nav>
        <div class="mt-auto pt-6 border-t border-white/5">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500"></div>
                <div>
                    <p class="text-sm font-bold">Analyst</p>
                    <p class="text-xs text-gray-500">@Derik LU</p>
                </div>
            </div>
        </div>
    </aside>'''

    # 生成摘要 HTML
    latest_summaries_html = "".join([f'<li class="flex items-start gap-2 mb-2"><i class="fa-solid fa-circle-dot text-[8px] mt-2 text-orange-500/60"></i><span>{s}</span></li>' for s in latest_entry['summaries']])

    # 生成 Archive Grid (仅显示最近 9 天)
    archive_entries = past_entries[:8] # 1个最新的 + 8个历史 = 9个
    archive_grid_html = " ".join([f'''
                <a href="{item['url']}" class="glass-card p-6 rounded-2xl group flex flex-col h-full">
                    <div class="flex justify-between items-start mb-4">
                        <span class="text-gray-500 dark:text-gray-400 font-mono text-sm">{item['date']}</span>
                        <i class="fa-solid fa-calendar-day text-gray-700 dark:text-gray-600 group-hover:text-orange-500/50 transition-colors"></i>
                    </div>
                    <h4 class="font-bold mb-4 group-hover:text-orange-500 transition-colors">市场日报</h4>
                    <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-3 mb-6 flex-1">
                        {item['summaries'][0] if item['summaries'] else '查看当日详细市场报告...'}
                    </p>
                    <div class="text-xs text-orange-500 font-bold flex items-center gap-1 mt-auto">
                        查看详情 <i class="fa-solid fa-chevron-right text-[10px]"></i>
                    </div>
                </a>
                ''' for item in archive_entries]) if archive_entries else '<p class="text-gray-600 dark:text-gray-500 col-span-full italic">暂无更多历史记录</p>'

    # 生成 Portal HTML
    portal_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Insights Portal | 加密货币深度观察</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
        }}
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ transition: background-color 0.3s, color 0.3s; }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }}
        .dark .glass-card {{
            background: rgba(255, 255, 255, 0.03);
            border-color: rgba(255, 255, 255, 0.05);
        }}
        .light .glass-card {{
            background: rgba(255, 255, 255, 0.8);
            border-color: rgba(0, 0, 0, 0.05);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .glass-card:hover {{
            transform: translateY(-5px);
        }}
        .dark .glass-card:hover {{
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 153, 0, 0.3);
        }}
        .light .glass-card:hover {{
            background: rgba(255, 255, 255, 0.95);
            border-color: rgba(255, 153, 0, 0.3);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        .orange-glow {{
            box-shadow: 0 0 20px rgba(255, 153, 0, 0.1);
        }}
        .light {{ background-color: #f9fafb; color: #111827; }}
        .dark {{ background-color: #080808; color: #e5e7eb; }}

        /* Custom Scrollbar */
        .custom-scrollbar::-webkit-scrollbar {{
            width: 4px;
        }}
        .custom-scrollbar::-webkit-scrollbar-track {{
            background: transparent;
        }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{
            background: rgba(255, 153, 0, 0.2);
            border-radius: 10px;
        }}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 153, 0, 0.4);
        }}
    </style>
    <script>
        function toggleTheme() {{
            const html = document.documentElement;
            if (html.classList.contains('dark')) {{
                html.classList.remove('dark');
                html.classList.add('light');
                localStorage.setItem('theme', 'light');
            }} else {{
                html.classList.remove('light');
                html.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }}
        }}

        // Initialize theme
        (function() {{
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.classList.add(savedTheme);
        }})();
    </script>
</head>
<body class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
        <!-- Theme Toggle -->
        <div class="flex justify-end mb-8">
            <button onclick="toggleTheme()" class="p-3 rounded-xl glass-card text-orange-500 hover:scale-110 active:scale-95 transition-all">
                <i class="fa-solid fa-circle-half-stroke text-xl"></i>
            </button>
        </div>
        <!-- Header -->
        <header class="text-center mb-16">
            <a href="/" class="inline-block hover:opacity-80 transition-opacity">
                <div class="p-3 rounded-2xl bg-orange-500/10 mb-4 inline-block">
                    <i class="fa-solid fa-chart-line text-orange-500 text-3xl"></i>
                </div>
                <h1 class="text-4xl font-black tracking-tight mb-2">Crypto <span class="text-orange-500">Insights</span> Portal</h1>
            </a>
            <p class="text-gray-500 dark:text-gray-400">每日加密货币市场深度分析与宏观动态追踪</p>
        </header>

        <!-- Featured Latest -->
        <section class="mb-16">
            <h2 class="text-sm font-bold text-orange-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                <span class="w-8 h-[1px] bg-orange-500/30"></span>
                最新发布
            </h2>
            <a href="{latest_entry['url']}" class="block group">
                <div class="glass-card orange-glow p-8 rounded-3xl flex flex-col md:flex-row justify-between items-start gap-8">
                    <div class="flex-1">
                        <div class="flex items-center gap-3 mb-4">
                            <span class="px-3 py-1 bg-orange-500/20 text-orange-500 text-xs font-bold rounded-full">LATEST UPDATE</span>
                            <span class="text-gray-500 dark:text-gray-400 text-sm font-mono">{latest_entry['date']}</span>
                        </div>
                        <h3 class="text-3xl font-bold mb-4 group-hover:text-orange-500 transition-colors">加密货币市场日报 - {latest_entry['date']}</h3>
                        
                        <div class="bg-black/20 dark:bg-white/5 rounded-2xl p-6 mb-6 border border-white/5">
                            <p class="text-xs font-bold text-orange-500/80 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <i class="fa-solid fa-bolt-lightning"></i> 核心动态预览
                            </p>
                            <ul class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed space-y-2">
                                {latest_summaries_html}
                            </ul>
                        </div>

                        <div class="flex items-center text-orange-500 font-bold gap-2">
                            立即阅读全文 <i class="fa-solid fa-arrow-right transition-transform group-hover:translate-x-2"></i>
                        </div>
                    </div>
                    <div class="w-full md:w-64 h-64 bg-orange-500/5 rounded-2xl border border-orange-500/10 flex items-center justify-center overflow-hidden shrink-0">
                         <i class="fa-solid fa-newspaper text-8xl text-orange-500/20"></i>
                    </div>
                </div>
            </a>
        </section>

        <!-- Archive Grid -->
        <section>
            <h2 class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                <span class="w-8 h-[1px] bg-gray-500/30"></span>
                历史存档 (最近 8 天)
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {archive_grid_html}
            </div>
        </section>

        <!-- Footer -->
        <footer class="mt-24 pt-8 border-t border-white/5 dark:border-white/5 text-center text-gray-600 dark:text-gray-500 text-sm">
            <p>&copy; 2026 Crypto Insights. All rights reserved.</p>
        </footer>
    </div>
    {get_auth_assets()}
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(portal_html)
    print("Generated Portal index.html at root")

    # 更新所有页面的 Sidebar 和 Auth Assets
    for entry in entries:
        file_path = entry['url'].lstrip('/')
        abs_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                page_content = f.read()
            
            # 1. 注入图片处理逻辑
            page_content = inject_image_handlers(page_content)
            
            # 2. 更新整个 Sidebar
            sidebar_pattern = r'<!-- Sidebar -->\s*<aside.*?>.*?</aside>'
            new_sidebar = generate_sidebar_html(entry["date"])
            
            if re.search(sidebar_pattern, page_content, flags=re.DOTALL):
                page_content = re.sub(sidebar_pattern, new_sidebar, page_content, flags=re.DOTALL)
            else:
                # 备用方案：如果没找到注释，尝试匹配 <aside>
                page_content = re.sub(r'<aside.*?>.*?</aside>', new_sidebar, page_content, flags=re.DOTALL)

            # 3. 注入 Auth Assets (如果尚未存在)
            if 'id="authModal"' not in page_content:
                # 计算相对路径深度以正确引用 js/
                depth = file_path.count('/')
                base_path = "../" * depth
                auth_assets = get_auth_assets(base_path)
                # 在 </body> 前插入
                page_content = page_content.replace('</body>', f'{auth_assets}\n</body>')
            else:
                # 如果已存在，也要确保图片处理脚本在里面
                if 'function handleImageError' not in page_content:
                    depth = file_path.count('/')
                    base_path = "../" * depth
                    # 插入到 <head> 结束前
                    page_content = page_content.replace('</head>', f'<script>function handleImageError(img) {{ /* fallback logic */ img.src="https://via.placeholder.com/800x450?text=Error"; }}</script>\n</head>')
            
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            print(f"Updated sidebar and auth for {entry['date']}")

    # Update vercel.json
    vercel_config = {
        "cleanUrls": True,
        "rewrites": [
            { "source": "/", "destination": "/index.html" },
            { "source": "/latest", "destination": f"/content/{latest_entry['date'].replace('-', '/')}/index.html" }
        ]
    }
    with open('vercel.json', 'w', encoding='utf-8') as f:
        json.dump(vercel_config, f, indent=4)
    print("Updated vercel.json")

if __name__ == "__main__":
    update_latest()
