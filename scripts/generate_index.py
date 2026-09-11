import os
import re
from pathlib import Path
from html.parser import HTMLParser

class MetadataExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.h1 = None
        self.img_src = None
        self.in_title = False
        self.in_h1 = False
        self.found_img = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        elif tag == 'h1' and not self.h1:
            self.in_h1 = True
        elif tag == 'img' and not self.found_img:
            attrs_dict = dict(attrs)
            if 'src' in attrs_dict:
                self.img_src = attrs_dict['src']
                self.found_img = True
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False
    
    def handle_data(self, data):
        if self.in_title and not self.title:
            self.title = data.strip()
        elif self.in_h1 and not self.h1:
            self.h1 = data.strip()

def extract_metadata(html_content):
    """从 HTML 提取标题和第一张图片"""
    extractor = MetadataExtractor()
    try:
        extractor.feed(html_content)
    except:
        pass
    
    title = extractor.title or extractor.h1 or "未命名文件"
    img_src = extractor.img_src
    
    return title, img_src

def generate_index():
    """生成目录页面"""
    pages_dir = Path('pages')
    
    if not pages_dir.exists():
        pages_dir.mkdir(parents=True, exist_ok=True)
    
    # 扫描所有 HTML 文件
    html_files = sorted(pages_dir.glob('*.html'))
    
    works = []
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        title, img_src = extract_metadata(html_content)
        
        # 处理图片路径（转换为相对于根目录的路径）
        if img_src:
            if not img_src.startswith(('http://', 'https://', 'data:')):
                # 如果图片在 pages 文件夹里，构建正确的路径
                if not img_src.startswith('/'):
                    img_src = f"pages/{img_src}"
        
        works.append({
            'filename': html_file.name,
            'title': title,
            'img_src': img_src
        })
    
    # 生成 HTML
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TG@BGG_Comics</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 50px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 30px;
            margin-bottom: 50px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .card-image {
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            flex-shrink: 0;
        }
        
        .card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .card-content {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .card-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.4;
            word-break: break-word;
        }
        
        .card-link {
            color: #667eea;
            font-size: 0.95em;
            font-weight: 500;
            margin-top: auto;
        }
        
        .empty {
            text-align: center;
            color: white;
            font-size: 1.2em;
        }
        
        .empty p {
            margin-top: 20px;
        }
        
        footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.95em;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨TG@BGG_Comics</h1>
"""
    
    if works:
        html_content += '        <div class="gallery">\n'
        
        for work in works:
            html_content += f'''            <a href="pages/{work['filename']}" class="card">
                <div class="card-image">
'''
            
            if work['img_src']:
                html_content += f'                    <img src="{work["img_src"]}" alt="{work["title"]}">\n'
            else:
                html_content += '                    <div style="width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center;"><span style="color: white; font-size: 3em;">📄</span></div>\n'
            
            html_content += f'''                </div>
                <div class="card-content">
                    <div class="card-title">{work['title']}</div>
                    <div class="card-link">点击查看 →</div>
                </div>
            </a>
'''
        
        html_content += '        </div>\n'
    else:
        html_content += '''        <div class="empty">
            <p>暂无文件</p>
        </div>
'''
    
    html_content += '''        <footer>
            <p>TG@BGG_Comics</p>
        </footer>
    </div>
</body>
</html>
"""'

    # 写入 index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 已生成 index.html，包含 {len(works)} 个文件")

if __name__ == '__main__':
    generate_index()
