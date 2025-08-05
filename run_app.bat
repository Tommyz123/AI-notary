@echo off
echo 【Notary 教学系统】启动中...
echo 正在检查依赖环境...

REM 创建虚拟环境（可选）
python -m venv venv
call venv\Scripts\activate

echo 正在安装依赖，请稍等...
pip install --upgrade pip
pip install streamlit pandas

echo 启动程序中...
streamlit run app.py

pause
