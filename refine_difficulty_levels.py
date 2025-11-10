#!/usr/bin/env python3
"""
P1-4: 完善难度标记
基于内容复杂度、法律概念密度、先决条件等因素优化难度评级
"""

import json
import re
from typing import Dict, List

def calculate_content_complexity(lesson: Dict) -> int:
    """计算内容复杂度（1-10分）"""
    content = lesson['content']['raw']
    score = 0

    # 1. 内容长度（长度越长，难度可能越高）
    word_count = lesson['content']['word_count']
    if word_count < 300:
        score += 1
    elif word_count < 600:
        score += 2
    elif word_count < 900:
        score += 3
    else:
        score += 4

    # 2. 法律条款引用数量
    legal_refs = len(re.findall(r'§\s*\d+', content))
    score += min(legal_refs // 2, 2)  # 最多加2分

    # 3. 案例引用数量（案例多 = 更复杂）
    case_refs = len(re.findall(r'Matter of|People v\.|v\. ', content))
    score += min(case_refs, 2)  # 最多加2分

    # 4. 专业术语密度
    technical_terms = [
        'acknowledgment', 'jurat', 'affidavit', 'affirmation', 'authentication',
        'apostille', 'certification', 'conveyance', 'credential', 'notarization',
        'verification', 'attestation', 'deposition'
    ]
    term_count = sum(1 for term in technical_terms if term in content.lower())
    score += min(term_count // 2, 2)  # 最多加2分

    return min(score, 10)  # 最高10分

def determine_difficulty(lesson: Dict, complexity_score: int) -> str:
    """根据复杂度分数和其他因素确定难度等级"""
    module_id = lesson['module_id']
    title = lesson['title'].lower()

    # 基础难度（基于复杂度分数）
    if complexity_score <= 3:
        base_difficulty = "⭐"
    elif complexity_score <= 5:
        base_difficulty = "⭐⭐"
    elif complexity_score <= 7:
        base_difficulty = "⭐⭐⭐"
    elif complexity_score <= 9:
        base_difficulty = "⭐⭐⭐⭐"
    else:
        base_difficulty = "⭐⭐⭐⭐⭐"

    # 模块调整
    # Module 0 (入门) - 降低难度
    if module_id == "0":
        return "⭐"

    # Module 4 (电子公证) - 相对较难
    if module_id == "4":
        if base_difficulty in ["⭐", "⭐⭐"]:
            return "⭐⭐⭐"
        return base_difficulty

    # Module 9 (进阶) - 通常较难
    if module_id == "9":
        if base_difficulty in ["⭐", "⭐⭐"]:
            return "⭐⭐⭐"
        return base_difficulty

    # 特殊主题调整
    # 定义类课程 - 通常简单
    if 'definition' in title:
        return min(base_difficulty, "⭐⭐", key=lambda x: len(x))

    # 电子公证 - 较难
    if 'electronic' in title or 'remote' in title:
        if len(base_difficulty) < 3:
            return "⭐⭐⭐"

    # 复杂法律程序 - 较难
    if any(kw in title for kw in ['protest', 'apostille', 'authentication', 'corporation']):
        if len(base_difficulty) < 4:
            return "⭐⭐⭐⭐"

    return base_difficulty

def add_difficulty_metadata(lesson: Dict, complexity_score: int) -> Dict:
    """添加详细的难度元数据"""
    return {
        "level": lesson['difficulty'],
        "complexity_score": complexity_score,
        "factors": {
            "content_length": lesson['content']['word_count'],
            "legal_references": len(re.findall(r'§\s*\d+', lesson['content']['raw'])),
            "case_references": len(re.findall(r'Matter of|People v\.', lesson['content']['raw'])),
            "prerequisites_count": len(lesson.get('prerequisites', []))
        },
        "learning_tips": get_learning_tips(lesson['difficulty'])
    }

def get_learning_tips(difficulty: str) -> List[str]:
    """根据难度提供学习建议"""
    tips = {
        "⭐": [
            "适合初学者，建议仔细阅读",
            "预计学习时间：15-20分钟",
            "可以快速掌握基础概念"
        ],
        "⭐⭐": [
            "需要理解基本法律概念",
            "预计学习时间：20-30分钟",
            "建议做笔记记录重点"
        ],
        "⭐⭐⭐": [
            "包含较多专业术语和法律条款",
            "预计学习时间：30-45分钟",
            "建议结合案例理解",
            "可能需要复习前置课程"
        ],
        "⭐⭐⭐⭐": [
            "内容复杂，需要深入理解",
            "预计学习时间：45-60分钟",
            "建议分段学习，做好笔记",
            "完成后进行自测巩固"
        ],
        "⭐⭐⭐⭐⭐": [
            "最高难度，综合运用多个概念",
            "预计学习时间：60分钟以上",
            "建议先复习相关基础课程",
            "可能需要多次学习才能完全掌握",
            "强烈建议做练习题巩固"
        ]
    }
    return tips.get(difficulty, [])

def refine_all_difficulties(input_file: str, output_file: str):
    """优化所有课程的难度标记"""
    print("=" * 70)
    print("  P1-4: 完善难度标记")
    print("=" * 70)

    # 读取结构
    print("\n📖 读取课程结构...")
    with open(input_file, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    # 收集所有课程
    all_lessons = []
    for module in structure['modules']:
        all_lessons.extend(module['lessons'])

    print(f"✅ 读取 {len(all_lessons)} 个课程")

    # 计算并更新难度
    print("\n🎯 分析内容复杂度并更新难度...")
    difficulty_distribution = {"⭐": 0, "⭐⭐": 0, "⭐⭐⭐": 0, "⭐⭐⭐⭐": 0, "⭐⭐⭐⭐⭐": 0}

    for i, lesson in enumerate(all_lessons):
        # 计算复杂度
        complexity = calculate_content_complexity(lesson)

        # 确定难度
        new_difficulty = determine_difficulty(lesson, complexity)
        lesson['difficulty'] = new_difficulty
        difficulty_distribution[new_difficulty] += 1

        # 添加难度元数据
        lesson['difficulty_metadata'] = add_difficulty_metadata(lesson, complexity)

        if (i + 1) % 20 == 0:
            print(f"  已处理 {i + 1}/{len(all_lessons)} 个课程...")

    # 更新模块难度（基于该模块课程的平均难度）
    print("\n📊 更新模块难度...")
    for module in structure['modules']:
        if module['lessons']:
            avg_difficulty = sum(len(l['difficulty']) for l in module['lessons']) / len(module['lessons'])
            if avg_difficulty <= 1.5:
                module['difficulty'] = "⭐"
            elif avg_difficulty <= 2.5:
                module['difficulty'] = "⭐⭐"
            elif avg_difficulty <= 3.5:
                module['difficulty'] = "⭐⭐⭐"
            elif avg_difficulty <= 4.5:
                module['difficulty'] = "⭐⭐⭐⭐"
            else:
                module['difficulty'] = "⭐⭐⭐⭐⭐"

    # 添加难度统计
    structure['difficulty_statistics'] = {
        "distribution": difficulty_distribution,
        "easiest_lessons": sorted(
            all_lessons,
            key=lambda x: (len(x['difficulty']), x['difficulty_metadata']['complexity_score'])
        )[:5],
        "hardest_lessons": sorted(
            all_lessons,
            key=lambda x: (len(x['difficulty']), x['difficulty_metadata']['complexity_score']),
            reverse=True
        )[:5]
    }

    # 保存简化版（移除完整课程内容以减小统计文件大小）
    stats = {
        "distribution": difficulty_distribution,
        "easiest_lessons": [
            {
                "lesson_id": l['lesson_id'],
                "title": l['title'],
                "difficulty": l['difficulty'],
                "complexity_score": l['difficulty_metadata']['complexity_score']
            }
            for l in structure['difficulty_statistics']['easiest_lessons']
        ],
        "hardest_lessons": [
            {
                "lesson_id": l['lesson_id'],
                "title": l['title'],
                "difficulty": l['difficulty'],
                "complexity_score": l['difficulty_metadata']['complexity_score']
            }
            for l in structure['difficulty_statistics']['hardest_lessons']
        ]
    }
    structure['difficulty_statistics'] = stats

    # 保存
    print("\n💾 保存更新后的结构...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到: {output_file}")

    # 生成报告
    print("\n" + "=" * 70)
    print("📊 难度分布统计")
    print("=" * 70)
    for difficulty, count in difficulty_distribution.items():
        percentage = (count / len(all_lessons)) * 100
        print(f"  {difficulty}: {count} 个课程 ({percentage:.1f}%)")

    print("\n" + "=" * 70)
    print("📉 最简单的5个课程")
    print("=" * 70)
    for lesson in stats['easiest_lessons']:
        print(f"  [{lesson['lesson_id']}] {lesson['title']}")
        print(f"      难度: {lesson['difficulty']} | 复杂度: {lesson['complexity_score']}/10")

    print("\n" + "=" * 70)
    print("📈 最困难的5个课程")
    print("=" * 70)
    for lesson in stats['hardest_lessons']:
        print(f"  [{lesson['lesson_id']}] {lesson['title']}")
        print(f"      难度: {lesson['difficulty']} | 复杂度: {lesson['complexity_score']}/10")

    print("\n" + "=" * 70)
    print("✅ P1-4任务完成！")
    print("   🎉 P1阶段全部完成！")
    print("=" * 70)

def main():
    input_file = '/home/user/AI-notary/course_structure.json'
    output_file = '/home/user/AI-notary/course_structure.json'

    refine_all_difficulties(input_file, output_file)

if __name__ == '__main__':
    main()
