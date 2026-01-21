#!/usr/bin/env python3
"""
PDF 图片提取脚本
从 PDF 文件中提取图片并按规范命名保存
"""

import os
import sys
from pathlib import Path

def extract_images_from_pdf(pdf_path: str, output_dir: str, problem_id: str, image_type: str = "question"):
    """
    从 PDF 中提取图片并按规范命名
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录（通常是 image/）
        problem_id: 题目ID，如 P-2026-01-1.1-014
        image_type: 图片类型，question（题目配图）或 analysis（解析配图）
    
    Returns:
        保存的图片路径
    """
    try:
        from pdf2image import convert_from_path
        from PIL import Image
    except ImportError:
        print("请先安装依赖：pip install pdf2image Pillow")
        sys.exit(1)
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 转换 PDF 为图片
    try:
        pages = convert_from_path(pdf_path, dpi=150)
    except Exception as e:
        print(f"PDF 转换失败: {e}")
        return None
    
    # 生成文件名
    filename = f"{problem_id}-{image_type}.png"
    save_path = output_path / filename
    
    # 保存第一页作为示例（实际使用时需要根据具体位置提取）
    if pages:
        pages[0].save(save_path, "PNG")
        print(f"图片已保存: {save_path}")
        return str(save_path)
    
    return None


def batch_extract_images(pdf_path: str, output_dir: str, year_month: str, chapter: str, start_num: int = 1):
    """
    批量提取 PDF 中的所有图片
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        year_month: 年月，如 2026-01
        chapter: 章节号，如 1.1
        start_num: 起始题目序号
    """
    try:
        import subprocess
        result = subprocess.run(
            ["pdfimages", "-png", pdf_path, f"{output_dir}/temp"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"pdfimages 执行失败: {result.stderr}")
            return []
        
        # 重命名提取的图片
        output_path = Path(output_dir)
        temp_images = sorted(output_path.glob("temp-*.png"))
        
        renamed_images = []
        for i, img_path in enumerate(temp_images):
            problem_num = start_num + (i // 2)  # 假设每道题最多2张图
            img_type = "question" if i % 2 == 0 else "analysis"
            
            new_name = f"P-{year_month}-{chapter}-{problem_num:03d}-{img_type}.png"
            new_path = output_path / new_name
            
            img_path.rename(new_path)
            renamed_images.append(str(new_path))
            print(f"重命名: {img_path.name} -> {new_name}")
        
        return renamed_images
        
    except FileNotFoundError:
        print("pdfimages 未安装，请安装 poppler-utils")
        print("Ubuntu/Debian: sudo apt install poppler-utils")
        print("macOS: brew install poppler")
        return []


def generate_image_reference(problem_id: str, image_type: str, description: str = "") -> str:
    """
    生成 Markdown 格式的图片引用
    
    Args:
        problem_id: 题目ID
        image_type: question 或 analysis
        description: 图片描述
    
    Returns:
        Markdown 图片引用字符串
    """
    filename = f"{problem_id}-{image_type}.png"
    alt_text = description if description else f"{'题目' if image_type == 'question' else '解析'}配图"
    return f"![{alt_text}](image/{filename})"


if __name__ == "__main__":
    # 使用示例
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python extract_images.py <pdf_path> [output_dir] [problem_id]")
        print("")
        print("示例:")
        print("  python extract_images.py problems.pdf ./image P-2026-01-1.1-001")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./image"
    problem_id = sys.argv[3] if len(sys.argv) > 3 else "P-2026-01-1.1-001"
    
    extract_images_from_pdf(pdf_path, output_dir, problem_id)
