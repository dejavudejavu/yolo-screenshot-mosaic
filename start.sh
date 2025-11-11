#!/bin/bash

echo "Starting YOLO Image Mosaic Tool..."
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# 检查依赖是否安装
echo "Checking dependencies..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# 启动Flask服务器
echo ""
echo "Starting Flask server on http://localhost:5000"
echo "Open index.html in your browser to use the tool"
echo ""
python3 app.py

