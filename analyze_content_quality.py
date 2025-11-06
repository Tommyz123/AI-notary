#!/usr/bin/env python3
"""
课程内容质量分析工具
Content Quality Analysis Tool for Notary Training System
"""

import sqlite3
import json
from collections import defaultdict
import re

def analyze_content_quality(content, title):
    """分析单个课程内容的质量"""
    if not content:
        return {
            'score': 0,
            'length': 0,
            'structure_score': 0,
            'definition_score': 0,
            'testability_score': 0,
            'issues': ['内容为空 / Content is empty']
        }

    issues = []

    # 1. 内容长度分析 (0-3分)
    length = len(content)
    if length >= 500:
        length_score = 3
    elif length >= 200:
        length_score = 2
    elif length >= 100:
        length_score = 1
    else:
        length_score = 0
        issues.append(f'内容过短 ({length} chars) / Content too short')

    # 2. 结构清晰度 (0-2分)
    structure_indicators = [
        (r'\n\n', '有段落分隔'),
        (r'\n-\s', '有列表项'),
        (r'\n\d+\.', '有编号列表'),
        (r'\[.*?\]', '有章节标记'),
        (r'Definition:|定义:|Key Points:|关键要点:', '有结构化标题')
    ]

    structure_count = sum(1 for pattern, _ in structure_indicators
                         if re.search(pattern, content))

    if structure_count >= 3:
        structure_score = 2
    elif structure_count >= 1:
        structure_score = 1
    else:
        structure_score = 0
        issues.append('缺少结构化元素 / Lacks structure')

    # 3. 定义完整性 (0-2分)
    has_definition = bool(re.search(
        r'(Definition|定义|means|refers to|is defined as|指的是)',
        content,
        re.IGNORECASE
    ))

    has_explanation = bool(re.search(
        r'(because|therefore|for example|such as|specifically|即|例如|因为|所以)',
        content,
        re.IGNORECASE
    ))

    if has_definition and has_explanation:
        definition_score = 2
    elif has_definition or has_explanation:
        definition_score = 1
    else:
        definition_score = 0
        issues.append('缺少清晰定义和解释 / Lacks clear definition')

    # 4. 可测试性 (0-3分)
    # 检查是否包含具体的事实、规则、日期、数字等
    testable_elements = [
        (r'\d+\s+(years?|days?|dollars?|percent)', '包含具体数字'),
        (r'(must|shall|may not|prohibited|required|允许|禁止|必须)', '包含明确规则'),
        (r'(felony|misdemeanor|penalty|fine|imprisonment|罚款|监禁)', '包含法律术语'),
        (r'(\$\d+|§\d+|\d+\%)', '包含具体数据'),
    ]

    testable_count = sum(1 for pattern, _ in testable_elements
                        if re.search(pattern, content, re.IGNORECASE))

    # 检查句子数量（更多句子 = 更多潜在问题）
    sentences = re.split(r'[.!?]+', content)
    sentence_count = len([s for s in sentences if len(s.strip()) > 10])

    if testable_count >= 3 and sentence_count >= 5:
        testability_score = 3
    elif testable_count >= 2 or sentence_count >= 3:
        testability_score = 2
    elif testable_count >= 1 or sentence_count >= 1:
        testability_score = 1
    else:
        testability_score = 0
        issues.append('难以生成有效测验题 / Hard to generate quizzes')

    # 总分
    total_score = length_score + structure_score + definition_score + testability_score

    return {
        'score': total_score,
        'max_score': 10,
        'length': length,
        'length_score': length_score,
        'structure_score': structure_score,
        'definition_score': definition_score,
        'testability_score': testability_score,
        'sentence_count': sentence_count,
        'issues': issues
    }

def generate_statistics(results):
    """生成统计数据"""
    stats = {
        'total_lessons': len(results),
        'score_distribution': defaultdict(int),
        'avg_score': 0,
        'avg_length': 0,
        'quality_levels': {
            'excellent': [],  # 8-10
            'good': [],       # 6-7
            'fair': [],       # 4-5
            'poor': []        # 0-3
        },
        'issues_summary': defaultdict(int)
    }

    total_score = 0
    total_length = 0

    for result in results:
        score = result['analysis']['score']
        stats['score_distribution'][score] += 1
        total_score += score
        total_length += result['analysis']['length']

        # 分级
        if score >= 8:
            stats['quality_levels']['excellent'].append(result)
        elif score >= 6:
            stats['quality_levels']['good'].append(result)
        elif score >= 4:
            stats['quality_levels']['fair'].append(result)
        else:
            stats['quality_levels']['poor'].append(result)

        # 问题统计
        for issue in result['analysis']['issues']:
            stats['issues_summary'][issue] += 1

    stats['avg_score'] = total_score / len(results) if results else 0
    stats['avg_length'] = total_length / len(results) if results else 0

    return stats

def main():
    # 连接数据库
    conn = sqlite3.connect('notary_training.db')
    cursor = conn.cursor()

    # 读取所有课程
    cursor.execute('SELECT lesson_no, title, content FROM lessons ORDER BY lesson_no')
    lessons = cursor.fetchall()

    print(f"\n{'='*80}")
    print(f"课程内容质量分析报告 / Content Quality Analysis Report")
    print(f"{'='*80}\n")
    print(f"总课程数 / Total Lessons: {len(lessons)}\n")

    # 分析每门课程
    results = []
    for lesson_no, title, content in lessons:
        analysis = analyze_content_quality(content, title)
        results.append({
            'lesson_no': lesson_no,
            'title': title,
            'analysis': analysis
        })

    # 生成统计
    stats = generate_statistics(results)

    # 输出统计信息
    print(f"\n{'='*80}")
    print(f"质量分级统计 / Quality Level Statistics")
    print(f"{'='*80}\n")

    print(f"✅ 优秀 (8-10分 / Excellent): {len(stats['quality_levels']['excellent'])} 门课程 "
          f"({len(stats['quality_levels']['excellent'])/stats['total_lessons']*100:.1f}%)")
    print(f"👍 良好 (6-7分 / Good): {len(stats['quality_levels']['good'])} 门课程 "
          f"({len(stats['quality_levels']['good'])/stats['total_lessons']*100:.1f}%)")
    print(f"⚠️  一般 (4-5分 / Fair): {len(stats['quality_levels']['fair'])} 门课程 "
          f"({len(stats['quality_levels']['fair'])/stats['total_lessons']*100:.1f}%)")
    print(f"❌ 较差 (0-3分 / Poor): {len(stats['quality_levels']['poor'])} 门课程 "
          f"({len(stats['quality_levels']['poor'])/stats['total_lessons']*100:.1f}%)")

    print(f"\n平均分数 / Average Score: {stats['avg_score']:.2f} / 10")
    print(f"平均长度 / Average Length: {stats['avg_length']:.0f} 字符")

    # 输出最差的10门课程
    print(f"\n{'='*80}")
    print(f"需要紧急改进的课程 (评分0-3分) / Courses Needing Urgent Improvement")
    print(f"{'='*80}\n")

    poor_courses = sorted(stats['quality_levels']['poor'],
                         key=lambda x: x['analysis']['score'])[:20]

    for result in poor_courses:
        print(f"\n课程 {result['lesson_no']}: {result['title']}")
        print(f"  评分: {result['analysis']['score']}/10")
        print(f"  长度: {result['analysis']['length']} 字符")
        print(f"  问题:")
        for issue in result['analysis']['issues']:
            print(f"    - {issue}")

    # 输出优秀课程示例
    print(f"\n{'='*80}")
    print(f"优秀课程示例 (评分8-10分) / Excellent Course Examples")
    print(f"{'='*80}\n")

    excellent_courses = sorted(stats['quality_levels']['excellent'],
                              key=lambda x: x['analysis']['score'],
                              reverse=True)[:5]

    for result in excellent_courses:
        print(f"\n课程 {result['lesson_no']}: {result['title']}")
        print(f"  评分: {result['analysis']['score']}/10")
        print(f"  长度: {result['analysis']['length']} 字符")
        print(f"  详细分数:")
        print(f"    - 内容长度: {result['analysis']['length_score']}/3")
        print(f"    - 结构清晰: {result['analysis']['structure_score']}/2")
        print(f"    - 定义完整: {result['analysis']['definition_score']}/2")
        print(f"    - 可测试性: {result['analysis']['testability_score']}/3")

    # 输出问题汇总
    print(f"\n{'='*80}")
    print(f"主要问题汇总 / Main Issues Summary")
    print(f"{'='*80}\n")

    sorted_issues = sorted(stats['issues_summary'].items(),
                          key=lambda x: x[1],
                          reverse=True)

    for issue, count in sorted_issues[:10]:
        print(f"  {issue}: {count} 门课程 "
              f"({count/stats['total_lessons']*100:.1f}%)")

    # 生成改进建议
    print(f"\n{'='*80}")
    print(f"改进建议 / Improvement Recommendations")
    print(f"{'='*80}\n")

    poor_count = len(stats['quality_levels']['poor'])
    fair_count = len(stats['quality_levels']['fair'])

    print(f"优先级 P1 - 紧急: 改进 {poor_count} 门较差课程 (0-3分)")
    print(f"  预计工作量: {poor_count * 0.5:.1f} - {poor_count * 0.75:.1f} 小时")
    print(f"  建议行动: 重写内容，添加定义、结构、示例\n")

    print(f"优先级 P2 - 重要: 改进 {fair_count} 门一般课程 (4-5分)")
    print(f"  预计工作量: {fair_count * 0.3:.1f} - {fair_count * 0.5:.1f} 小时")
    print(f"  建议行动: 扩展内容，优化结构，增加可测试点\n")

    total_hours_min = poor_count * 0.5 + fair_count * 0.3
    total_hours_max = poor_count * 0.75 + fair_count * 0.5
    print(f"总预计投入: {total_hours_min:.1f} - {total_hours_max:.1f} 小时")

    # 保存详细结果到JSON
    output = {
        'analysis_date': '2025-11-06',
        'total_lessons': stats['total_lessons'],
        'statistics': {
            'avg_score': stats['avg_score'],
            'avg_length': stats['avg_length'],
            'quality_distribution': {
                'excellent': len(stats['quality_levels']['excellent']),
                'good': len(stats['quality_levels']['good']),
                'fair': len(stats['quality_levels']['fair']),
                'poor': len(stats['quality_levels']['poor'])
            }
        },
        'lessons': results
    }

    with open('content_quality_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"详细分析结果已保存到: content_quality_analysis.json")
    print(f"{'='*80}\n")

    conn.close()

if __name__ == '__main__':
    main()
