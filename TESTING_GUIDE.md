# 🧪 AI-Notary 项目测试指南

**版本**: v1.1 (优化版)
**测试日期**: 2025-11-06
**适用系统**: Windows / macOS / Linux

---

## 📋 测试前准备

### 第一步：获取项目文件

#### Windows 用户

```powershell
# 打开 PowerShell 或命令提示符

# 1. 进入桌面
cd C:\Users\你的用户名\Desktop

# 2. 克隆项目（如果还没有）
git clone https://github.com/Tommyz123/AI-notary.git
cd AI-notary

# 3. 切换到优化分支
git checkout claude/project-overview-intro-011CUs8GkBAvUgT22Qgzt3FC

# 4. 拉取最新代码
git pull origin claude/project-overview-intro-011CUs8GkBAvUgT22Qgzt3FC

# 5. 确认文件存在
dir app.py
# 应该显示文件信息，如果显示"找不到文件"则有问题
```

#### 如果没有安装 Git

**选项A: 安装 Git**
- 访问：https://git-scm.com/download/win
- 下载并安装
- 重启命令行，再执行上述步骤

**选项B: 直接下载 ZIP**
1. 访问：https://github.com/Tommyz123/AI-notary
2. 点击绿色按钮 "Code" → "Download ZIP"
3. 解压到桌面
4. 重命名文件夹为 `AI-notary`

---

### 第二步：检查 Python 环境

```powershell
# 检查 Python 版本（需要 3.8+）
python --version

# 如果显示 Python 3.8 或更高版本，继续
# 如果没有 Python，访问 https://www.python.org/downloads/ 下载安装
```

---

### 第三步：安装依赖

```powershell
# 在项目目录中
cd C:\Users\你的用户名\Desktop\AI-notary

# 安装所需库
pip install -r requirements.txt

# 等待安装完成，应该看到：
# Successfully installed streamlit-x.x.x pandas-x.x.x ...
```

**如果遇到错误**：
```powershell
# 使用国内镜像源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 第四步：配置环境变量

```powershell
# 1. 创建 .env 文件
copy .env.example .env

# 2. 编辑 .env 文件
notepad .env

# 或者使用其他文本编辑器
# code .env  (如果你安装了 VS Code)
```

**在 .env 文件中配置**：

```bash
# 选择 API 提供商
API_PROVIDER=openai

# 如果使用 OpenAI
OPENAI_API_KEY=sk-你的密钥在这里
OPENAI_MODEL=gpt-3.5-turbo

# 或者使用 DeepSeek
# API_PROVIDER=deepseek
# DEEPSEEK_API_KEY=你的DeepSeek密钥
# DEEPSEEK_MODEL=deepseek-chat

# 其他设置（可选，使用默认值即可）
ENABLE_RESPONSE_CACHING=true
CACHE_DURATION_MINUTES=60
```

**保存文件** (Ctrl+S)

---

### 第五步：初始化数据库

```powershell
# 运行初始化脚本
python init_db.py

# 应该看到：
# 🚀 Initializing Notary Training System Database...
# ==================================================
# ✅ Database initialized successfully!
# ✅ Admin user created successfully!
#    Username: admin
#    Password: admin123
#    User ID: 1
# ✅ Imported XX lessons from CSV
# ==================================================
# 🎉 Setup completed!
```

**如果看到错误**，检查：
- lessons.csv 文件是否存在
- Python 版本是否正确

---

## 🚀 启动应用

```powershell
# 启动 Streamlit 应用
streamlit run app.py

# 应该看到：
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://xxx.xxx.xxx.xxx:8501
```

**自动打开浏览器**，如果没有，手动访问：http://localhost:8501

---

## ✅ 测试清单

### 基础功能测试

#### 1. 登录测试
- [ ] 打开应用，看到登录页面
- [ ] 输入用户名：`admin`
- [ ] 输入密码：`admin123`
- [ ] 点击 "Login"
- [ ] **预期结果**：成功登录，看到课程列表

---

### 新功能测试（v1.1 优化）

#### 2. 快速导航测试 ⭐ 新功能

**测试步骤**：
1. 登录后，查看页面顶部
2. 应该看到：
   ```
   ████████░░░░░░░░ 10%
   📚 Overall Progress: 1/10 lessons (10.0% complete)

   [⬅️ Previous] [📖 Jump to Lesson: ▼] [Next ➡️]
   ```

**测试项**：
- [ ] 点击 **Next ➡️** 按钮
  - **预期**：进入下一课，页面刷新很快
- [ ] 点击 **⬅️ Previous** 按钮
  - **预期**：返回上一课
- [ ] 在第一课时，Previous 按钮应该是灰色禁用状态
- [ ] 在最后一课时，Next 按钮应该是灰色禁用状态

**评分标准**：
- 导航速度快（< 1秒）✅
- 按钮状态正确 ✅
- 页面无闪烁 ✅

---

#### 3. 下拉选择器测试 ⭐ 新功能

**测试步骤**：
1. 点击中间的下拉菜单
2. 应该看到所有课程列表
3. 已完成的课程前面有 ✅ 标记

**测试项**：
- [ ] 下拉菜单显示所有课程
- [ ] 选择任意课程
  - **预期**：立即跳转到该课程
- [ ] 课程标题被截断（长标题显示 `...`）
- [ ] 完成的课程显示 ✅ 标记

---

#### 4. 进度条测试 ⭐ 新功能

**测试步骤**：
1. 观察页面顶部的进度条
2. 标记一个课程为完成
3. 查看进度条变化

**测试项**：
- [ ] 进度条显示正确的完成百分比
- [ ] 显示格式：`X/Y lessons (Z% complete)`
- [ ] 完成课程后，进度条增加
- [ ] 进度条颜色清晰可见

---

#### 5. 保存通知测试 ⭐ 新功能

**测试步骤**：
1. 点击 **📘 Mark as Completed** 按钮
2. 观察页面反馈

**测试项**：
- [ ] 立即看到绿色通知：`✅ Lesson 'XXX' marked as completed and saved!`
- [ ] 通知消息清晰易读
- [ ] 再次点击取消完成
  - **预期**：看到蓝色通知：`ℹ️ Lesson 'XXX' unmarked and saved!`

---

#### 6. 课程测验分页测试 ⭐⭐⭐ 核心新功能

**测试步骤**：
1. 在任意课程页面，滚动到测验部分
2. 观察测验的显示方式

**测试项**：
- [ ] 测验标题显示：`🧪 Quiz for This Lesson`
- [ ] 如果题目超过10题，显示页码信息：
  ```
  📄 Page 1 of 3 | Questions 1-10 of 25
  ✍️ Progress: 0/25 questions answered
  ```
- [ ] 只显示当前页的 10 道题（不是全部）
- [ ] 答题后，进度自动更新：`✍️ Progress: 5/25 questions answered`

**分页导航测试**：
- [ ] 看到底部导航栏：
  ```
  [⬅️ Prev Page] [Page 1 / 3] [⚠️ 10 unanswered] [Next Page ➡️]
  ```
- [ ] 点击 **Next Page ➡️**
  - **预期**：显示第 2 页的题目（11-20题）
- [ ] 点击 **⬅️ Prev Page**
  - **预期**：返回第 1 页
- [ ] 如果当前页有未答题，中间显示警告：`⚠️ X unanswered`

**提交按钮测试**：
- [ ] 在第 1 页时，看不到提交按钮
- [ ] 显示提示：`💡 Navigate to the last page to submit...`
- [ ] 导航到最后一页，看到 **✅ Submit Quiz** 按钮
- [ ] 如果有未答题，显示警告：`⚠️ X questions not answered yet...`
- [ ] 点击提交
  - **预期**：显示分数和详细结果

**结果展示测试**：
- [ ] 提交后显示：`🎉 Quiz Submitted!`
- [ ] 显示分数：`📊 Your Score: 8/10 (80.0%)`
- [ ] 点击 **📋 View Detailed Results** 展开
  - **预期**：看到所有题目的对错详情
  - ✅ 正确的题目显示绿色
  - ❌ 错误的题目显示红色，并显示正确答案和解释

---

#### 7. 最终考试分页测试 ⭐⭐⭐ 核心新功能

**测试步骤**：
1. 点击侧边栏的 **🏁 Final Test**
2. 等待生成 50 道题（可能需要 1-2 分钟）

**测试项**：
- [ ] 生成期间显示：`Generating 50 questions... This may take a minute.`
- [ ] 生成完成后，显示分页：
  ```
  📄 Page 1 of 5 | Questions 1-10 of 50
  ✍️ Progress: 0/50 questions answered
  ```
- [ ] 只显示 10 道题（不是全部 50 题）
- [ ] 导航功能与课程测验相同
- [ ] 在第 5 页（最后一页）显示提交按钮
- [ ] 提交后显示：
  - 总分：`🧾 Final Score: 42 / 50 (84.0%)`
  - 通过/失败消息（>= 40分通过）
  - 详细结果（可展开）
- [ ] 点击 **🔙 Back to Lessons** 返回

---

### 传统功能测试（确保没有破坏）

#### 8. AI 解释功能

**测试项**：
- [ ] 选择详细程度：Overview (fast) / Standard / In-depth
- [ ] 切换后，重新生成解释
- [ ] 解释长度符合预期：
  - Overview: ~220 词
  - Standard: ~600 词
  - In-depth: ~1200 词

---

#### 9. 逐点深入功能

**测试项**：
- [ ] 在解释下方看到：`🔎 Deep dive by point (optional)`
- [ ] 显示 3-8 个要点按钮：`Explain point 1`, `Explain point 2`...
- [ ] 点击任意按钮
  - **预期**：展开该要点的详细解释

---

#### 10. 问答功能

**测试项**：
- [ ] 在 `💬 Ask a Question` 输入框输入问题
- [ ] 点击 **Submit Question**
- [ ] 等待 AI 回答
- [ ] 答案基于当前课程内容

---

#### 11. 语音朗读功能

**测试项**：
- [ ] 点击 **🔈 Play Explanation** 按钮
- [ ] 浏览器开始朗读课程解释
- [ ] 点击 **🛑 Stop** 按钮
- [ ] 朗读停止

---

#### 12. 侧边栏功能

**测试项**：
- [ ] 侧边栏显示所有课程
- [ ] 已完成的课程显示 ✅
- [ ] 点击侧边栏课程可以跳转（传统方式）
- [ ] 详细程度下拉菜单正常工作
- [ ] **📊 My Analytics** 按钮可用
- [ ] **🏁 Final Test** 按钮可用
- [ ] 底部显示 API 提供商信息

---

## 📊 性能测试

### 响应速度测试

| 操作 | 预期时间 | 实际时间 | 通过 |
|------|---------|---------|------|
| 点击 Next/Previous | < 0.5秒 | _____ | [ ] |
| 下拉菜单跳转 | < 0.5秒 | _____ | [ ] |
| 测验翻页 | < 0.3秒 | _____ | [ ] |
| 标记完成 | < 0.5秒 | _____ | [ ] |
| AI 解释（缓存命中） | < 0.1秒 | _____ | [ ] |
| AI 解释（新请求） | 10-60秒 | _____ | [ ] |
| 测验生成 | 5-15秒 | _____ | [ ] |

---

## 🐛 常见问题排查

### 问题 1: 应用无法启动

**症状**：`streamlit: command not found` 或 `File does not exist: app.py`

**解决方案**：
```powershell
# 检查是否在正确目录
pwd  # 或 cd

# 应该在 AI-notary 目录
# 如果不是，cd 到正确目录

# 重新安装 streamlit
pip install streamlit

# 再次运行
streamlit run app.py
```

---

### 问题 2: 数据库错误

**症状**：`no such table: users` 或类似错误

**解决方案**：
```powershell
# 删除旧数据库（如果存在）
del notary_training.db

# 重新初始化
python init_db.py

# 再次运行应用
streamlit run app.py
```

---

### 问题 3: API 密钥错误

**症状**：`❌ Missing required API key` 或 `❌ Failed to generate explanation`

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 打开 `.env`，确认 API 密钥正确填写
3. 确认 `API_PROVIDER` 与密钥匹配
4. 保存后重启应用

---

### 问题 4: 导入错误

**症状**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```powershell
# 重新安装所有依赖
pip install -r requirements.txt --upgrade

# 如果还是不行，逐个安装
pip install streamlit pandas requests python-dotenv plotly urllib3
```

---

### 问题 5: 页面空白或显示异常

**解决方案**：
```powershell
# 清除 Streamlit 缓存
streamlit cache clear

# 重启应用
streamlit run app.py
```

---

## ✅ 测试通过标准

### 基础标准（必须全部通过）
- [ ] 应用可以正常启动
- [ ] 可以登录系统
- [ ] 可以查看课程内容
- [ ] AI 解释可以正常生成
- [ ] 测验可以正常显示和提交

### 优化功能标准（新功能）
- [ ] 快速导航按钮工作正常
- [ ] 进度条显示正确
- [ ] 下拉选择器可以跳转
- [ ] 保存通知即时显示
- [ ] 测验分页显示（10题/页）
- [ ] 最终考试分页显示

### 性能标准
- [ ] 导航响应 < 1秒
- [ ] 无明显卡顿
- [ ] 页面刷新流畅

### 用户体验标准
- [ ] 界面清晰易懂
- [ ] 操作逻辑合理
- [ ] 反馈及时明确
- [ ] 无混淆或误导

---

## 📝 测试报告模板

```
测试日期：_____________
测试人员：_____________
版本：v1.1

【基础功能】
✅ 登录：通过
✅ 课程浏览：通过
✅ AI 解释：通过
✅ 测验功能：通过

【新功能】
✅ 快速导航：通过
✅ 进度条：通过
✅ 下拉选择：通过
✅ 保存通知：通过
✅ 测验分页：通过
✅ 最终考试分页：通过

【性能】
✅ 导航速度：0.3秒
✅ 页面刷新：流畅
✅ AI 响应：正常

【问题】
□ 无问题
□ 发现问题：
  1. _______________
  2. _______________

【总体评价】
□ 优秀  □ 良好  □ 一般  □ 需改进

【建议】
___________________________________
___________________________________
```

---

## 🎓 测试技巧

### 快速测试（5分钟）
只测试核心新功能：
1. 快速导航（Next/Previous）
2. 测验分页
3. 保存通知

### 完整测试（30分钟）
按照测试清单逐项测试

### 压力测试
- 快速连续点击导航按钮
- 频繁切换详细程度
- 短时间内多次提交测验

---

## 🚀 测试后

### 如果一切正常
恭喜！你可以开始使用新版本学习了！

### 如果发现问题
1. 记录问题详情（截图+描述）
2. 查看上面的"常见问题排查"
3. 如果无法解决，联系开发者

---

## 📞 获取帮助

遇到问题？
1. 查看 `TROUBLESHOOTING.md`
2. 查看 `SETUP_GUIDE.md`
3. 提交 GitHub Issue

---

**祝测试顺利！🎉**
