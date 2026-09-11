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
    
    /* 星空背景 */
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #0a0e27 0%, #1a0f3d 50%, #0a0e27 100%);
        min-height: 100vh;
        padding: 15px;
        position: relative;
        overflow-x: hidden;
    }}
    
    /* 星空效果 - 移动端 */
    @media (min-width: 0px) {{
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, #eee, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 60px 70px, #fff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 50px 50px, #fff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 130px 80px, #fff, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 90px 10px, #fff, rgba(0,0,0,0));
            background-size: 200px 200px;
            background-attachment: fixed;
            pointer-events: none;
            z-index: 0;
            opacity: 0.8;
        }}
    }}
    
    .container {{
        max-width: 1400px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }}
    
    h1 {{
        text-align: center;
        margin-bottom: 15px;
        color: #a78bfa;
        font-size: 24px;
        text-shadow: 0 0 20px rgba(167, 139, 250, 0.5), 0 0 40px rgba(139, 92, 246, 0.3);
        letter-spacing: 2px;
    }}
    
    .subtitle {{
        text-align: center;
        color: #8b5cf6;
        font-size: 12px;
        margin-bottom: 30px;
        opacity: 0.8;
    }}
    
    /* 移动端 */
    .gallery {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 12px;
    }}
    
    /* 平板 600px+ */
    @media (min-width: 600px) {{
        h1 {{ font-size: 32px; margin-bottom: 20px; }}
        .subtitle {{ font-size: 13px; margin-bottom: 35px; }}
        .gallery {{
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }}
        body {{ padding: 20px; }}
    }}
    
    /* 桌面 1024px+ */
    @media (min-width: 1024px) {{
        h1 {{ font-size: 40px; margin-bottom: 25px; }}
        .subtitle {{ font-size: 14px; margin-bottom: 40px; }}
        .gallery {{
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
        }}
        body {{ padding: 30px; }}
    }}
    
    /* 卡片 - 深紫色光晕效果 */
    .comic-card {{
        background: rgba(30, 20, 60, 0.6);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 
            0 0 20px rgba(139, 92, 246, 0.3),
            0 0 40px rgba(88, 44, 131, 0.2),
            inset 0 0 20px rgba(167, 139, 250, 0.1);
        border: 1px solid rgba(167, 139, 250, 0.2);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        cursor: pointer;
        backdrop-filter: blur(10px);
    }}
    
    .comic-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 0 30px rgba(139, 92, 246, 0.6),
            0 0 60px rgba(88, 44, 131, 0.4),
            inset 0 0 30px rgba(167, 139, 250, 0.2);
        border: 1px solid rgba(167, 139, 250, 0.5);
    }}
    
    .comic-card:active {{
        transform: scale(0.96);
    }}
    
    /* 图片容器 */
    .comic-image {{
        width: 100%;
        aspect-ratio: 2/3;
        background: linear-gradient(135deg, rgba(88, 44, 131, 0.2), rgba(139, 92, 246, 0.1));
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
    }}
    
    .comic-image img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
        filter: brightness(0.95);
    }}
    
    .comic-card:hover .comic-image img {{
        transform: scale(1.08);
        filter: brightness(1);
    }}
    
    .comic-image .placeholder {{
        font-size: 36px;
        opacity: 0.5;
    }}
    
    /* 标题 */
    .comic-title {{
        padding: 10px;
        font-weight: 600;
        text-align: center;
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        line-height: 1.3;
        color: #c9b8ff;
        text-shadow: 0 0 10px rgba(167, 139, 250, 0.3);
    }}
    
    .comic-card a {{
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        height: 100%;
    }}
    
    @media (min-width: 600px) {{
        .comic-image .placeholder {{ font-size: 40px; }}
        .comic-title {{ padding: 12px; font-size: 13px; }}
    }}
    
    @media (min-width: 1024px) {{
        .comic-image .placeholder {{ font-size: 48px; }}
        .comic-title {{ padding: 15px; font-size: 14px; }}
    }}
    
    /* 加载动画 */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(15, 10, 30, 0.5);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(to bottom, #8b5cf6, #a78bfa);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(to bottom, #a78bfa, #c4b5fd);
    }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ TG@BGG_Comics ✨</h1>
        <p class="subtitle">沉醉于迷人的色欲世界</p>
        <div class="gallery" id="comics-gallery">
"""
    
    for comic in comics:
        if comic['image']:
            img_html = f'<img src="{comic["image"]}" alt="{comic["title"]}" loading="lazy">'
        else:
            img_html = '<div class="placeholder">📖</div>'
        
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
    // Fisher-Yates 洗牌算法 - 客户端随机排序
    document.addEventListener('DOMContentLoaded', function() {{
        const gallery = document.getElementById('comics-gallery');
        const items = Array.from(gallery.children);
        
        // 随机打乱
        for (let i = items.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            const temp = items[i];
            items[i] = items[j];
            items[j] = temp;
        }}
        
        // 重新排列 DOM
        items.forEach(item => gallery.appendChild(item));
    }});
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ 生成完成: {output_file} ({len(comics)} 个文件)")

if __name__ == "__main__":
    generate_index()
