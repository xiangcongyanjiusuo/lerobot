import cv2
import time
import numpy as np
import os

def try_open_camera(cam_id):
    """
    尝试用不同的后端打开摄像头
    """
    # 首先尝试默认后端
    cap = cv2.VideoCapture(cam_id)
    if cap.isOpened():
        print(f"  使用默认后端打开成功")
        return cap
    
    # 尝试 DirectShow 后端
    cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"  使用 DirectShow 后端打开成功")
        return cap
    
    return None

def capture_images_with_ids(max_id=10, save_path="camera_id_images/"):
    """
    使用可用摄像头拍照并在图片上标记摄像头 ID。
    :param max_id: 假设的最大摄像头 ID 范围（默认 0 到 max_id-1）。
    :param save_path: 保存图片的路径（默认 "camera_id_images/"）。
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for cam_id in range(max_id):
        print(f"\n=== 测试摄像头 {cam_id} ===")
        # 尝试打开摄像头
        cap = try_open_camera(cam_id)
        
        if cap:
            # 设置摄像头参数
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print(f"摄像头 {cam_id} 已打开，正在初始化...")
            # 增加延迟让摄像头初始化
            time.sleep(2)
            
            # 读取多帧以确保获得有效画面
            best_frame = None
            best_brightness = 0
            
            for i in range(15):  # 进一步增加尝试次数
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    # 检查帧的亮度
                    mean_brightness = np.mean(frame)
                    print(f"摄像头 {cam_id} 第 {i+1} 帧 - 亮度: {mean_brightness:.2f}")
                    
                    # 保存亮度最高的帧
                    if mean_brightness > best_brightness:
                        best_brightness = mean_brightness
                        best_frame = frame.copy()
                        print(f"  → 更新最佳帧，亮度: {best_brightness:.2f}")
                time.sleep(0.2)  # 进一步减少延迟
            
            if best_frame is not None:
                print(f"\n摄像头 {cam_id} 最佳帧亮度: {best_brightness:.2f}")
                
                # 在图片上添加摄像头 ID 和亮度信息
                text = f"Camera ID: {cam_id}"
                brightness_text = f"Brightness: {best_brightness:.2f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(best_frame, text, (10, 50), font, 1, (0, 255, 0), 2)
                cv2.putText(best_frame, brightness_text, (10, 90), font, 0.8, (255, 255, 255), 2)

                # 保存图片
                img_path = os.path.join(save_path, f"camera_{cam_id}.jpg")
                success = cv2.imwrite(img_path, best_frame)
                if success:
                    print(f"✅ 成功保存摄像头 {cam_id} 的图片：{img_path}")
                    # 验证文件是否存在且大小合理
                    if os.path.exists(img_path):
                        file_size = os.path.getsize(img_path)
                        print(f"  文件大小: {file_size} 字节")
                    else:
                        print("  ❌ 保存失败：文件不存在")
                else:
                    print("  ❌ 保存失败：cv2.imwrite 返回 False")
            else:
                print(f"❌ 摄像头 {cam_id} 无法读取有效帧")

            cap.release()
        else:
            print(f"❌ 摄像头 {cam_id} 无法打开。")

    print("\n拍照完成！")

# 调用函数
capture_images_with_ids(max_id=10)
