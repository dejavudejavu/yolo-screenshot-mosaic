@echo off
echo Starting YOLO Image Mosaic Tool...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM 启动Flask服务器
echo.
echo Starting Flask server on http://localhost:5000
echo Open index.html in your browser to use the tool
echo.
python app.py

pause

