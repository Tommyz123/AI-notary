# 登录问题排查指南

## 问题诊断

已经完成了数据库初始化和用户创建。如果无法登录，请按以下步骤检查：

## 1. 确认数据库已正确初始化

运行数据库初始化脚本：
```bash
python3 init_db.py
```

应该看到：
```
✅ Database initialized successfully!
✅ Admin user created successfully!
   Username: admin
   Password: admin123
   User ID: 1
```

## 2. 测试数据库连接

运行测试脚本：
```bash
python3 test_login.py
```

应该看到：
```
✅ Authentication successful!
✅ Database module authentication successful!
```

## 3. 安装必要的Python包

如果要运行Streamlit应用，需要安装依赖：

### 使用pip安装：
```bash
pip install streamlit pandas python-dotenv plotly
```

### 或使用pip3：
```bash
pip3 install streamlit pandas python-dotenv plotly
```

### 或从requirements.txt安装：
```bash
pip install -r requirements.txt
```

## 4. 检查环境配置

确认.env文件存在且包含API密钥：
```bash
cat .env
```

应该包含：
```
DEEPSEEK_API_KEY=your_api_key_here
```

## 5. 运行应用

```bash
streamlit run app.py
```

## 6. 登录信息

- **用户名**: admin
- **密码**: admin123

## 常见问题解决

### 问题1: "ModuleNotFoundError: No module named 'streamlit'"
**解决**: 安装streamlit包
```bash
pip install streamlit
```

### 问题2: "No module named pip"
**解决**: 使用包管理器安装pip
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# CentOS/RHEL
sudo yum install python3-pip
```

### 问题3: 数据库文件不存在
**解决**: 重新运行初始化脚本
```bash
python3 init_db.py
```

### 问题4: API密钥错误
**解决**: 检查.env文件中的API密钥是否正确

### 问题5: 密码不匹配
**解决**: 重新创建管理员用户
```bash
# 删除现有数据库
rm notary_training.db
# 重新初始化
python3 init_db.py
```

## 验证步骤

1. ✅ 数据库文件存在: `notary_training.db`
2. ✅ 管理员用户已创建
3. ✅ 密码哈希正确匹配
4. ✅ 课程数据已导入 (121课程)
5. ⚠️ 需要安装Streamlit等依赖包

## 下一步

如果以上步骤都正确，但仍然无法登录，请：

1. 检查浏览器控制台是否有错误信息
2. 查看Streamlit应用的错误日志
3. 确认网络连接正常
4. 尝试使用不同的浏览器

## 联系支持

如果问题仍然存在，请提供：
- 错误信息的截图
- 运行`python3 test_login.py`的输出
- 操作系统版本
- Python版本 (`python3 --version`)