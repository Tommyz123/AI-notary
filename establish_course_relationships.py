#!/usr/bin/env python3
"""
P1-3: 建立课程关联网络
分析课程之间的关系，建立学习路径和推荐系统
"""

import json
import re
from typing import List, Dict, Set
from collections import defaultdict

def extract_references(content: str) -> Set[str]:
    """提取内容中引用的法律条款"""
    # 提取 §xxx 格式
    sections = re.findall(r'§\s*(\d+[a-z]*(?:-[a-z])?)', content)
    return set(sections)

def find_lessons_by_section(all_lessons: List[Dict], section: str) -> List[str]:
    """根据法律条款找到相关课程"""
    related = []
    for lesson in all_lessons:
        if f"§{section}" in lesson['title'] or f"§ {section}" in lesson['title']:
            related.append(lesson['lesson_id'])
    return related

def calculate_content_similarity(lesson1: Dict, lesson2: Dict) -> float:
    """计算两个课程的内容相似度（基于关键词重叠）"""
    # 提取关键词
    def get_keywords(lesson):
        keywords = set()
        # 从标题提取
        title_words = set(re.findall(r'\b[A-Za-z]{4,}\b', lesson['title'].lower()))
        keywords.update(title_words)
        # 从关键概念提取
        for concept in lesson.get('key_concepts', []):
            words = set(re.findall(r'\b[A-Za-z]{4,}\b', concept.lower()))
            keywords.update(words)
        return keywords

    kw1 = get_keywords(lesson1)
    kw2 = get_keywords(lesson2)

    if not kw1 or not kw2:
        return 0.0

    intersection = len(kw1 & kw2)
    union = len(kw1 | kw2)

    return intersection / union if union > 0 else 0.0

def build_relationships(all_lessons: List[Dict]) -> Dict[str, List[str]]:
    """为所有课程建立关系网络"""
    relationships = defaultdict(list)

    print("\n🔗 建立课程关系网络...")

    for i, lesson in enumerate(all_lessons):
        lesson_id = lesson['lesson_id']
        related = set()

        # 1. 同一法律条款系列（如§130, §131, §132...）
        if '§' in lesson['title']:
            section_match = re.search(r'§\s*(\d+)', lesson['title'])
            if section_match:
                section_num = int(section_match.group(1))
                # 添加相邻的条款
                for other in all_lessons:
                    other_section = re.search(r'§\s*(\d+)', other['title'])
                    if other_section:
                        other_num = int(other_section.group(1))
                        # 相邻的3个条款
                        if 0 < abs(other_num - section_num) <= 3:
                            related.add(other['lesson_id'])

        # 2. 基于内容引用的法律条款
        content = lesson['content']['raw']
        referenced_sections = extract_references(content)
        for ref_section in list(referenced_sections)[:3]:  # 最多3个引用
            ref_lessons = find_lessons_by_section(all_lessons, ref_section)
            related.update(ref_lessons)

        # 3. 同一模块内的相关课程
        module_id = lesson['module_id']
        module_lessons = [l for l in all_lessons if l['module_id'] == module_id]
        for other in module_lessons:
            if other['lesson_id'] != lesson_id:
                similarity = calculate_content_similarity(lesson, other)
                if similarity > 0.2:  # 相似度阈值
                    related.add(other['lesson_id'])

        # 4. 基于主题的关联
        # 公证操作类课程互相关联
        notarial_acts = ['acknowledgment', 'oath', 'affirmation', 'jurat', 'affidavit']
        if any(act in lesson['title'].lower() for act in notarial_acts):
            for other in all_lessons:
                if other['lesson_id'] != lesson_id:
                    if any(act in other['title'].lower() for act in notarial_acts):
                        related.add(other['lesson_id'])

        # 电子公证相关
        if 'electronic' in lesson['title'].lower() or 'remote' in lesson['title'].lower():
            for other in all_lessons:
                if other['lesson_id'] != lesson_id:
                    if 'electronic' in other['title'].lower() or 'remote' in other['title'].lower():
                        related.add(other['lesson_id'])

        # 5. 限制关联数量，优先选择最相关的
        if lesson_id in related:
            related.remove(lesson_id)  # 移除自身

        relationships[lesson_id] = list(related)[:6]  # 最多6个关联课程

        if (i + 1) % 20 == 0:
            print(f"  已处理 {i + 1}/{len(all_lessons)} 个课程...")

    return relationships

def add_recommended_next_lessons(lesson: Dict, all_lessons: List[Dict]) -> List[str]:
    """推荐下一步应该学习的课程"""
    recommendations = []
    module_id = lesson['module_id']
    lesson_num = int(lesson['original_number'])

    # 1. 同一模块的下一课
    module_lessons = sorted(
        [l for l in all_lessons if l['module_id'] == module_id],
        key=lambda x: int(x['original_number'])
    )
    current_index = next((i for i, l in enumerate(module_lessons) if l['lesson_id'] == lesson['lesson_id']), -1)
    if current_index >= 0 and current_index < len(module_lessons) - 1:
        recommendations.append(module_lessons[current_index + 1]['lesson_id'])

    # 2. 如果是模块的最后一课，推荐下一模块的第一课
    if current_index == len(module_lessons) - 1:
        next_module_id = str(int(module_id) + 1)
        next_module_lessons = [l for l in all_lessons if l['module_id'] == next_module_id]
        if next_module_lessons:
            first_lesson = sorted(next_module_lessons, key=lambda x: int(x['original_number']))[0]
            recommendations.append(first_lesson['lesson_id'])

    return recommendations

def enhance_with_relationships(input_file: str, output_file: str):
    """为课程结构添加关系网络"""
    print("=" * 70)
    print("  P1-3: 建立课程关联网络")
    print("=" * 70)

    # 读取现有结构
    print("\n📖 读取课程结构...")
    with open(input_file, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    # 收集所有课程
    all_lessons = []
    for module in structure['modules']:
        all_lessons.extend(module['lessons'])

    print(f"✅ 读取 {len(all_lessons)} 个课程")

    # 建立关系网络
    relationships = build_relationships(all_lessons)

    # 更新课程结构
    print("\n📝 更新课程关系...")
    for module in structure['modules']:
        for lesson in module['lessons']:
            lesson_id = lesson['lesson_id']
            # 添加关联课程
            lesson['related_lessons'] = relationships.get(lesson_id, [])
            # 添加推荐的下一步课程
            lesson['recommended_next'] = add_recommended_next_lessons(lesson, all_lessons)

    # 添加课程关系统计
    structure['relationship_statistics'] = {
        "total_relationships": sum(len(rels) for rels in relationships.values()),
        "average_relationships_per_lesson": round(
            sum(len(rels) for rels in relationships.values()) / len(all_lessons), 2
        ),
        "lessons_with_relationships": len([r for r in relationships.values() if r])
    }

    # 保存
    print("\n💾 保存增强后的结构...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到: {output_file}")

    # 生成报告
    print("\n" + "=" * 70)
    print("📊 关系网络统计")
    print("=" * 70)
    stats = structure['relationship_statistics']
    print(f"  总关系数: {stats['total_relationships']}")
    print(f"  平均每课关联数: {stats['average_relationships_per_lesson']}")
    print(f"  有关联的课程数: {stats['lessons_with_relationships']}/{len(all_lessons)}")

    # 显示示例
    print("\n" + "=" * 70)
    print("📊 关系示例（前3个课程）")
    print("=" * 70)
    for lesson in all_lessons[:3]:
        print(f"\n[{lesson['lesson_id']}] {lesson['title']}")
        if lesson.get('related_lessons'):
            print(f"  关联课程: {', '.join(lesson['related_lessons'][:3])}")
        if lesson.get('recommended_next'):
            print(f"  推荐下一步: {', '.join(lesson['recommended_next'])}")

    print("\n" + "=" * 70)
    print("✅ P1-3任务完成！")
    print("   下一步: P1-4 添加难度标记")
    print("=" * 70)

def main():
    input_file = '/home/user/AI-notary/course_structure.json'
    output_file = '/home/user/AI-notary/course_structure.json'

    enhance_with_relationships(input_file, output_file)

if __name__ == '__main__':
    main()
