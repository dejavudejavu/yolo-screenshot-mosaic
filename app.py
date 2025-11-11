from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import traceback
from infer import infer_image
import uuid

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# 创建必要的文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/process', methods=['POST'])
def process_image():
    """处理图片推理和打码"""
    try:
        # 检查是否有图片文件
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(image_file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 获取参数
        mosaic_size = int(request.form.get('mosaic_size', 10))
        use_mosaic = request.form.get('use_mosaic', 'true').lower() == 'true'
        overlay_file = request.files.get('overlay_image')
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        input_ext = image_file.filename.rsplit('.', 1)[1].lower()
        input_filename = f"{file_id}_input.{input_ext}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # 保存上传的图片
        image_file.save(input_path)
        
        # 处理遮挡图片
        overlay_path = None
        if not use_mosaic and overlay_file and overlay_file.filename:
            if allowed_file(overlay_file.filename):
                overlay_ext = overlay_file.filename.rsplit('.', 1)[1].lower()
                overlay_filename = f"{file_id}_overlay.{overlay_ext}"
                overlay_path = os.path.join(UPLOAD_FOLDER, overlay_filename)
                overlay_file.save(overlay_path)
            else:
                return jsonify({'error': '遮挡图片格式不支持'}), 400
        
        # 生成输出文件名
        output_filename = f"{file_id}_result.jpg"
        output_path = os.path.join(RESULT_FOLDER, output_filename)
        
        # 执行推理
        try:
            if use_mosaic:
                result_img = infer_image(input_path, output_path, mosaic_size=mosaic_size)
            else:
                result_img = infer_image(input_path, output_path, mosaic_size=mosaic_size, overlay_img_path=overlay_path)
            
            if result_img is None:
                # 清理上传的文件
                if os.path.exists(input_path):
                    os.remove(input_path)
                if overlay_path and os.path.exists(overlay_path):
                    os.remove(overlay_path)
                return jsonify({'error': '图片处理失败，可能是模型加载失败或图片格式问题'}), 500
            
            # 返回结果图片
            response = send_file(output_path, mimetype='image/jpeg')
            
            # 清理上传的文件（保留结果文件）
            if os.path.exists(input_path):
                os.remove(input_path)
            if overlay_path and os.path.exists(overlay_path):
                os.remove(overlay_path)
            
            return response
        
        except Exception as infer_error:
            # 清理上传的文件
            if os.path.exists(input_path):
                os.remove(input_path)
            if overlay_path and os.path.exists(overlay_path):
                os.remove(overlay_path)
            if os.path.exists(output_path):
                os.remove(output_path)
            raise infer_error
    
    except ValueError as e:
        return jsonify({'error': f'参数错误: {str(e)}'}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

