# 🎯 AI-Notary 课程数据改进计划

**制定日期**: 2025-11-07
**目标**: 将教学适配度从33.4%提升至65-70%
**预计周期**: 2周
**总工作量**: 约20-25小时

---

## 📊 当前状态

| 指标 | 现状 | 目标 | 差距 |
|------|------|------|------|
| 技术质量 | 9.0/10 | 9.0/10 | ✓ 已达标 |
| 数据质量 | 8.9/10 | 9.0/10 | 接近目标 |
| 教学适配度 | 33.4% | 65-70% | +32-37个百分点 |
| 案例覆盖率 | 16.5% | 50%+ | +34个百分点 |
| 结构化率 | 33.1% | 60%+ | +27个百分点 |

---

## 🎯 改进目标

### 总体目标
在2周内将教学适配度提升至**65-70%**，使课程数据更好地支持AI教学系统。

### 具体目标

1. **案例覆盖率**: 16.5% → 50%+ (至少60个课程)
2. **结构化率**: 33.1% → 60%+ (至少72个课程)
3. **内容充足度**: 80.2% → 95%+ (至少115个课程)
4. **术语定义完整性**: 57% → 90%+ (术语类课程)

---

## 📅 三阶段实施计划

### 🔥 阶段一：立即修复（Day 1，2小时）

**优先级**: ⚡⚡⚡ 紧急
**目标**: 快速提升20-30%，无需大量数据修改
**预期提升**: 33.4% → 50-55%

#### Task 1.1: 优化 prompt_template.txt ⭐⭐⭐

**工作量**: 10分钟
**负责人**: 技术团队
**执行步骤**:

1. 备份当前模板
   ```bash
   cp prompt_template.txt prompt_template.txt.backup
   ```

2. 修改 `prompt_template.txt` 为：

```txt
You are an experienced and articulate AI instructor specializing in notary public training.

Your task is to create a comprehensive, easy-to-understand lesson explanation based on the provided content.

Lesson ID: {id}
Lesson Title: {title}
Lesson Content: {content}

Instructions for your explanation:

1. STRUCTURE & CLARITY
   - Begin with a brief overview (2-3 sentences)
   - Break down complex concepts into clear, logical steps
   - Use headings and bullet points for readability
   - Conclude with key takeaways

2. REAL-WORLD APPLICATION (REQUIRED)
   - If the content includes examples, expand on them
   - If no examples are provided, CREATE realistic scenarios based on:
     * Common notary public situations
     * Typical legal scenarios notaries encounter
     * Practical workplace applications
   - Make examples specific and actionable

3. PRACTICAL GUIDANCE
   - Explain WHY this matters to notary public practice
   - Highlight what notaries MUST do vs MUST NOT do
   - Include potential consequences of errors
   - Mention common mistakes to avoid (if applicable)

4. DEPTH APPROPRIATE TO CONTENT
   - Brief definitions: 200-300 word explanation
   - Legal provisions: 400-600 word explanation
   - Complex procedures: 600-800 word explanation
   - Always prioritize clarity over length

5. PROFESSIONAL TONE
   - Use clear, professional language
   - Avoid legal jargon unless necessary (then explain it)
   - Write as if teaching a new notary public
   - Be encouraging while being thorough

Your output should be well-structured, practical, and immediately useful for someone learning to be a notary public.
```

3. 测试改进效果
   ```bash
   # 测试3-5个不同类型的课程
   # 验证AI生成的解释质量
   ```

**验收标准**:
- ✓ AI生成的解释包含案例（即使原内容没有）
- ✓ 结构清晰，有标题和要点
- ✓ 长度适中（200-800字符根据内容）

**预期效果**: 立即提升20-30%教学质量

---

#### Task 1.2: 创建改进跟踪系统

**工作量**: 30分钟

创建 `improvement_tracker.csv`:

```csv
LessonNo,CurrentLength,HasExample,IsStructured,Priority,Status,AssignedTo,CompletedDate
001,4500,No,Yes,Medium,Pending,,
002,4039,No,No,High,Pending,,
...
```

**执行命令**:
```python
# 自动生成跟踪表
python3 scripts/generate_tracker.py
```

---

#### Task 1.3: 建立质量检查脚本

**工作量**: 1小时

创建 `scripts/quality_check.py`:

```python
#!/usr/bin/env python3
"""
课程质量自动检查脚本
检查: 长度、结构、案例、法律引用等
"""

import csv
import re

def check_lesson_quality(lesson):
    score = 0
    issues = []

    # 检查长度
    length = len(lesson['Content'])
    if length < 200:
        issues.append("内容过短")
    elif length >= 300:
        score += 20

    # 检查结构
    if lesson['Content'].count('\n\n') >= 2:
        score += 20
    else:
        issues.append("缺少段落结构")

    # 检查案例
    if re.search(r'example|for instance|scenario|case|matter of',
                 lesson['Content'], re.I):
        score += 30
    else:
        issues.append("缺少案例")

    # 检查专业性
    if re.search(r'§\d+|Executive Law|Real Property Law',
                 lesson['Content']):
        score += 15

    # 检查实用性
    if re.search(r'notary|must|shall|important|note',
                 lesson['Content'], re.I):
        score += 15

    return score, issues

# 运行检查并生成报告
```

---

### 🔧 阶段二：快速提升（Day 2-7，12小时）

**优先级**: ⚡⚡ 高
**目标**: 扩充最需要改进的课程
**预期提升**: 50-55% → 65%

#### Task 2.1: 扩充25个最短术语定义 ⭐⭐⭐

**工作量**: 5-6小时
**目标课程**: Lessons 064-121中<300字符的25个

**执行清单**:

| No | Title | 当前长度 | 目标长度 | 状态 |
|----|-------|---------|---------|------|
| 099 | Lien | 105 | 350+ | ⬜ |
| 092 | Ex Parte | 110 | 350+ | ⬜ |
| 114 | Subordination Clause | 112 | 350+ | ⬜ |
| 095 | Judgment | 116 | 350+ | ⬜ |
| 121 | Note | 102 | 350+ | ⬜ |
| 073 | Apostile | 128 | 350+ | ⬜ |
| 080 | Chattel Paper | 157 | 350+ | ⬜ |
| 082 | Consideration | 115 | 350+ | ⬜ |
| 084 | Contract | 133 | 350+ | ⬜ |
| 085 | Conveyance | 119 | 350+ | ⬜ |
| 087 | Deponent | 136 | 350+ | ⬜ |
| 088 | Deposition | 185 | 350+ | ⬜ |
| 090 | Escrow | 163 | 350+ | ⬜ |
| 098 | Lease | 143 | 350+ | ⬜ |
| 102 | Mortgage | 132 | 350+ | ⬜ |
| 107 | Proof | 149 | 350+ | ⬜ |
| 108 | Protest | 146 | 350+ | ⬜ |
| 112 | Statute of Frauds | 132 | 350+ | ⬜ |
| 115 | Sunday | 115 | 350+ | ⬜ |
| 074 | Attest | 103 | 350+ | ⬜ |
| 075 | Attestation Clause | 147 | 350+ | ⬜ |
| 078 | Certified Copy | 264 | 350+ | ⬜ |
| 118 | Venue | 238 | 350+ | ⬜ |
| 076 | Authentication | 133 | 350+ | ⬜ |
| 086 | County Clerk Certificate | 133 | 350+ | ⬜ |

**扩充模板**:

```markdown
[原始定义]

**在公证实践中的应用**:
公证员在以下情况会遇到[术语]:
- [场景1]
- [场景2]
- [场景3]

**实例**:
[具体案例说明该术语如何在实际工作中使用]

**重要提示**:
[该术语对公证员的重要性、注意事项]
```

**示例 - Lesson 099 (Lien)**:

```
当前 (105字符):
A legal right or claim upon a specific property which attaches
to the property until a debt is satisfied.

改进后 (380字符):
A legal right or claim upon a specific property which attaches
to the property until a debt is satisfied.

在公证实践中的应用:
公证员在以下情况会遇到留置权(Lien):
- 公证带有现有留置权的房产契约
- 处理创建留置权的抵押文件
- 认证承包商提交的机械留置权(mechanic's lien)

实例:
房主为房屋再融资。旧抵押贷款在房产上创建了留置权。公证员必须确保
在记录新抵押留置权之前，有适当的文件来解除旧留置权。留置权的顺序
和优先级对产权清晰至关重要。

重要提示:
公证员虽然不决定留置权的有效性，但必须准确记录和认证涉及留置权的
文件。不当处理可能导致产权纠纷。
```

**执行脚本**:

```python
# scripts/expand_terms.py
import csv

terms_to_expand = {
    '099': {
        'title': 'Lien',
        'addition': '''
在公证实践中的应用:
公证员在以下情况会遇到留置权(Lien):
- 公证带有现有留置权的房产契约
- 处理创建留置权的抵押文件
- 认证承包商提交的机械留置权(mechanic's lien)

实例:
房主为房屋再融资。旧抵押贷款在房产上创建了留置权。公证员必须确保
在记录新抵押留置权之前，有适当的文件来解除旧留置权。留置权的顺序
和优先级对产权清晰至关重要。

重要提示:
公证员虽然不决定留置权的有效性，但必须准确记录和认证涉及留置权的
文件。不当处理可能导致产权纠纷。
'''
    },
    # ... 其他24个术语
}

# 批量更新
```

**验收标准**:
- ✓ 每个术语≥350字符
- ✓ 包含"在公证实践中的应用"部分
- ✓ 包含实例
- ✓ 包含重要提示

---

#### Task 2.2: 为前30个课程添加案例段落 ⭐⭐

**工作量**: 6-7小时
**目标课程**: Lessons 001-030

**执行清单**:

| No | Title | 有案例 | 优先级 | 状态 |
|----|-------|--------|--------|------|
| 001 | Professional Conduct | 是 | Low | ⬜ |
| 002 | §130. Appointment | 否 | High | ⬜ |
| 003 | §131. Procedure | 否 | High | ⬜ |
| 004 | §132. Certificates | 否 | High | ⬜ |
| 005 | §133. Certification | 否 | High | ⬜ |
| 006 | §140. Executive Law | 否 | Medium | ⬜ |
| 007 | §3-200 Election Law | 否 | Medium | ⬜ |
| 008 | §3. Public Officers | 否 | Medium | ⬜ |
| 009 | §534. County Law | 否 | Medium | ⬜ |
| 010 | Member of legislature | 否 | Low | ⬜ |
| 011 | Sheriffs | 否 | Medium | ⬜ |
| 012 | Notary disqualifications | 否 | High | ⬜ |
| 013 | §134. Signature | 否 | High | ⬜ |
| 014 | §135. Powers | 否 | High | ⬜ |
| 015 | §135-a. Acting without | 否 | High | ⬜ |
| 016 | §135-b. Advertising | 否 | High | ⬜ |
| 017 | §135-c. Electronic | 是 | Low | ⬜ |
| 018 | §136. Notarial fees | 否 | Medium | ⬜ |
| 019 | §137. Statement | 否 | High | ⬜ |
| 020 | §138. Powers of notaries | 否 | High | ⬜ |
| 021-030 | ... | 否 | High | ⬜ |

**案例添加模板**:

```markdown
[原始内容]

---

**实际应用场景**:

**场景**: [描述一个真实的公证情况]

**正确做法**:
- [步骤1]
- [步骤2]
- [步骤3]

**错误示例**: [常见错误]

**重要提醒**: [关键注意事项]
```

**示例 - Lesson 012 (Notary disqualifications)**:

```markdown
[原始内容保持不变]

---

**实际应用场景**:

**场景1: 家庭成员的文件**
张女士是一名公证员。她的女儿要购买房产，需要公证抵押文件。
张女士能为女儿公证吗？

**正确做法**:
- 张女士必须拒绝，因为她在交易中有直接利益关系（女儿）
- 建议女儿找另一位公证员
- 记录拒绝的原因，保护自己

**错误示例**:
公证员为配偶、子女、父母等直系亲属公证文件。这种公证在法律上
无效，且公证员可能面临纪律处分或吊销执照。

**场景2: 担任公司董事的公证员**
李先生既是ABC公司的董事，又是公证员。公司CEO需要签署一份
公司贷款文件并需要公证。

**正确做法**:
- 李先生可以为CEO的签名做公证（§138允许）
- 但李先生不能作为签署人同时担任公证员
- 必须确保自己不是文件的当事方

**重要提醒**:
利益冲突是公证员最常见的违规原因之一。原则是：如果你在交易中
有任何财务或个人利益，必须回避。疑义时应咨询法律顾问。
```

**验收标准**:
- ✓ 至少2个实际场景
- ✓ 明确正确做法和错误示例
- ✓ 包含重要提醒
- ✓ 案例与课程内容直接相关

---

### 📈 阶段三：系统优化（Day 8-14，8-10小时）

**优先级**: ⚡ 中
**目标**: 全面优化课程结构
**预期提升**: 65% → 70%+

#### Task 3.1: 批量优化课程结构

**工作量**: 6-7小时
**目标**: 为剩余60个课程添加结构化元素

**执行方法**:

1. **分类处理**:
   - 法律条文类(011-040): 添加"关键要点"和"实践影响"
   - 程序类(041-063): 添加"步骤指南"和"常见错误"
   - 其他术语(064-121): 已在Task 2.1处理

2. **自动化辅助**:

```python
# scripts/add_structure.py

def add_structure_to_legal(content):
    """为法律条文类添加结构"""
    return f"""
{content}

## 关键要点
- [从内容中提取3-5个要点]

## 对公证员的实践影响
[说明这条法律如何影响日常公证工作]
"""

def add_structure_to_procedure(content):
    """为程序类添加结构"""
    return f"""
{content}

## 操作步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 常见错误
- ❌ [错误1]
- ❌ [错误2]
- ✓ [正确做法]
"""
```

**批量执行清单**:

| 范围 | 数量 | 优先级 | 负责人 | 状态 |
|------|------|--------|--------|------|
| 法律框架 011-020 | 10 | High | | ⬜ |
| 法律框架 021-030 | 10 | High | | ⬜ |
| 法律框架 031-040 | 10 | Medium | | ⬜ |
| 程序类 041-050 | 10 | High | | ⬜ |
| 程序类 051-063 | 13 | Medium | | ⬜ |

---

#### Task 3.2: 创建课程交叉引用

**工作量**: 2-3小时

**目标**: 建立课程之间的知识连接

**执行步骤**:

1. 识别相关课程对:
   ```python
   # scripts/find_related.py

   related_lessons = {
       '001': ['012', '014', '015'],  # Professional Conduct相关
       '012': ['001', '020', '038'],  # Disqualifications相关
       '064': ['065', '071'],  # Acknowledgment相关
       # ...
   }
   ```

2. 在课程末尾添加"相关课程":
   ```markdown
   ---

   **相关课程**:
   - Lesson 012: Notary disqualifications
   - Lesson 020: Powers of notaries
   - Lesson 038: Stockholders
   ```

**验收标准**:
- ✓ 至少50个课程有交叉引用
- ✓ 引用准确、相关
- ✓ 有助于学习路径引导

---

#### Task 3.3: 质量验证与修订

**工作量**: 2-3小时

**执行步骤**:

1. **运行质量检查脚本**:
   ```bash
   python3 scripts/quality_check.py > quality_report.txt
   ```

2. **生成改进对比报告**:
   ```bash
   python3 scripts/compare_versions.py \
     --before lessons.csv.before \
     --after lessons.csv \
     --output improvement_report.md
   ```

3. **手工抽查**: 随机检查10-15个课程

4. **修复问题**: 根据检查结果调整

**验收标准**:
- ✓ 所有课程通过质量检查
- ✓ 教学适配度≥65%
- ✓ 无明显错误或不一致

---

## 📋 执行时间表

### Week 1

| 日期 | 任务 | 工作量 | 负责人 |
|------|------|--------|--------|
| Day 1 (周一) | Task 1.1: 优化模板 | 10分钟 | ⬜ |
| Day 1 (周一) | Task 1.2: 创建跟踪系统 | 30分钟 | ⬜ |
| Day 1 (周一) | Task 1.3: 质量检查脚本 | 1小时 | ⬜ |
| Day 2-3 (周二-三) | Task 2.1: 扩充术语(1-12) | 3小时 | ⬜ |
| Day 4-5 (周四-五) | Task 2.1: 扩充术语(13-25) | 3小时 | ⬜ |
| Day 5-7 (周五-日) | Task 2.2: 添加案例(001-015) | 3-4小时 | ⬜ |

### Week 2

| 日期 | 任务 | 工作量 | 负责人 |
|------|------|--------|--------|
| Day 8-9 (周一-二) | Task 2.2: 添加案例(016-030) | 3-4小时 | ⬜ |
| Day 10-11 (周三-四) | Task 3.1: 优化结构(011-040) | 3-4小时 | ⬜ |
| Day 12-13 (周五-六) | Task 3.1: 优化结构(041-063) | 3小时 | ⬜ |
| Day 13 (周六) | Task 3.2: 交叉引用 | 2小时 | ⬜ |
| Day 14 (周日) | Task 3.3: 质量验证 | 2-3小时 | ⬜ |

---

## ✅ 验收标准

### 定量指标

| 指标 | 当前 | 目标 | 验收方法 |
|------|------|------|----------|
| 教学适配度 | 33.4% | ≥65% | 运行评估脚本 |
| 案例覆盖率 | 16.5% | ≥50% | 检查是否包含案例关键词 |
| 结构化率 | 33.1% | ≥60% | 检查段落和小标题 |
| 内容充足度 | 80.2% | ≥95% | 检查字符数 |
| 术语完整性 | 57% | ≥90% | 检查术语类课程长度 |

### 定性指标

- ✓ AI生成的解释清晰、结构化
- ✓ 包含实际案例和应用场景
- ✓ 适合初学者理解
- ✓ 专业准确，无法律错误
- ✓ 课程之间有逻辑连接

### 验收流程

1. **自动检查** (Day 14上午):
   ```bash
   python3 scripts/final_quality_check.py
   ```

2. **人工抽查** (Day 14下午):
   - 随机抽取20个课程
   - 验证案例准确性
   - 检查结构合理性

3. **生成最终报告**:
   ```bash
   python3 scripts/generate_final_report.py \
     --output IMPROVEMENT_FINAL_REPORT.md
   ```

4. **用户测试** (可选):
   - 让3-5名测试用户试用
   - 收集反馈
   - 微调

---

## 🛠️ 工具与脚本

### 需要创建的脚本

1. **scripts/generate_tracker.py** - 生成改进跟踪表
2. **scripts/quality_check.py** - 质量自动检查
3. **scripts/expand_terms.py** - 批量扩充术语
4. **scripts/add_structure.py** - 添加结构化元素
5. **scripts/find_related.py** - 识别相关课程
6. **scripts/compare_versions.py** - 对比前后版本
7. **scripts/final_quality_check.py** - 最终质量检查
8. **scripts/generate_final_report.py** - 生成最终报告

### 辅助工具

- **improvement_tracker.csv** - 进度跟踪表
- **quality_report.txt** - 质量检查报告
- **improvement_report.md** - 改进对比报告
- **IMPROVEMENT_FINAL_REPORT.md** - 最终成果报告

---

## 📊 预期成果

### 改进前后对比

| 维度 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 教学适配度 | 33.4% | 65-70% | +96-110% |
| 案例覆盖率 | 16.5% (20课程) | 50%+ (60+课程) | +200%+ |
| 结构化率 | 33.1% (40课程) | 60%+ (72+课程) | +80%+ |
| 内容充足度 | 80.2% (97课程) | 95%+ (115+课程) | +18%+ |
| 平均课程长度 | 907字符 | 1100+字符 | +21%+ |

### 具体改进

- ✅ **25个术语定义**扩充至350+字符，包含应用场景和案例
- ✅ **30个核心课程**添加实际应用场景和正确/错误示例
- ✅ **60个课程**优化结构，添加小标题和要点
- ✅ **50+个课程**建立交叉引用，形成知识网络
- ✅ **prompt模板**优化，AI生成质量显著提升

### 用户体验提升

- 📚 学生能更容易理解抽象法律概念
- 🎯 通过案例学习实际应用
- 🔗 通过交叉引用建立系统知识
- ⚡ AI生成的解释更结构化、更实用
- ✓ 整体学习效果提升50%+

---

## 🚨 风险与应对

### 风险识别

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 时间不足 | 中 | 高 | 优先完成Task 1.1和2.1 |
| 内容错误 | 低 | 高 | 专家审核，保留原文 |
| 案例不真实 | 中 | 中 | 参考真实判例 |
| 技术问题 | 低 | 中 | 充分测试脚本 |
| 人力不足 | 高 | 高 | 可分阶段执行 |

### 应急方案

**如果时间不足**:
1. 优先执行Task 1.1（模板优化）- 最高ROI
2. 执行Task 2.1前12个术语
3. 执行Task 2.2前15个课程
4. 其余留待下一阶段

**如果质量不达标**:
1. 回退到备份版本
2. 专家审核问题部分
3. 调整改进策略

---

## 📝 执行检查清单

### 阶段一检查清单

- [ ] prompt_template.txt 已备份
- [ ] prompt_template.txt 已更新
- [ ] 测试3-5个课程生成效果
- [ ] improvement_tracker.csv 已创建
- [ ] quality_check.py 已创建并测试
- [ ] 质量基线报告已生成

### 阶段二检查清单

**术语扩充**:
- [ ] Lesson 099-114 (15个) 已完成
- [ ] Lesson 073-090 (10个) 已完成
- [ ] 质量检查通过
- [ ] 每个术语≥350字符

**案例添加**:
- [ ] Lesson 001-015 已完成
- [ ] Lesson 016-030 已完成
- [ ] 每个课程至少2个场景
- [ ] 包含正确做法和错误示例

### 阶段三检查清单

- [ ] 法律框架类(011-040) 结构优化完成
- [ ] 程序类(041-063) 结构优化完成
- [ ] 50+课程交叉引用已添加
- [ ] 最终质量检查通过
- [ ] 对比报告已生成
- [ ] 教学适配度≥65%

---

## 📈 监控与报告

### 日常监控

**每日**:
- 更新 improvement_tracker.csv
- 记录完成的课程数
- 记录遇到的问题

**每3天**:
- 运行 quality_check.py
- 生成进度报告
- 调整计划（如需要）

### 里程碑报告

**Week 1结束**:
```markdown
## Week 1 Progress Report

### 完成情况
- 模板优化: ✓
- 术语扩充: 25/25 (100%)
- 案例添加: 15/30 (50%)

### 质量指标
- 教学适配度: 33.4% → 50%
- 案例覆盖率: 16.5% → 35%

### 下周计划
- 完成剩余15个案例
- 开始结构优化
```

**Week 2结束**:
```markdown
## Final Report

### 总体完成情况
- 所有任务完成: ✓/✗
- 教学适配度: XX%
- 质量提升: +XX%

### 主要成果
- [列出关键成果]

### 遗留问题
- [列出未解决的问题]

### 后续建议
- [下一阶段改进建议]
```

---

## 🎯 后续改进方向

完成本次2周改进计划后，建议的后续方向：

### Phase 2 (1-2个月)

1. **深度案例开发**
   - 为每个课程开发3-5个深度案例
   - 建立案例库
   - 添加案例分析和讨论

2. **多媒体增强**
   - 添加流程图文字描述
   - 创建检查清单
   - 开发模拟场景

3. **评估体系完善**
   - 为每个课程设计测验题
   - 创建综合评估
   - 建立能力模型

### Phase 3 (3-6个月)

1. **智能个性化**
   - 根据学习进度推荐课程
   - 识别薄弱环节
   - 自适应难度

2. **社区内容**
   - 收集真实案例
   - 用户贡献内容
   - 专家问答

---

## 📞 支持与资源

### 技术支持
- AI API: OpenAI/DeepSeek
- Python 3.8+
- Git版本控制

### 参考资料
- 纽约州公证员手册
- 相关法律条文
- 真实判例库

### 联系方式
- 项目负责人: [待填写]
- 技术支持: [待填写]
- 内容审核: [待填写]

---

**计划制定**: 2025-11-07
**计划批准**: [待批准]
**开始执行**: [待确定]
**预计完成**: [开始日期+14天]

---

## 附录：命令快速参考

```bash
# 备份当前数据
cp lessons.csv lessons.csv.before_improvement

# 生成跟踪表
python3 scripts/generate_tracker.py

# 运行质量检查
python3 scripts/quality_check.py > quality_report.txt

# 扩充术语
python3 scripts/expand_terms.py --lessons 099,092,114 --output lessons.csv

# 添加案例
python3 scripts/add_examples.py --range 001-030 --output lessons.csv

# 优化结构
python3 scripts/add_structure.py --category legal --range 011-040

# 最终检查
python3 scripts/final_quality_check.py --threshold 65

# 生成报告
python3 scripts/generate_final_report.py --output IMPROVEMENT_FINAL_REPORT.md

# 提交Git
git add lessons.csv IMPROVEMENT_FINAL_REPORT.md
git commit -m "Complete 2-week improvement plan"
git push
```
