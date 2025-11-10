#!/usr/bin/env python3
"""
生成课程改进跟踪表
"""

import csv
import re
from pathlib import Path


def analyze_lesson(lesson):
    """分析课程状态"""
    content = lesson['Content']
    length = len(content)

    # 检查是否有案例
    has_example = bool(re.search(
        r'example|for instance|scenario|case|matter of',
        content, re.I
    ))

    # 检查结构
    is_structured = (
        content.count('\n\n') >= 2 or
        bool(re.search(r'\n\d+\.|\n-', content))
    )

    # 确定优先级
    lesson_no = int(lesson['No'])

    if length < 200:
        priority = 'Critical'  # 内容过短，紧急
    elif lesson_no <= 30 and not has_example:
        priority = 'High'  # 前30课程缺少案例
    elif lesson_no >= 64 and length < 300:
        priority = 'High'  # 术语定义过短
    elif not has_example:
        priority = 'Medium'  # 缺少案例
    elif not is_structured:
        priority = 'Medium'  # 缺少结构
    else:
        priority = 'Low'  # 已较好

    # 确定类别
    if lesson_no <= 10:
        category = 'Professional'
    elif lesson_no <= 40:
        category = 'Legal'
    elif lesson_no <= 63:
        category = 'Procedure'
    else:
        category = 'Terminology'

    return {
        'length': length,
        'has_example': 'Yes' if has_example else 'No',
        'is_structured': 'Yes' if is_structured else 'No',
        'priority': priority,
        'category': category
    }


def main():
    """主函数"""

    # 读取课程数据
    lessons_file = Path(__file__).parent.parent / 'lessons.csv'

    if not lessons_file.exists():
        print(f"❌ 错误: 找不到 {lessons_file}")
        return

    with open(lessons_file, 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        lessons = list(reader)

    # 生成跟踪表
    tracker_file = Path(__file__).parent.parent / 'improvement_tracker.csv'

    with open(tracker_file, 'w', encoding='UTF-8', newline='') as f:
        fieldnames = [
            'LessonNo',
            'Title',
            'Category',
            'CurrentLength',
            'HasExample',
            'IsStructured',
            'Priority',
            'Status',
            'AssignedTo',
            'CompletedDate',
            'Notes'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lesson in lessons:
            analysis = analyze_lesson(lesson)

            writer.writerow({
                'LessonNo': lesson['No'],
                'Title': lesson['Title'][:50],  # 限制长度
                'Category': analysis['category'],
                'CurrentLength': analysis['length'],
                'HasExample': analysis['has_example'],
                'IsStructured': analysis['is_structured'],
                'Priority': analysis['priority'],
                'Status': 'Pending',
                'AssignedTo': '',
                'CompletedDate': '',
                'Notes': ''
            })

    # 统计
    critical = sum(1 for l in lessons if analyze_lesson(l)['priority'] == 'Critical')
    high = sum(1 for l in lessons if analyze_lesson(l)['priority'] == 'High')
    medium = sum(1 for l in lessons if analyze_lesson(l)['priority'] == 'Medium')
    low = sum(1 for l in lessons if analyze_lesson(l)['priority'] == 'Low')

    print("=" * 80)
    print("📋 课程改进跟踪表已生成")
    print("=" * 80)
    print(f"\n文件位置: {tracker_file}")
    print(f"总课程数: {len(lessons)}")
    print()
    print("优先级分布:")
    print(f"  Critical (紧急): {critical} 课程")
    print(f"  High (高):       {high} 课程")
    print(f"  Medium (中):     {medium} 课程")
    print(f"  Low (低):        {low} 课程")
    print()
    print("下一步:")
    print("  1. 打开 improvement_tracker.csv")
    print("  2. 分配任务到 AssignedTo 列")
    print("  3. 完成后更新 Status 为 'Completed'")
    print("  4. 填写 CompletedDate")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
