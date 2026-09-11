import os
import re
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime

class MetadataExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.heading = None
        self.image_src = None
        self.in_head = False
        self.found_img = False

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        elif tag == 'img' and not self.found_img:
            attrs_dict = dict(attrs)
            src = attrs_dict.get('src', '')
            # 接受任何格式：相对路径、绝对路径、data: URI、http(s)
            if src:
                self.image_src = src
                self.found_img = True

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False

    def handle_data(self, data):
        if not self.title and self.in_head:
            text = data.strip()
            if text:
                self.title = text
        elif not self.heading:
            text = data.strip()
            if text:
                self.heading = text

def convert_image_path(img_src, html_file_path):
    """
    处理三种图片源：
    1. base64/data URI → 直接返回
    2. 绝对路径(/开头) → 直接返回
    3. 外部URL(http) → 直接返回
    4. 相对路径 → 转换为 pages/ 相对路径
    """
    # base64 或外部 URL，直接返回
    if img_src.startswith('data:') or img_src.startswith('http'):
        return img_src
    
    # 绝对路径
    if img_src.startswith('/'):
        return img_src
    
    # 相对路径转换
    html_dir = Path(html_file_path).parent
    relative_to_pages = html_dir.relative_to(Path('pages'))
    full_path = relative_to_pages / img_src
    
    return f"pages/{full_path}".replace('\\', '/')

def generate_index():
    pages_dir = Path('pages')
    comics = []

    for html_file in sorted(pages_dir.rglob('*.html')):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            extractor = MetadataExtractor()
            extractor.feed(content)

            title = extractor.title or extractor.heading or html_file.stem
            image_src = extractor.image_src or ''

            # 转换图片路径
            if image_src:
                image_src = convert_image_path(image_src, html_file)

            # 获取链接
            relative_path = html_file.relative_to(pages_dir)
            link = f"pages/{relative_path}".replace('\\', '/')

            comics.append({
                'title': title,
                'link': link,
                'image': image_src
            })

            # 调试输出
            img_preview = image_src[:50] + '...' if len(image_src) > 50 else image_src
            print(f"✅ {html_file.name} → 标题: {title}, 图片: {img_preview}")

        except Exception as e:
            print(f"❌ 错误处理 {html_file}: {e}")

    # 生成 HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TG@BGG_Comics</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ text-align: center; margin-bottom: 40px; color: #333; font-size: 2.5em; }}
        
        .gallery {{
            display: grid;
            gap: 30px;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        }}

        .card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
        }}

        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
        }}

        .card-image {{
            width: 100%;
            height: 160px;
            object-fit: cover;
            background: #e0e0e0;
        }}

        .card-title {{
            padding: 16px;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-weight: 500;
            font-size: 0.95em;
            line-height: 1.4;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}

        /* 移动设备 */
        @media (max-width: 600px) {{
            .gallery {{ grid-template-columns: 1fr; gap: 20px; }}
            h1 {{ font-size: 1.8em; margin-bottom: 30px; }}
        }}

        /* 平板 */
        @media (min-width: 600px) and (max-width: 1000px) {{
            .gallery {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 TG@BGG_Comics</h1>
        <div class="gallery">
'''

    for comic in comics:
        img_tag = ''
        if comic['image']:
            img_tag = f'<img src="{comic["image"]}" alt="{comic["title"]}" class="card-image" onerror="this.style.display=\'none\'">'
        else:
            img_tag = '<div class="card-image" style="display: flex; align-items: center; justify-content: center; font-size: 3em;">📄</div>'

        html_content += f'''        <a href="{comic['link']}" class="card">
            {img_tag}
            <div class="card-title">{comic['title']}</div>
        </a>
'''

    html_content += '''        </div>
    </div>
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ 索引已生成！共 {len(comics)} 个文件")

if __name__ == '__main__':
    generate_index()
