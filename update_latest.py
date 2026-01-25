import os
import re
import json

def get_summary_from_md(date_str):
    md_path = f"{date_str}.md"
    if not os.path.exists(md_path):
        return "暂无摘要信息"
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 提取前三个摘要作为精选
    summaries = re.findall(r'\* \*\*摘要\*\*：(.*?)(?=\n|$)', content)
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

    if entries:
        latest_entry = entries[0]
        past_entries = entries[1:]

        print(f"Detected {len(entries)} entries. Latest: {latest_entry['date']}")

        # 生成摘要 HTML
        latest_summaries_html = "".join([f'<li class="flex items-start gap-2 mb-2"><i class="fa-solid fa-circle-dot text-[8px] mt-2 text-orange-500/60"></i><span>{s}</span></li>' for s in latest_entry['summaries']])

        # 生成导航栏 HTML (用于 Portal 和所有页面)
        def generate_nav_html(current_date=None, is_portal=False):
            portal_link_class = "flex items-center gap-3 text-sm font-semibold text-orange-500 bg-orange-500/10 p-2 rounded-xl" if is_portal else "flex items-center gap-3 text-sm text-gray-400 p-2 hover:text-white transition-colors"
            
            nav_items = [f'''
                <a href="/" class="{portal_link_class}">
                    <i class="fa-solid fa-house"></i> Portal
                </a>
            ''']
            
            # 日期条目
            display_entries = entries[:8]
            for entry in display_entries:
                active_class = "flex items-center gap-3 text-sm font-semibold text-orange-500 bg-orange-500/10 p-2 rounded-xl" if current_date == entry['date'] else "flex items-center gap-3 text-sm text-gray-400 p-2 hover:text-white transition-colors"
                nav_items.append(f'''
                    <a href="{entry['url']}" class="{active_class}">
                        <i class="fa-solid fa-calendar-day"></i> {entry['date'].replace('-', '.')}
                    </a>
                ''')
            
            # History 区域 (如果多于8个条目)
            history_section = ""
            if len(entries) > 8:
                # 按照年、月、周、日层级
                history_data = {}
                for entry in entries[8:]: # 剩下的条目进入 History
                    y, m, d = entry['date'].split('-')
                    if y not in history_data: history_data[y] = {}
                    if m not in history_data[y]: history_data[y][m] = []
                    history_data[y][m].append(entry)
                
                years_html = []
                for year, months in history_data.items():
                    months_html = []
                    for month, days in months.items():
                        days_html = []
                        for day_entry in days:
                            days_html.append(f'''
                                <a href="{day_entry['url']}" class="block text-[11px] text-gray-500 hover:text-orange-500 py-1 border-l border-white/5 pl-3 -ml-[1px]">
                                    {day_entry['date']}
                                </a>
                            ''')
                        
                        months_html.append(f'''
                            <details class="group/month ml-2">
                                <summary class="flex items-center justify-between text-[12px] text-gray-400 p-1 cursor-pointer hover:text-white list-none">
                                    <span>{month}月</span>
                                    <i class="fa-solid fa-chevron-right text-[8px] transition-transform group-open/month:rotate-90"></i>
                                </summary>
                                <div class="pl-2 mt-1 space-y-1">
                                    {" ".join(days_html)}
                                </div>
                            </details>
                        ''')
                    
                    years_html.append(f'''
                        <details class="group/year">
                            <summary class="flex items-center justify-between text-sm text-gray-300 p-2 cursor-pointer hover:text-white list-none">
                                <span class="flex items-center gap-2"><i class="fa-solid fa-folder text-xs text-orange-500/50"></i> {year}年</span>
                                <i class="fa-solid fa-chevron-right text-[10px] transition-transform group-open/year:rotate-90"></i>
                            </summary>
                            <div class="pl-2 mt-1 space-y-1">
                                {" ".join(months_html)}
                            </div>
                        </details>
                    ''')

                history_section = f'''
                <div class="mt-8 pt-6 border-t border-white/5">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">History Archive</p>
                    <div class="space-y-1">
                        {" ".join(years_html)}
                    </div>
                </div>
                '''
            
            return f'''
            <nav class="space-y-2">
                <div>
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Navigation</p>
                    <div class="space-y-1">
                        {" ".join(nav_items)}
                    </div>
                </div>
                {history_section}
            </nav>
            '''

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
                历史存档
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {" ".join([f'''
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
                ''' for item in past_entries]) if past_entries else '<p class="text-gray-600 dark:text-gray-500 col-span-full italic">暂无更多历史记录</p>'}
            </div>
        </section>

        <!-- Footer -->
        <footer class="mt-24 pt-8 border-t border-white/5 dark:border-white/5 text-center text-gray-600 dark:text-gray-500 text-sm">
            <p>&copy; 2026 Crypto Insights. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
"""
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(portal_html)
        print("Generated Portal index.html at root with summaries")

        # 更新所有页面的 Sidebar
        for entry in entries:
            file_path = entry['url'].lstrip('/')
            abs_path = os.path.join(os.getcwd(), file_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    page_content = f.read()
                
                # 1. 更新 Logo 跳转链接
                logo_pattern = r'<div class="flex items-center gap-3 mb-10">.*?</div>'
                new_logo = f'''<a href="/" class="flex items-center gap-3 mb-10 hover:opacity-80 transition-opacity">
            <div class="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <i class="fa-solid fa-bolt text-black"></i>
            </div>
            <span class="font-extrabold text-xl tracking-tighter">INSIGHT</span>
        </a>'''
                page_content = re.sub(logo_pattern, new_logo, page_content, flags=re.DOTALL)
                
                # 2. 更新 Nav 导航逻辑
                nav_pattern = r'<nav class="space-y-6">.*?</nav>'
                new_nav = f'<nav class="space-y-6">{generate_nav_html(entry["date"])}</nav>'
                page_content = re.sub(nav_pattern, new_nav, page_content, flags=re.DOTALL)
                
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(page_content)
                print(f"Updated sidebar for {entry['date']}")

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
    else:
        print("No entries found.")

if __name__ == "__main__":
    update_latest()
