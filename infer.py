from ultralytics import YOLO
import cv2

# 加载模型（自动使用CPU）
model = YOLO("best.pt")  # 替换为你的best.pt路径

# 推理参数配置（CPU优化关键）
infer_params = {
    "conf": 0.3,               # 置信度阈值
    "iou": 0.5,                # NMS阈值
    "imgsz": 640,              # 与训练时一致
    "device": "cpu",           # 强制使用CPU
    "half": False,             # CPU不支持FP16，禁用
    "int8": True,              # 启用INT8量化推理（提速，精度损失极小）
    "batch": 1,                # CPU批量推理效率低，设为1
    "optimize": True           # 启用PyTorch推理优化
}


def apply_mosaic(img, x1, y1, x2, y2, mosaic_size=10):
    """
    在指定区域应用马赛克效果
    
    Args:
        img: 输入图像
        x1, y1: 左上角坐标
        x2, y2: 右下角坐标
        mosaic_size: 马赛克块大小（越小越模糊）
    
    Returns:
        处理后的图像
    """
    # 确保坐标在图像范围内
    h, w = img.shape[:2]
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(x2)), min(h, int(y2))
    
    # 提取检测区域
    roi = img[y1:y2, x1:x2].copy()
    
    if roi.size == 0:
        return img
    
    # 计算缩小后的尺寸
    roi_h, roi_w = roi.shape[:2]
    small_h = max(1, roi_h // mosaic_size)
    small_w = max(1, roi_w // mosaic_size)
    
    # 缩小图像
    small_roi = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    # 放大回原始尺寸
    mosaic_roi = cv2.resize(small_roi, (roi_w, roi_h), interpolation=cv2.INTER_NEAREST)
    
    # 将马赛克区域放回原图
    img[y1:y2, x1:x2] = mosaic_roi
    
    return img


def apply_image_overlay(img, x1, y1, x2, y2, overlay_img):
    """
    在指定区域应用图片遮挡
    
    Args:
        img: 输入图像
        x1, y1: 左上角坐标
        x2, y2: 右下角坐标
        overlay_img: 遮挡图片
    
    Returns:
        处理后的图像
    """
    # 确保坐标在图像范围内
    h, w = img.shape[:2]
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(x2)), min(h, int(y2))
    
    # 计算检测区域尺寸
    roi_h, roi_w = y2 - y1, x2 - x1
    
    if roi_h <= 0 or roi_w <= 0:
        return img
    
    # 调整遮挡图片尺寸以匹配检测区域
    overlay_resized = cv2.resize(overlay_img, (roi_w, roi_h), interpolation=cv2.INTER_LINEAR)
    
    # 将遮挡图片放回原图
    img[y1:y2, x1:x2] = overlay_resized
    
    return img


# 1. 图片推理
def infer_image(img_path, save_path="result.jpg", mosaic_size=10, overlay_img_path=None):
    """
    对图片进行推理，并在检测到的区域打马赛克或应用图片遮挡
    
    Args:
        img_path: 输入图片路径
        save_path: 保存路径
        mosaic_size: 马赛克块大小（默认10，数值越小越模糊）
        overlay_img_path: 遮挡图片路径（如果提供，则使用图片遮挡；否则使用马赛克）
    
    Returns:
        处理后的图像数组
    """
    img = cv2.imread(img_path)
    if img is None:
        print(f"错误：无法读取图片 {img_path}")
        return None
    
    # 执行推理
    results = model(img, **infer_params)
    
    # 获取检测结果
    boxes = results[0].boxes
    
    # 加载遮挡图片（如果提供）
    overlay_img = None
    if overlay_img_path:
        overlay_img = cv2.imread(overlay_img_path)
        if overlay_img is None:
            print(f"警告：无法读取遮挡图片 {overlay_img_path}，将使用马赛克")
            overlay_img = None
    
    # 在检测区域应用遮挡
    if len(boxes) > 0:
        for box in boxes:
            # 获取边界框坐标（xyxy格式）
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            if overlay_img is not None:
                # 使用图片遮挡
                img = apply_image_overlay(img, x1, y1, x2, y2, overlay_img)
            else:
                # 使用马赛克
                img = apply_mosaic(img, x1, y1, x2, y2, mosaic_size)
        
        method = "图片遮挡" if overlay_img is not None else "马赛克"
        print(f"检测到 {len(boxes)} 个目标，已应用{method}")
    else:
        print("未检测到任何目标")
    
    # 保存结果
    cv2.imwrite(save_path, img)
    print(f"图片结果保存至：{save_path}")
    
    return img


# 运行示例（根据需求选择）
if __name__ == "__main__":
    infer_image("10058.jpg")  # 图片推理
