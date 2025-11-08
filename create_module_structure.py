#!/usr/bin/env python3
"""
创建课程模块化JSON结构
将121个课程组织成10个模块的层次结构
"""

import csv
import json
import re
from typing import List, Dict

# 10个模块的定义
MODULES = [
    {
        "module_id": "0",
        "title": "入门导读 (Introduction)",
        "difficulty": "⭐",
        "description": "课程介绍和新手指南",
        "lesson_pattern": r"^(00[0-4]|Module 0)"
    },
    {
        "module_id": "1",
        "title": "基础知识 (Foundation)",
        "difficulty": "⭐",
        "description": "公证人职业基础、职责与资格要求",
        "keywords": ["professional conduct", "appointment", "qualification", "duties", "powers", "misconduct"]
    },
    {
        "module_id": "2",
        "title": "任命流程 (Appointment Process)",
        "difficulty": "⭐⭐",
        "description": "申请、考试、认证与续期",
        "keywords": ["application", "exam", "commission", "renewal", "fee", "oath"]
    },
    {
        "module_id": "3",
        "title": "公证操作 (Notarial Acts)",
        "difficulty": "⭐⭐",
        "description": "认证、宣誓、证词等公证行为",
        "keywords": ["acknowledgment", "oath", "affirmation", "affidavit", "jurat", "proof", "administration"]
    },
    {
        "module_id": "4",
        "title": "电子公证 (Electronic Notarization)",
        "difficulty": "⭐⭐⭐",
        "description": "电子公证技术要求与实施",
        "keywords": ["electronic", "digital", "remote", "video", "audio", "technology", "credential analysis"]
    },
    {
        "module_id": "5",
        "title": "房地产文件 (Real Property)",
        "difficulty": "⭐⭐⭐",
        "description": "房地产相关文件公证",
        "keywords": ["real property", "deed", "mortgage", "conveyance", "recording"]
    },
    {
        "module_id": "6",
        "title": "限制与合规 (Compliance & Restrictions)",
        "difficulty": "⭐⭐⭐",
        "description": "禁止行为、利益冲突和法律边界",
        "keywords": ["prohibition", "advertising", "conflict", "legal practice", "unauthorized"]
    },
    {
        "module_id": "7",
        "title": "违规与处罚 (Violations & Penalties)",
        "difficulty": "⭐⭐⭐",
        "description": "违规行为、刑事民事责任",
        "keywords": ["violation", "penalty", "criminal", "misdemeanor", "felony", "removal", "liability"]
    },
    {
        "module_id": "8",
        "title": "专业实务 (Professional Practice)",
        "difficulty": "⭐⭐⭐⭐",
        "description": "印章、记录、证书格式等实务操作",
        "keywords": ["seal", "stamp", "certificate", "journal", "record", "form", "signature"]
    },
    {
        "module_id": "9",
        "title": "进阶专题 (Advanced Topics)",
        "difficulty": "⭐⭐⭐⭐",
        "description": "特殊情况、定义、术语和复杂案例",
        "keywords": ["definition", "corporation", "authentication", "apostille", "certification", "protest"]
    }
]

def read_lessons(csv_file: str) -> List[Dict]:
    """读取所有课程"""
    lessons = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lessons.append({
                'number': row['No'],
                'title': row['Title'],
                'content': row['Content']
            })
    return lessons

def estimate_difficulty(lesson_number: int, title: str, content: str) -> str:
    """估算课程难度"""
    # 基于课程编号和内容长度估算
    num = int(lesson_number)
    content_length = len(content)

    if num <= 10:
        return "⭐"
    elif num <= 30:
        return "⭐⭐"
    elif num <= 70:
        return "⭐⭐⭐"
    elif num <= 100:
        return "⭐⭐⭐⭐"
    else:
        return "⭐⭐⭐⭐⭐"

def estimate_time(content: str) -> str:
    """估算学习时间"""
    words = len(content.split())
    # 假设阅读速度: 200词/分钟
    minutes = max(10, words // 200)

    if minutes <= 15:
        return "10-15分钟"
    elif minutes <= 25:
        return "15-25分钟"
    elif minutes <= 40:
        return "25-40分钟"
    else:
        return "40-60分钟"

def assign_to_module(lesson: Dict) -> str:
    """根据课程内容分配到合适的模块"""
    title = lesson['title'].lower()
    content = lesson['content'].lower()
    num = int(lesson['number'])

    # Module 0: 入门课程 (000-004)
    if num <= 4:
        return "0"

    # Module 4: 电子公证 (特定课程)
    if "electronic" in title:
        return "4"

    # Module 5: 房地产
    if any(kw in title or kw in content for kw in ["real property", "deed", "mortgage", "conveyance"]):
        return "5"

    # Module 7: 违规与处罚
    if any(kw in title for kw in ["violation", "penalty", "criminal", "misdemeanor", "removal"]):
        return "7"

    # Module 8: 印章、记录、证书
    if any(kw in title for kw in ["seal", "certificate", "stamp", "signature", "journal"]):
        return "8"

    # Module 9: 定义和术语
    if "definition" in title.lower() or num >= 100:
        return "9"

    # Module 3: 公证操作
    if any(kw in title for kw in ["acknowledgment", "oath", "affirmation", "jurat", "affidavit"]):
        return "3"

    # Module 2: 任命流程
    if any(kw in title for kw in ["§13", "appointment", "commission", "qualification", "application"]):
        if num <= 20:
            return "2"

    # Module 6: 限制与合规
    if any(kw in title or kw in content for kw in ["advertising", "misconduct", "prohibition"]):
        return "6"

    # Module 1: 基础知识 (前30课中的剩余)
    if num <= 30:
        return "1"

    # 其他按内容关键词分配
    for module in MODULES[3:]:  # 从Module 3开始检查
        module_keywords = module.get('keywords', [])
        if any(kw in title or kw in content for kw in module_keywords):
            return module['module_id']

    # 默认分配到Module 9 (进阶专题)
    return "9"

def extract_key_concepts(content: str, limit: int = 5) -> List[str]:
    """从内容中提取关键概念（§符号标记的法律条款）"""
    concepts = []

    # 提取 §xxx 格式的法律条款
    section_refs = re.findall(r'§\s*\d+[a-z]*(?:-[a-z])?', content)
    concepts.extend(list(set(section_refs))[:3])

    # 提取引用的案例
    case_refs = re.findall(r'Matter of \w+|People v\. \w+|\w+ v\. \w+', content)
    concepts.extend(list(set(case_refs))[:2])

    return concepts[:limit]

def create_lesson_object(lesson: Dict, module_id: str) -> Dict:
    """创建课程对象"""
    number = lesson['number']

    return {
        "lesson_id": f"{module_id}.{number}",
        "original_number": number,
        "module_id": module_id,
        "title": lesson['title'],
        "difficulty": estimate_difficulty(int(number), lesson['title'], lesson['content']),
        "estimated_time": estimate_time(lesson['content']),
        "prerequisites": [],  # 待在P1-3中填充

        "learning_objectives": [
            f"理解{lesson['title']}的核心概念",
            f"掌握{lesson['title']}的法律要求",
            f"能够应用{lesson['title']}的相关规定"
        ],

        "key_concepts": extract_key_concepts(lesson['content']),

        "content": {
            "raw": lesson['content'],
            "word_count": len(lesson['content'].split()),
            "char_count": len(lesson['content'])
        },

        "assessments": {
            "pre_quiz": [],     # 待在P2-1中填充
            "practice_questions": [],  # 待在P2-1中填充
            "post_quiz": []     # 待在P2-1中填充
        },

        "related_lessons": [],  # 待在P1-3中填充
        "additional_resources": [],

        "metadata": {
            "created": "2025-11-08",
            "version": "1.0",
            "status": "active"
        }
    }

def create_module_structure(lessons: List[Dict]) -> Dict:
    """创建完整的模块结构"""
    structure = {
        "course_info": {
            "title": "纽约州公证人培训课程 (New York Notary Public Training)",
            "version": "2.0",
            "total_modules": 10,
            "total_lessons": len(lessons),
            "created": "2025-11-08",
            "description": "基于NYS Department of State官方文档的系统化公证人培训课程"
        },
        "modules": []
    }

    # 为每个模块创建结构
    for module in MODULES:
        module_obj = {
            "module_id": module['module_id'],
            "title": module['title'],
            "difficulty": module['difficulty'],
            "description": module['description'],
            "lessons": [],
            "estimated_total_time": "待计算",
            "completion_criteria": "完成所有课程并通过测试"
        }

        # 分配课程到模块
        for lesson in lessons:
            assigned_module = assign_to_module(lesson)
            if assigned_module == module['module_id']:
                lesson_obj = create_lesson_object(lesson, module['module_id'])
                module_obj['lessons'].append(lesson_obj)

        # 计算总时间
        if module_obj['lessons']:
            total_minutes = sum([
                int(lesson['estimated_time'].split('-')[0])
                for lesson in module_obj['lessons']
            ])
            hours = total_minutes // 60
            minutes = total_minutes % 60
            module_obj['estimated_total_time'] = f"{hours}小时{minutes}分钟"

        structure['modules'].append(module_obj)

    return structure

def generate_statistics(structure: Dict) -> Dict:
    """生成统计信息"""
    stats = {
        "total_modules": len(structure['modules']),
        "total_lessons": 0,
        "lessons_by_module": {},
        "difficulty_distribution": {
            "⭐": 0,
            "⭐⭐": 0,
            "⭐⭐⭐": 0,
            "⭐⭐⭐⭐": 0,
            "⭐⭐⭐⭐⭐": 0
        }
    }

    for module in structure['modules']:
        module_id = module['module_id']
        lesson_count = len(module['lessons'])
        stats['total_lessons'] += lesson_count
        stats['lessons_by_module'][f"Module {module_id}"] = lesson_count

        for lesson in module['lessons']:
            stats['difficulty_distribution'][lesson['difficulty']] += 1

    return stats

def main():
    """主函数"""
    print("=" * 70)
    print("  P1-1: 创建模块化JSON结构")
    print("  将121个课程组织成10个模块")
    print("=" * 70)

    csv_file = '/home/user/AI-notary/lessons.csv'
    output_file = '/home/user/AI-notary/course_structure.json'
    stats_file = '/home/user/AI-notary/course_statistics.json'

    # 读取课程
    print("\n📖 读取课程数据...")
    lessons = read_lessons(csv_file)
    print(f"✅ 成功读取 {len(lessons)} 个课程")

    # 创建模块结构
    print("\n🏗️  创建模块结构...")
    structure = create_module_structure(lessons)

    # 生成统计
    print("\n📊 生成统计信息...")
    stats = generate_statistics(structure)

    # 输出结果
    print("\n💾 保存JSON文件...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"✅ 主结构已保存: {output_file}")

    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ 统计信息已保存: {stats_file}")

    # 显示统计
    print("\n" + "=" * 70)
    print("📊 课程分布统计")
    print("=" * 70)
    for module_name, count in stats['lessons_by_module'].items():
        print(f"  {module_name}: {count} 个课程")

    print(f"\n  总计: {stats['total_lessons']} 个课程")

    print("\n" + "=" * 70)
    print("📈 难度分布")
    print("=" * 70)
    for difficulty, count in stats['difficulty_distribution'].items():
        print(f"  {difficulty}: {count} 个课程")

    print("\n" + "=" * 70)
    print("✅ P1-1任务完成！")
    print("   下一步: P1-2 为每课添加学习目标和关键概念")
    print("=" * 70)

if __name__ == '__main__':
    main()
