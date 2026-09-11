import os
import html
from datetime import datetime

def generate_index(pages_dir='pages'):
    """生成index.html目录列表"""
    
    if not os.path.exists(pages_dir):
        os.makedirs(pages_dir)
    
    # 获取所有HTML文件
    html_files = []
    if os.path.isdir(pages_dir):
        html_files = [f for f in os.listdir(pages_dir) if f.endswith('.html')]
    
    html_files.sort()
    
    # 获取文件信息
    file_info = []
    for filename in html_files:
        filepath = os.path.join(pages_dir, filename)
        size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        
        # 格式化文件大小
        if size < 1024:
            size_str = f"{size}B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.1f}KB"
        else:
            size_str = f"{size/(1024*1024):.1f}MB"
        
        file_info.append({
            'name': filename,
            'size': size_str,
            'mtime': mod_time,
            'url': f"pages/{filename}"
        })
    
    # 生成HTML
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的静态HTML集合</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 36px;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            font-size: 14px;
        }
        
        .stat {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .content {
            padding: 40px 30px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        
        .empty-state h2 {
            font-size: 20px;
            margin-bottom: 10px;
            color: #666;
        }
        
        .file-list {
            display: grid;
            gap: 12px;
        }
        
        .file-item {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 20px;
            align-items: center;
            padding: 16px 20px;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
        }
        
        .file-item:hover {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-color: #667eea;
            transform: translateX(6px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }
        
        .file-name {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 500;
            color: #667eea;
            min-width: 0;
        }
        
        .file-name span:first-child {
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .file-name span:last-child {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .file-meta {
            display: flex;
            gap: 30px;
            font-size: 13px;
            color: #666;
            text-align: right;
        }
        
        .file-size {
            min-width: 60px;
        }
        
        .file-date {
            min-width: 120px;
        }
        
        .footer {
            padding: 20px 30px;
            border-top: 1px solid #e0e0e0;
            background: #f8f9fa;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .stats {
                flex-direction: column;
                gap: 15px;
            }
            
            .content {
                padding: 20px;
            }
            
            .file-item {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            
            .file-meta {
                flex-direction: column;
                gap: 5px;
                text-align: left;
            }
            
            .file-size,
            .file-date {
                min-width: unset;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 TG@BGG_Comics</h1>
            <p>点击下方任意文件即可查看</p>
            <div class="stats">
                <div class="stat">
                    <span>📄</span>
                    <span>{} 个文件</span>
                </div>
            </div>
        </div>
        
        <div class="content">
'''
    
    if file_info:
        html_content += '            <div class="file-list">\n'
        for info in file_info:
            html_content += f'''                <a href="{info['url']}" class="file-item">
                    <div class="file-name">
                        <span>📄</span>
                        <span title="{html.escape(info['name'])}">{html.escape(info['name'])}</span>
                    </div>
                    <div class="file-meta">
                        <div class="file-size">{info['size']}</div>
                        <div class="file-date">{info['mtime']}</div>
                    </div>
                </a>
'''
        html_content += '            </div>\n'
    else:
        html_content += '''            <div class="empty-state">
                <div class="empty-state-icon">📂</div>
                <h2>还没有HTML文件</h2>
                <p>请在 pages 文件夹中添加 HTML 文件</p>
            </div>
'''
    
    html_content += '''        </div>
        
        <div class="footer">
            🤖 此页面由 GitHub Actions 自动生成 | 最后更新: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''
        </div>
    </div>
</body>
</html>'''
    
    return html_content

if __name__ == '__main__':
    index_html = generate_index('pages')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("✅ index.html 已生成")
