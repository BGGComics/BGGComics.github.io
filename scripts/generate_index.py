import os
import re
from pathlib import Path

class MetadataExtractor:
    def extract_image(self, content):
        """
        从 HTML 提取第一张图片，支持多种格式：
        - JavaScript urls 数组中的 base64
        - JavaScript urls 数组中的 HTTP 链接
        - <img> 标签中的 base64
        - <img> 标签中的 HTTP 链接
        - 相对路径
        """
        
        # 方法1：提取 JavaScript urls = ["..."] 数组中的第一个元素
        # 关键：使用 DOTALL flag 使 . 匹配换行，处理长的 base64 字符串
        urls_match = re.search(
            r'urls\s*=\s*\[\s*["\']([^"\']+)["\']',
            content,
            re.DOTALL
        )
        if urls_match:
            img_src = urls_match.group(1).strip()
            if img_src:
                return img_src
        
        # 方法2：查找第一个 <img src="..."> 标签
        # 支持 src="..."、src='...'、src=...（无引号）
        img_match = re.search(
            r'<img[^>]+src\s*=\s*["\']?([^"\'>\s]+)["\']?',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if img_match:
            return img_match.group(1)
        
        return None
    
    def extract_title(self, content):
        """提取 <title> 标签内容"""
        match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        return match.group(1) if match else "Untitled"

def generate_index():
    pages_dir = "pages"
    output_file = "index.html"
    extractor = MetadataExtractor()
    
    comics = []
    
    # 扫描 pages 目录
    if os.path.exists(pages_dir):
        for filename in sorted(os.listdir(pages_dir)):
            if filename.endswith('.html'):
                file_path = os.path.join(pages_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    title = extractor.extract_title(content)
                    image = extractor.extract_image(content)
                    
                    comics.append({
                        'title': title,
                        'image': image,
                        'file': filename
                    })
                    print(f"✓ {filename} -> {title} {'(image found)' if image else '(no image)'}")
                
                except Exception as e:
                    print(f"✗ {filename} -> Error: {e}")
    
    # 生成 HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TG@BGG_Comics</title>
    <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 15px; }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    h1 {{ text-align: center; margin-bottom: 25px; color: #333; font-size: 28px; }}
    
    /* 移动端（默认） */
    .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 12px; }}
    
    /* 平板 600px+ */
    @media (min-width: 600px) {{
        .gallery {{ grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }}
        body {{ padding: 20px; }}
        h1 {{ font-size: 32px; margin-bottom: 30px; }}
    }}
    
    /* 桌面 1024px+ */
    @media (min-width: 1024px) {{
        .gallery {{ grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }}
        body {{ padding: 25px; }}
        h1 {{ font-size: 36px; margin-bottom: 35px; }}
    }}
    
    .comic-card {{ 
        background: white; 
        border-radius: 8px; 
        overflow: hidden; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
    }}
    .comic-card:hover {{ transform: translateY(-5px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .comic-card:active {{ transform: scale(0.98); }}
    
    .comic-card a {{ text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }}
    .comic-image {{ width: 100%; aspect-ratio: 2/3; background: #e0e0e0; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    .comic-image img {{ width: 100%; height: 100%; object-fit: cover; }}
    .comic-image .placeholder {{ font-size: 36px; }}
    .comic-title {{ padding: 10px; font-weight: bold; text-align: center; flex-grow: 1; display: flex; align-items: center; justify-content: center; font-size: 12px; line-height: 1.3; }}
    
    @media (min-width: 600px) {{
        .comic-title {{ padding: 12px; font-size: 13px; }}
        .comic-image .placeholder {{ font-size: 40px; }}
    }}
    
    @media (min-width: 1024px) {{
        .comic-title {{ padding: 15px; font-size: 14px; }}
        .comic-image .placeholder {{ font-size: 48px; }}
    }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 TG@BGG_Comics</h1>
        <div class="gallery" id="comics-gallery">
"""
    
    for comic in comics:
        if comic['image']:
            img_html = f'<img src="{comic["image"]}" alt="{comic["title"]}" loading="lazy">'
        else:
            img_html = '<div class="placeholder">📄</div>'
        
        html_content += f"""            <div class="comic-card">
                <a href="pages/{comic['file']}">
                    <div class="comic-image">
                        {img_html}
                    </div>
                    <div class="comic-title">{comic['title']}</div>
                </a>
            </div>
"""
    
    html_content += """        </div>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const gallery = document.getElementById('comics-gallery');
        const items = Array.from(gallery.children);
        
        // Fisher-Yates 洗牌算法 - 每次打开/刷新都随机排序
        for (let i = items.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            const temp = items[i];
            items[i] = items[j];
            items[j] = temp;
        }
        
        // 重新排列 DOM
        items.forEach(item => gallery.appendChild(item));
    });
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 生成完成: {output_file} ({len(comics)} 个文件)")

if __name__ == "__main__":
    generate_index()
