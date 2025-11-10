#!/usr/bin/env python3
"""
字符编码修复脚本
修复lessons.csv中的编码问题
"""

import csv
import re
from pathlib import Path

# 编码修复映射表
ENCODING_FIXES = {
    # 引号修复
    '?': '"',  # 开引号
    '?': '"',  # 闭引号
    '�': '§',  # 章节符号
    '?': "'",  # 撇号

    # 其他常见错误
    '�': '—',  # 破折号
    '�': '…',  # 省略号
}

def fix_text(text):
    """修复文本中的编码错误"""
    if not text:
        return text

    fixed = text
    for wrong, correct in ENCODING_FIXES.items():
        fixed = fixed.replace(wrong, correct)

    return fixed

def analyze_encoding_issues(csv_file):
    """分析CSV文件中的编码问题"""
    issues = {}

    # 先尝试UTF-8，如果失败则使用ISO-8859-1
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(csv_file, 'r', encoding='iso-8859-1') as f:
            content = f.read()

    for wrong_char in ENCODING_FIXES.keys():
        count = content.count(wrong_char)
        if count > 0:
            issues[wrong_char] = count

    return issues

def fix_csv_encoding(input_file, output_file=None):
    """修复CSV文件的编码"""
    if output_file is None:
        output_file = input_file.replace('.csv', '_fixed.csv')

    print(f"📖 读取文件: {input_file}")

    # 分析编码问题
    issues = analyze_encoding_issues(input_file)
    if issues:
        print("\n🔍 发现的编码问题:")
        for char, count in issues.items():
            replacement = ENCODING_FIXES.get(char, '?')
            print(f"  '{char}' → '{replacement}' : {count}次")
    else:
        print("\n✅ 未发现编码问题")
        return

    # 读取并修复
    rows_fixed = 0
    total_fixes = 0

    # 使用ISO-8859-1读取
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='iso-8859-1') as infile:
            reader = csv.reader(infile)
            rows = list(reader)

    fixed_rows = []
    for row in rows:
        fixed_row = [fix_text(cell) for cell in row]
        fixed_rows.append(fixed_row)

        # 统计修复
        if row != fixed_row:
            rows_fixed += 1
            for orig, fixed in zip(row, fixed_row):
                if orig != fixed:
                    total_fixes += sum(orig.count(wrong) for wrong in ENCODING_FIXES.keys())

    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(fixed_rows)

    print(f"\n✅ 修复完成!")
    print(f"  - 修复了 {rows_fixed} 行")
    print(f"  - 总共修复 {total_fixes} 处错误")
    print(f"  - 输出文件: {output_file}")

    return output_file

def create_diff_report(original_file, fixed_file, output_report):
    """创建修复对比报告"""
    # 读取原文件（可能是ISO-8859-1）
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
    except UnicodeDecodeError:
        with open(original_file, 'r', encoding='iso-8859-1') as f:
            original_lines = f.readlines()

    # 读取修复后的文件（应该是UTF-8）
    with open(fixed_file, 'r', encoding='utf-8') as f:
        fixed_lines = f.readlines()

    with open(output_report, 'w', encoding='utf-8') as report:
        report.write("# 字符编码修复报告\n\n")
        report.write(f"原文件: {original_file}\n")
        report.write(f"修复后: {fixed_file}\n\n")

        report.write("## 修复详情\n\n")

        diff_count = 0
        for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines), 1):
            if orig != fixed:
                diff_count += 1
                report.write(f"### 第 {i} 行\n")
                report.write(f"原文: {orig}")
                report.write(f"修复: {fixed}\n\n")

        report.write(f"\n总共修复了 {diff_count} 行\n")

    print(f"📄 对比报告已生成: {output_report}")

if __name__ == '__main__':
    import sys

    input_file = '/home/user/AI-notary/lessons.csv'
    output_file = '/home/user/AI-notary/lessons_fixed.csv'
    report_file = '/home/user/AI-notary/encoding_fix_report.md'

    print("=" * 60)
    print("  字符编码修复工具")
    print("=" * 60)

    # 执行修复
    fixed_file = fix_csv_encoding(input_file, output_file)

    # 生成对比报告
    if fixed_file:
        print("\n📝 生成修复报告...")
        create_diff_report(input_file, fixed_file, report_file)

    print("\n✨ 全部完成!")
    print("\n下一步:")
    print("  1. 检查 lessons_fixed.csv")
    print("  2. 查看 encoding_fix_report.md")
    print("  3. 如果满意，替换原文件: mv lessons_fixed.csv lessons.csv")
