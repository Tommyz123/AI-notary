# 快速设置指南 / Quick Setup Guide

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
nano .env  # 或使用其他编辑器
```

**重要：** 至少需要配置以下内容：
- 选择 API 提供商：`API_PROVIDER=openai` 或 `API_PROVIDER=deepseek`
- 添加对应的 API 密钥

### 3. 初始化数据库
```bash
python init_db.py
```

这将：
- ✅ 创建数据库表结构
- ✅ 创建管理员账户 (admin/admin123)
- ✅ 从 CSV 导入课程数据

### 4. 启动应用
```bash
streamlit run app.py
```

### 5. 登录系统
- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **安全警告**: 首次登录后请立即更改默认密码！

---

## 📁 环境变量配置说明

编辑 `.env` 文件配置以下内容：

### API 配置（必需）
```bash
# 选择 API 提供商: "openai" 或 "deepseek"
API_PROVIDER=openai

# OpenAI 配置（如果使用 OpenAI）
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# 或 DeepSeek 配置（如果使用 DeepSeek）
DEEPSEEK_API_KEY=your-deepseek-key-here
DEEPSEEK_MODEL=deepseek-chat
```

### 性能优化（可选）
```bash
# 启用响应缓存以提高性能
ENABLE_RESPONSE_CACHING=true
CACHE_DURATION_MINUTES=60

# API 调用速率限制
RATE_LIMIT_PER_MINUTE=30
```

### 其他设置（可选）
```bash
# 应用名称
APP_NAME=Notary Training System

# 内容长度限制
MAX_CONTENT_LENGTH=12000

# AI 响应参数
DEFAULT_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=800
```

---

## ⚠️ 常见问题

### 问题 1: 找不到模块错误
```
ModuleNotFoundError: No module named 'dotenv'
```
**解决方案**: 运行 `pip install -r requirements.txt`

### 问题 2: 数据库错误
```
sqlite3.OperationalError: no such table: users
```
**解决方案**: 运行 `python init_db.py` 初始化数据库

### 问题 3: API 密钥错误
```
❌ Missing required API key
```
**解决方案**:
1. 确保创建了 `.env` 文件
2. 检查 API 密钥是否正确填写
3. 确认选择的 API 提供商与密钥匹配

### 问题 4: 无法连接 API
```
API call failed: timeout
```
**解决方案**:
1. 检查网络连接
2. 验证 API 密钥是否有效
3. 检查 API 服务状态

---

## 🔧 高级配置

### 使用 OpenAI 加速响应
```bash
# 运行配置脚本
python setup_openai.py
```

这将自动配置 OpenAI API 以获得更快的响应速度。

### 数据库迁移
如果从旧版本升级：
```bash
python migrate_data.py
```

### 检查数据库
```bash
python check_db.py
```

---

## 📊 功能测试

### 测试登录系统
```bash
python test_login.py
```

### 测试 API 连接
```bash
python ai_api.py
```

---

## 🔐 安全建议

1. **更改默认密码**
   - 首次登录后立即更改 admin 密码

2. **保护 .env 文件**
   - 不要提交 `.env` 到 Git
   - 不要分享包含真实密钥的 `.env`

3. **使用强密码**
   - 至少 6 个字符
   - 包含字母和数字
   - 建议包含特殊字符

4. **定期备份数据库**
   ```bash
   cp notary_training.db notary_training.db.backup
   ```

---

## 📝 项目结构

```
AI-notary/
├── app.py                    # 主应用入口
├── config.py                 # 配置管理
├── database.py               # 数据库操作
├── auth.py                   # 认证系统
├── ai_api.py                 # AI API 接口
├── init_db.py                # 数据库初始化
├── .env.example              # 环境变量模板
├── requirements.txt          # 依赖列表
├── lessons.csv               # 课程数据
└── README.md                 # 项目说明
```

---

## 🆘 获取帮助

如果遇到问题：
1. 查看 `TROUBLESHOOTING.md`
2. 查看 `SECURITY_AUDIT.md`
3. 在 GitHub 提交 Issue

---

## ✅ 设置完成检查清单

- [ ] 安装所有依赖
- [ ] 创建并配置 .env 文件
- [ ] 初始化数据库
- [ ] 成功启动应用
- [ ] 登录系统
- [ ] 更改默认密码
- [ ] 测试课程学习功能
- [ ] 测试测验功能

完成所有步骤后，你就可以开始使用系统了！🎉
