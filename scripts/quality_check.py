#!/usr/bin/env python3
"""
课程质量自动检查脚本
检查: 长度、结构、案例、法律引用等
"""

import csv
import re
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_lesson_quality(lesson):
    """检查单个课程质量"""
    score = 0
    issues = []
    details = {}

    content = lesson['Content']
    length = len(content)

    # 1. 检查长度 (20分)
    if length < 200:
        issues.append("内容过短(<200字符)")
        details['length_score'] = 0
    elif length < 300:
        details['length_score'] = 10
        score += 10
    else:
        details['length_score'] = 20
        score += 20

    # 2. 检查结构 (20分)
    paragraphs = content.count('\n\n')
    has_list = bool(re.search(r'\n\d+\.|\n-|\n\*', content))

    if paragraphs >= 2 or has_list:
        details['structure_score'] = 20
        score += 20
    elif paragraphs >= 1:
        details['structure_score'] = 10
        score += 10
    else:
        issues.append("缺少段落结构")
        details['structure_score'] = 0

    # 3. 检查案例 (30分)
    case_keywords = [
        r'example', r'for instance', r'scenario', r'case',
        r'matter of', r'people v\.', r'实例', r'场景', r'案例'
    ]
    has_example = any(re.search(kw, content, re.I) for kw in case_keywords)

    if has_example:
        details['example_score'] = 30
        score += 30
    else:
        issues.append("缺少案例/示例")
        details['example_score'] = 0

    # 4. 检查专业性 (15分)
    legal_refs = re.findall(r'§\d+|Executive Law|Real Property Law|Election Law|County Law', content)

    if len(legal_refs) >= 3:
        details['legal_score'] = 15
        score += 15
    elif len(legal_refs) >= 1:
        details['legal_score'] = 10
        score += 10
    else:
        details['legal_score'] = 0

    # 5. 检查实用性 (15分)
    practical_keywords = [
        r'notary', r'must', r'shall', r'should', r'important',
        r'note', r'warning', r'correct', r'incorrect'
    ]
    practical_count = sum(1 for kw in practical_keywords
                          if re.search(kw, content, re.I))

    if practical_count >= 5:
        details['practical_score'] = 15
        score += 15
    elif practical_count >= 3:
        details['practical_score'] = 10
        score += 10
    elif practical_count >= 1:
        details['practical_score'] = 5
        score += 5
    else:
        details['practical_score'] = 0

    details['total_score'] = score
    details['length'] = length
    details['paragraphs'] = paragraphs
    details['legal_refs'] = len(legal_refs)

    return score, issues, details


def calculate_teaching_fitness(lessons):
    """计算教学适配度"""

    # 案例覆盖率 (30%)
    with_examples = sum(1 for l in lessons
        if any(kw in l['Content'].lower()
               for kw in ['example', 'for instance', 'scenario', 'case', 'matter of']))
    example_rate = with_examples / len(lessons) * 100

    # 结构化率 (30%)
    structured = sum(1 for l in lessons
        if l['Content'].count('\n\n') >= 2 or
           re.search(r'\n\d+\.|\n-', l['Content']))
    structure_rate = structured / len(lessons) * 100

    # 内容充足度 (20%)
    adequate = sum(1 for l in lessons if len(l['Content']) >= 200)
    adequate_rate = adequate / len(lessons) * 100

    # 专业性 (10%)
    with_legal = sum(1 for l in lessons if re.search(r'§\d+', l['Content']))
    legal_rate = with_legal / len(lessons) * 100

    # 权威性 (10%)
    with_cases = sum(1 for l in lessons
        if re.search(r'Matter of|People v\.', l['Content']))
    case_rate = with_cases / len(lessons) * 100

    # 加权总分
    fitness = (
        example_rate * 0.30 +
        structure_rate * 0.30 +
        adequate_rate * 0.20 +
        legal_rate * 0.10 +
        case_rate * 0.10
    )

    return {
        'fitness': fitness,
        'example_rate': example_rate,
        'structure_rate': structure_rate,
        'adequate_rate': adequate_rate,
        'legal_rate': legal_rate,
        'case_rate': case_rate,
        'with_examples': with_examples,
        'structured': structured,
        'adequate': adequate
    }


def main():
    """主函数"""

    # 读取课程数据
    lessons_file = Path(__file__).parent.parent / 'lessons.csv'

    if not lessons_file.exists():
        print(f"❌ 错误: 找不到 {lessons_file}")
        sys.exit(1)

    with open(lessons_file, 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        lessons = list(reader)

    print("=" * 80)
    print("📊 课程质量检查报告")
    print("=" * 80)
    print(f"\n总课程数: {len(lessons)}")
    print(f"数据文件: {lessons_file}")
    print()

    # 整体质量分析
    total_score = 0
    all_issues = []

    excellent = 0  # ≥80分
    good = 0       # 60-79分
    fair = 0       # 40-59分
    poor = 0       # <40分

    problem_lessons = []

    for lesson in lessons:
        score, issues, details = check_lesson_quality(lesson)
        total_score += score

        if score >= 80:
            excellent += 1
        elif score >= 60:
            good += 1
        elif score >= 40:
            fair += 1
        else:
            poor += 1
            problem_lessons.append({
                'No': lesson['No'],
                'Title': lesson['Title'],
                'Score': score,
                'Issues': issues,
                'Length': details['length']
            })

    avg_score = total_score / len(lessons)

    # 输出总体质量
    print("【整体质量评分】")
    print(f"  平均分数: {avg_score:.1f}/100")
    print()
    print("  质量分布:")
    print(f"    优秀 (≥80分): {excellent} 课程 ({excellent/len(lessons)*100:.1f}%)")
    print(f"    良好 (60-79): {good} 课程 ({good/len(lessons)*100:.1f}%)")
    print(f"    合格 (40-59): {fair} 课程 ({fair/len(lessons)*100:.1f}%)")
    print(f"    不合格 (<40): {poor} 课程 ({poor/len(lessons)*100:.1f}%)")
    print()

    # 教学适配度
    fitness_data = calculate_teaching_fitness(lessons)

    print("【教学适配度评估】")
    print(f"  总体适配度: {fitness_data['fitness']:.1f}%")
    print()
    print("  细分指标:")
    print(f"    案例覆盖率 (30%): {fitness_data['example_rate']:.1f}% ({fitness_data['with_examples']} 课程)")
    print(f"    结构化率 (30%):   {fitness_data['structure_rate']:.1f}% ({fitness_data['structured']} 课程)")
    print(f"    内容充足度 (20%): {fitness_data['adequate_rate']:.1f}% ({fitness_data['adequate']} 课程)")
    print(f"    专业性 (10%):     {fitness_data['legal_rate']:.1f}%")
    print(f"    权威性 (10%):     {fitness_data['case_rate']:.1f}%")
    print()

    # 评级
    fitness = fitness_data['fitness']
    if fitness >= 70:
        grade = "优秀 🏆"
    elif fitness >= 60:
        grade = "良好 ✓"
    elif fitness >= 50:
        grade = "合格 ~"
    else:
        grade = "需改进 ⚠️"

    print(f"  评级: {grade}")
    print()

    # 问题课程
    if problem_lessons:
        print("【需要改进的课程】")
        print(f"  共 {len(problem_lessons)} 个课程需要重点改进:")
        print()

        for p in problem_lessons[:10]:  # 只显示前10个
            print(f"  {p['No']}: {p['Title']}")
            print(f"    评分: {p['Score']}/100")
            print(f"    长度: {p['Length']} 字符")
            print(f"    问题: {', '.join(p['Issues'])}")
            print()

        if len(problem_lessons) > 10:
            print(f"  ... 还有 {len(problem_lessons) - 10} 个课程需要改进")
            print()

    # 改进建议
    print("【改进建议】")

    if fitness_data['example_rate'] < 50:
        print(f"  ⚠️ 案例覆盖率偏低 ({fitness_data['example_rate']:.1f}%)")
        print(f"     建议: 为至少 {int(len(lessons) * 0.5 - fitness_data['with_examples'])} 个课程添加案例")

    if fitness_data['structure_rate'] < 60:
        print(f"  ⚠️ 结构化率偏低 ({fitness_data['structure_rate']:.1f}%)")
        print(f"     建议: 为至少 {int(len(lessons) * 0.6 - fitness_data['structured'])} 个课程优化结构")

    if fitness_data['adequate_rate'] < 95:
        print(f"  ⚠️ 内容充足度不足 ({fitness_data['adequate_rate']:.1f}%)")
        print(f"     建议: 扩充 {len(lessons) - fitness_data['adequate']} 个课程的内容")

    print()
    print("=" * 80)
    print(f"✓ 检查完成")
    print("=" * 80)

    # 返回状态码
    if fitness >= 65:
        sys.exit(0)  # 成功
    else:
        sys.exit(1)  # 需要改进


if __name__ == '__main__':
    main()
