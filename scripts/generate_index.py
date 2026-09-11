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
    body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ text-align: center; margin-bottom: 30px; color: #333; }}
    .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    .comic-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.3s; }}
    .comic-card:hover {{ transform: translateY(-5px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .comic-card a {{ text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }}
    .comic-image {{ width: 100%; aspect-ratio: 2/3; background: #e0e0e0; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    .comic-image img {{ width: 100%; height: 100%; object-fit: cover; }}
    .comic-image .placeholder {{ font-size: 48px; }}
    .comic-title {{ padding: 15px; font-weight: bold; text-align: center; flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 TG@BGG_Comics</h1>
        <div class="gallery">
"""
    
    for comic in comics:
        if comic['image']:
            img_html = f'<img src="{comic["image"]}" alt="{comic["title"]}">'
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
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 生成完成: {output_file} ({len(comics)} 个文件)")

if __name__ == "__main__":
    generate_index()
