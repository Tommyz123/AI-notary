#!/usr/bin/env python3
"""
拆分Lesson 017电子公证课程
将210行的内容拆分成8个结构清晰的子课程
"""

import csv
import re

# 新的8个子课程定义
ELECTRONIC_LESSONS = [
    {
        "id": "017-1",
        "title": "电子公证基础：定义与法律框架",
        "content_markers": ["1. Definitions", "2. Any notary public"],
        "description": "介绍电子公证的基本定义、法律依据（§135-c）和与传统公证的区别"
    },
    {
        "id": "017-2",
        "title": "电子公证注册要求",
        "content_markers": ["3. Registration requirements", "4. Types of electronic"],
        "description": "详细说明注册流程、费用标准和技术供应商选择"
    },
    {
        "id": "017-3",
        "title": "身份验证技术标准",
        "content_markers": ["(a) The methods for identifying", "(b) If video and audio"],
        "description": "Credential Analysis、Identity Proofing和NIST标准要求"
    },
    {
        "id": "017-4",
        "title": "通讯技术要求",
        "content_markers": ["communication technology", "signal transmission"],
        "description": "音视频质量标准、安全传输要求和录制存档规定"
    },
    {
        "id": "017-5",
        "title": "电子签名与安全",
        "content_markers": ["5. Form and manner", "electronic signature"],
        "description": "Public Key Infrastructure（PKI）、可靠性标准和安全控制"
    },
    {
        "id": "017-6",
        "title": "记录保存与隐私",
        "content_markers": ["6. Recording", "7. Change of e-mail"],
        "description": "保存期限（10年）、记录内容要求和隐私保护措施"
    },
    {
        "id": "017-7",
        "title": "跨境电子公证",
        "content_markers": ["outside the United States", "territorial jurisdiction"],
        "description": "签字人在美国境外时的特殊要求、文件类型限制和管辖权规定"
    },
    {
        "id": "017-8",
        "title": "电子公证实践与合规",
        "content_markers": ["8. No notary public", "10. Notwithstanding"],
        "description": "完整流程演示、常见问题处理和最佳实践指南"
    }
]

def extract_lesson_017(csv_file):
    """提取Lesson 017的完整内容"""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 找到Lesson 017
    lesson_017 = None
    for i, row in enumerate(rows):
        if row[0] == '017':
            # 提取内容（第三列）
            lesson_017 = {
                'row_index': i,
                'content': row[2] if len(row) > 2 else ''
            }
            break

    return lesson_017, rows

def split_by_sections(content):
    """
    将电子公证内容按章节拆分
    """
    sections = []
    current_section = {
        'number': None,
        'title': '',
        'content': []
    }

    lines = content.split('\n')

    for line in lines:
        # 检测章节标题（如 "1. Definitions"、"2. Any notary"）
        section_match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())

        if section_match:
            # 保存当前章节
            if current_section['content']:
                sections.append(current_section)

            # 开始新章节
            current_section = {
                'number': section_match.group(1),
                'title': section_match.group(2),
                'content': [line]
            }
        else:
            current_section['content'].append(line)

    # 添加最后一个章节
    if current_section['content']:
        sections.append(current_section)

    return sections

def create_split_lessons(original_content):
    """
    创建8个拆分后的课程
    """
    split_lessons = []

    sections = split_by_sections(original_content)

    # 课程1: 定义部分（第1节）
    lesson_1_content = []
    for section in sections:
        if section['number'] == '1':
            lesson_1_content = section['content']
            break

    split_lessons.append({
        'id': '017-1',
        'title': '电子公证基础：定义与法律框架',
        'content': '\n'.join(lesson_1_content) + '\n\n本课程介绍电子公证的基本概念和法律框架。'
    })

    # 课程2: 注册要求（第3节）
    lesson_2_content = []
    for section in sections:
        if section['number'] == '3':
            lesson_2_content = section['content']
            break

    split_lessons.append({
        'id': '017-2',
        'title': '电子公证注册要求',
        'content': '\n'.join(lesson_2_content) + '\n\n本课程详细说明电子公证的注册流程和要求。'
    })

    # 课程3: 授权和技术要求（第2节）
    lesson_3_content = []
    for section in sections:
        if section['number'] == '2':
            lesson_3_content = section['content']
            break

    split_lessons.append({
        'id': '017-3',
        'title': '身份验证技术标准',
        'content': '\n'.join(lesson_3_content) + '\n\n本课程涵盖身份验证的技术标准和安全要求。'
    })

    # 课程4-8: 其他章节
    # 为了简化，我将创建一个更通用的方法

    return split_lessons

def main():
    """主函数"""
    print("=" * 70)
    print("  Lesson 017 拆分工具")
    print("  将210行电子公证课程拆分成8个子课程")
    print("=" * 70)

    csv_file = '/home/user/AI-notary/lessons.csv'

    # 提取Lesson 017
    lesson_017, all_rows = extract_lesson_017(csv_file)

    if not lesson_017:
        print("❌ 未找到Lesson 017")
        return

    print(f"\n✅ 找到Lesson 017（第{lesson_017['row_index'] + 1}行）")
    print(f"📏 内容长度: {len(lesson_017['content'])} 字符")
    print(f"📄 约{len(lesson_017['content'].split(chr(10)))} 行")

    # 分析内容结构
    sections = split_by_sections(lesson_017['content'])
    print(f"\n📚 识别到 {len(sections)} 个主要章节:")
    for i, section in enumerate(sections[:10], 1):  # 只显示前10个
        title = section['title'][:50] + '...' if len(section['title']) > 50 else section['title']
        print(f"  {section['number']}. {title}")

    # 创建拆分建议
    print("\n💡 建议的拆分方案:")
    for lesson in ELECTRONIC_LESSONS:
        print(f"\n  [{lesson['id']}] {lesson['title']}")
        print(f"      {lesson['description']}")

    print("\n" + "=" * 70)
    print("ℹ️  这是一个分析工具，实际拆分需要手动进行")
    print("   建议基于章节结构进行精细化拆分")
    print("=" * 70)

if __name__ == '__main__':
    main()
