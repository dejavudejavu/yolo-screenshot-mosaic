# YOLO 图片打码工具

基于 YOLO 模型的图片自动打码工具，支持马赛克和图片遮挡两种方式。

## 功能特性

- 📤 图片上传（支持拖拽）
- 🎨 马赛克打码（可调节模糊程度）
- 🖼️ 图片遮挡（支持自定义遮挡图片）
- 🔍 实时预览效果
- 📥 结果下载

## 项目结构

```
yolo-pytorch-docker/
├── app.py              # Flask 后端 API
├── infer.py            # YOLO 推理和打码逻辑
├── index.html          # Vue 3 前端页面
├── requirements.txt    # Python 依赖
├── best.pt            # YOLO 模型文件
├── uploads/           # 上传文件目录（自动创建）
└── results/           # 结果文件目录（自动创建）
```

## 安装和运行

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 3. 打开前端页面

直接用浏览器打开 `index.html` 文件，或者使用本地服务器：

```bash
# 使用 Python 简单服务器
python -m http.server 8000

# 然后访问 http://localhost:8000
```

## 使用方法

### 快速开始

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **启动后端服务**：
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   chmod +x start.sh
   ./start.sh
   
   # 或者直接运行
   python app.py
   ```

3. **打开前端页面**：
   - 直接用浏览器打开 `index.html` 文件
   - 或者使用本地服务器（推荐）：
     ```bash
     python -m http.server 8000
     # 然后访问 http://localhost:8000
     ```

### 使用步骤

1. **上传图片**：
   - 点击上传区域选择图片
   - 或直接拖拽图片到上传区域
   - 支持格式：png, jpg, jpeg, gif, bmp

2. **选择打码方式**：
   - **马赛克模式**：
     - 调整滑块设置马赛克块大小（5-30）
     - 数值越小，马赛克越模糊
     - 可以实时预览马赛克效果
   - **图片遮挡模式**：
     - 点击"选择遮挡图片"按钮
     - 上传自定义遮挡图片
     - 遮挡图片会自动调整到检测区域大小

3. **开始打码**：
   - 点击"开始打码"按钮
   - 等待处理完成（处理时间取决于图片大小和检测目标数量）
   - 处理完成后，右侧会显示打码后的图片

4. **下载结果**：
   - 点击"下载图片"按钮保存处理后的图片
   - 图片会自动保存为 JPEG 格式

## API 接口

### POST /api/process

处理图片推理和打码

**请求参数：**
- `image` (file): 输入图片文件
- `mosaic_size` (int): 马赛克块大小（默认 10）
- `use_mosaic` (bool): 是否使用马赛克（true/false）
- `overlay_image` (file, 可选): 遮挡图片文件（当 use_mosaic=false 时）

**返回：**
- 处理后的图片（JPEG 格式）

### GET /api/health

健康检查接口

**返回：**
```json
{
  "status": "ok"
}
```

## 技术栈

### 后端
- Flask: Web 框架
- Flask-CORS: 跨域支持
- OpenCV: 图像处理
- Ultralytics YOLO: 目标检测

### 前端
- Vue 3: 前端框架
- Element Plus: UI 组件库

## 注意事项

1. **模型文件**：确保 `best.pt` 模型文件存在于项目根目录
2. **目录创建**：首次运行会自动创建 `uploads` 和 `results` 目录
3. **图片格式**：支持的图片格式：png, jpg, jpeg, gif, bmp
4. **处理时间**：处理大图片可能需要较长时间，请耐心等待
5. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Edge等）
6. **跨域问题**：如果前端和后端不在同一端口，确保后端已启用CORS（已默认启用）
7. **文件清理**：上传的临时文件会在处理完成后自动清理，结果文件保留在 `results` 目录
8. **内存使用**：处理大图片时可能会占用较多内存，建议图片大小不超过10MB

## 开发说明

### 修改推理参数

在 `infer.py` 中修改 `infer_params` 字典：

```python
infer_params = {
    "conf": 0.3,      # 置信度阈值
    "iou": 0.5,       # NMS阈值
    "imgsz": 640,     # 图片尺寸
    "device": "cpu",  # 设备（cpu/cuda）
    # ... 其他参数
}
```

### 自定义遮挡效果

可以修改 `apply_image_overlay` 函数来实现不同的遮挡效果，例如：
- 添加透明度
- 添加边框
- 应用滤镜效果

## 许可证

MIT License

