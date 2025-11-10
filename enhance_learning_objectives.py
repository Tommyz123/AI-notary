#!/usr/bin/env python3
"""
P1-2: 增强学习目标和关键概念
为每个课程生成更精确的学习目标和关键概念
"""

import json
import re
from typing import List, Dict

def extract_legal_sections(content: str) -> List[str]:
    """提取法律条款（§符号）"""
    sections = re.findall(r'§\s*\d+[a-z]*(?:-[a-z])?', content)
    return list(set(sections))

def extract_case_references(content: str) -> List[str]:
    """提取案例引用"""
    # 匹配 "Matter of XXX" 或 "XXX v. YYY" 格式
    cases = re.findall(r'(?:Matter of|People (?:ex rel\.|v\.)) [A-Z]\w+|[A-Z]\w+ v\. [A-Z]\w+', content)
    return list(set(cases))[:3]  # 最多3个

def extract_key_terms(content: str, title: str) -> List[str]:
    """从标题和内容中提取关键术语"""
    key_terms = []

    # 从标题提取
    title_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', title)
    key_terms.extend(title_words[:2])

    # 查找引号中的重要术语
    quoted = re.findall(r'"([^"]+)"', content)
    for q in quoted[:3]:
        if len(q.split()) <= 4:  # 短语
            key_terms.append(q)

    # 查找大写开头的重要短语
    important_phrases = re.findall(
        r'\b(?:Personal Appearance|Oath|Affirmation|Acknowledgment|Jurat|'
        r'Notarial Act|Certificate|Signature|Identity|Verification|'
        r'Credential Analysis|Identity Proofing|Remote|Electronic|'
        r'Real Property|Mortgage|Deed|Conveyance)\b',
        content
    )
    key_terms.extend(list(set(important_phrases))[:3])

    return list(set(key_terms))[:5]

def generate_learning_objectives(lesson: Dict) -> List[str]:
    """根据课程内容生成具体的学习目标"""
    title = lesson['title']
    content = lesson['content']['raw']
    module_id = lesson['module_id']

    objectives = []

    # 基于课程类型生成不同的学习目标
    if '§' in title:
        # 法律条款课程
        section_num = re.search(r'§\s*(\d+[a-z]*)', title)
        if section_num:
            objectives.append(f"理解纽约州法律{section_num.group(0)}的具体规定和适用范围")
            objectives.append(f"掌握{section_num.group(0)}中的关键要求和限制条件")

    if "definition" in title.lower():
        # 定义类课程
        objectives.append("准确理解并记忆关键法律术语的官方定义")
        objectives.append("能够在实际场景中正确识别和应用相关概念")

    elif any(kw in title.lower() for kw in ["acknowledgment", "oath", "affirmation", "jurat"]):
        # 公证操作类
        objectives.append(f"掌握{title}的标准程序和法律要求")
        objectives.append(f"能够正确执行{title}并识别常见错误")
        objectives.append("了解违规操作的法律后果和责任")

    elif any(kw in title.lower() for kw in ["electronic", "remote", "video"]):
        # 电子公证类
        objectives.append("理解电子公证的技术要求和安全标准")
        objectives.append("掌握身份验证和通讯技术的具体规范")
        objectives.append("了解电子公证与传统公证的关键区别")

    elif any(kw in title.lower() for kw in ["seal", "certificate", "signature"]):
        # 实务操作类
        objectives.append(f"掌握{title}的正确格式和使用方法")
        objectives.append("了解相关的法律要求和最佳实践")

    elif any(kw in content.lower() for kw in ["penalty", "violation", "criminal", "removal"]):
        # 违规处罚类
        objectives.append("识别可能导致处罚的违规行为")
        objectives.append("理解违规的法律后果（刑事、民事责任）")
        objectives.append("掌握合规操作的标准和要求")

    # 如果还没有足够的目标，添加通用目标
    while len(objectives) < 3:
        if len(objectives) == 0:
            objectives.append(f"全面理解{title}的核心内容和法律依据")
        elif len(objectives) == 1:
            objectives.append(f"掌握{title}在实际工作中的应用方法")
        else:
            objectives.append("能够识别和避免相关的常见错误和风险")

    return objectives[:4]  # 最多4个目标

def enhance_key_concepts(lesson: Dict) -> List[str]:
    """增强关键概念提取"""
    content = lesson['content']['raw']
    title = lesson['title']

    concepts = []

    # 1. 法律条款
    legal_sections = extract_legal_sections(content)
    concepts.extend(legal_sections[:2])

    # 2. 案例引用
    cases = extract_case_references(content)
    concepts.extend(cases[:2])

    # 3. 关键术语
    key_terms = extract_key_terms(content, title)
    concepts.extend(key_terms[:3])

    # 4. 从内容中提取数字信息（如期限、费用等）
    numbers = re.findall(r'\$\d+|(?:\d+)\s*(?:year|month|day|hour)s?', content)
    if numbers:
        concepts.extend([f"重要数值: {numbers[0]}"])

    return list(dict.fromkeys(concepts))[:6]  # 去重，最多6个

def add_prerequisites(lesson: Dict, all_lessons: List[Dict]) -> List[str]:
    """添加前置课程"""
    prerequisites = []
    module_id = lesson['module_id']
    lesson_num = int(lesson['original_number'])

    # Module 0的课程没有前置要求
    if module_id == "0":
        return []

    # 其他模块的第一课推荐完成Module 0
    if lesson_num > 4:  # 第一个非Module 0的课
        module_lessons = [l for l in all_lessons if l['module_id'] == module_id]
        if module_lessons and module_lessons[0]['lesson_id'] == lesson['lesson_id']:
            prerequisites.append("0.001")  # Module 0概览

    # 如果是法律条款的后续部分，添加前一条款
    if '§' in lesson['title']:
        section_num = re.search(r'§\s*(\d+)', lesson['title'])
        if section_num:
            num = int(section_num.group(1))
            if num > 130:
                # 查找前一个§条款
                for prev_lesson in all_lessons:
                    prev_section = re.search(r'§\s*(\d+)', prev_lesson['title'])
                    if prev_section and int(prev_section.group(1)) == num - 1:
                        prerequisites.append(prev_lesson['lesson_id'])
                        break

    return prerequisites[:2]  # 最多2个前置课程

def enhance_course_structure(input_file: str, output_file: str):
    """增强整个课程结构"""
    print("=" * 70)
    print("  P1-2: 增强学习目标和关键概念")
    print("=" * 70)

    # 读取现有结构
    print("\n📖 读取课程结构...")
    with open(input_file, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    # 收集所有课程（用于建立前置关系）
    all_lessons = []
    for module in structure['modules']:
        all_lessons.extend(module['lessons'])

    # 增强每个课程
    print("\n🔧 增强学习目标和关键概念...")
    enhanced_count = 0
    for module in structure['modules']:
        print(f"\n  处理 Module {module['module_id']}: {module['title']}")
        for lesson in module['lessons']:
            # 生成新的学习目标
            lesson['learning_objectives'] = generate_learning_objectives(lesson)

            # 增强关键概念
            lesson['key_concepts'] = enhance_key_concepts(lesson)

            # 添加前置课程
            lesson['prerequisites'] = add_prerequisites(lesson, all_lessons)

            enhanced_count += 1
            if enhanced_count % 10 == 0:
                print(f"    已处理 {enhanced_count}/{len(all_lessons)} 个课程...")

    print(f"\n✅ 成功增强 {enhanced_count} 个课程")

    # 保存增强后的结构
    print("\n💾 保存增强后的结构...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到: {output_file}")

    # 生成示例报告
    print("\n" + "=" * 70)
    print("📊 增强示例（前3个课程）")
    print("=" * 70)
    for i, lesson in enumerate(all_lessons[:3]):
        print(f"\n[{lesson['lesson_id']}] {lesson['title']}")
        print(f"\n  学习目标:")
        for obj in lesson['learning_objectives']:
            print(f"    • {obj}")
        print(f"\n  关键概念:")
        for concept in lesson['key_concepts']:
            print(f"    • {concept}")
        if lesson['prerequisites']:
            print(f"\n  前置课程: {', '.join(lesson['prerequisites'])}")

    print("\n" + "=" * 70)
    print("✅ P1-2任务完成！")
    print("   下一步: P1-3 建立课程关联网络")
    print("=" * 70)

def main():
    input_file = '/home/user/AI-notary/course_structure.json'
    output_file = '/home/user/AI-notary/course_structure.json'  # 覆盖原文件

    enhance_course_structure(input_file, output_file)

if __name__ == '__main__':
    main()
