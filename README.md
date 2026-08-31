# GenkiArm（GenkiBot）

低成本具身智能学习平台，基于斯坦福 ALPHA（aloha）机械臂构型和开源 [LeRobot](https://github.com/huggingface/lerobot) 项目修改开发，用于机械臂遥操作数据采集、ACT（Action Chunking with Transformers）模仿学习训练与策略部署。

## 硬件与端口

| 部件 | 说明 |
|---|---|
| 主臂（leader，示教） | Genki M1 电机 ×6（GBot 协议），串口 `com4` |
| 从臂（follower，执行） | Feetech STS3215 电机 ×6，串口 `com5` |
| 相机 ×2 | `laptop`（相机索引 2）、`phone`（相机索引 3），640×480 @ 30fps |

机器人配置见 [lerobot/configs/robot/so100.yaml](lerobot/configs/robot/so100.yaml)。

## 需要下载/安装的依赖（Requirements）

### 1. Python 环境

- Python 3.10（建议 conda）

```bash
conda create -y -n jszn python=3.10
conda activate jszn
```

### 2. Python 包

```bash
git clone https://github.com/xiangcongyanjiusuo/lerobot.git   # 或 https://gitee.com/huahuaze/genkiarm.git
cd lerobot
pip install -e .
pip install -r requirements.txt
```

> 训练需要 NVIDIA GPU：请从 [pytorch.org](https://pytorch.org/get-started/locally/) 安装与你的 CUDA 版本匹配的 torch/torchvision。

### 3. ffmpeg（录制视频必需，需自行下载）

录制数据时 LeRobot 调用 ffmpeg 把图像帧编码成 mp4 视频。仓库不包含 ffmpeg（体积约 435MB，超出 GitHub 限制），需要自行下载：

- 下载地址（Windows release 版）：https://www.gyan.dev/ffmpeg/builds/
- 解压后把 `ffmpeg.exe`、`ffprobe.exe` 放到本项目的 `ffmpeg/bin/` 目录，或加入系统 PATH

### 4. USB 串口驱动

主臂/从臂通过 USB 转串口连接。若设备管理器里看不到 `com4`/`com5`，需安装对应转接芯片的驱动（常见为 CH340 / FTDI，按你的硬件型号到官网下载）。

## 快速开始

详细参数说明见 [操作文档.md](操作文档.md)。

```bash
# 1. 遥操作测试（不带相机）
python lerobot/scripts/control_robot.py teleoperate --robot-path lerobot/configs/robot/so100.yaml --robot-overrides "~cameras" --display-cameras 0

# 2. 采集数据（50 集 × 45 秒；重新录制务必带 --force-override 1）
python lerobot/scripts/control_robot.py record --robot-path lerobot/configs/robot/so100.yaml --fps 30 --root data --repo-id pick/so100_test --tags pickbottle --episode-time-s 45 --reset-time-s 6 --num-episodes 50 --push-to-hub 0 --force-override 1

# 3. 训练 ACT 策略（约 8 万步；中断后加 resume=true 续训）
set DATA_DIR=./data/
python lerobot/scripts/train.py dataset_repo_id=pick/so100_test policy=act_so100_real env=so100_real hydra.run.dir=outputs/train/act_so100_new hydra.job.name=act_so100_new device=cuda wandb.enable=false

# 4. 部署评估（模型自主控制）
python lerobot/scripts/control_robot.py record --robot-path lerobot/configs/robot/so100.yaml --fps 30 --root data --repo-id pick/eval_so100_test --tags pickbottle --warmup-time-s 5 --episode-time-s 300 --reset-time-s 10 --num-episodes 2 -p outputs/train/act_so100_new/checkpoints/last/pretrained_model
```

> 采集时快捷键：`→` 提前结束当前片段，`←` 重录当前片段，`Esc` 停止采集。

## 数据集与模型

- `data/pick/so100_test/`：50 个 episode 的采集数据。**仓库中只包含状态/动作记录**（`episodes/`、`train/`、`meta_data/`），相机视频不进入版本库（`.gitignore` 排除，体积约 5.6GB）
- `outputs/train/act_so100_new/checkpoints/last/`：训练完成的 ACT 模型（经 Git LFS 存储）

## 已知问题

- **PyTorch ≥ 2.6 续训报错**：新版 torch 的 `torch.load` 默认 `weights_only=True`，加载含 numpy 对象的 `training_state.pth` 会失败。已在 [lerobot/common/logger.py](lerobot/common/logger.py) 中修复
- **Windows 保存 checkpoint 提示符号链接失败**（WinError 1314）：无管理员权限时自动回退为复制，不影响使用
- **GitHub 推送 100MB 限制**：模型权重等大文件经 Git LFS 上传；github.com 直连不稳定时多试几次

## 目录结构

```
genkiarm/
├── lerobot/             # LeRobot 源码（含 GBot 主臂驱动改造）
│   ├── configs/robot/so100.yaml   # 机器人硬件配置
│   └── scripts/         # control_robot / train / eval 等脚本
├── data/                # 采集数据（视频不在版本库）
├── outputs/train/       # 训练输出与模型 checkpoint
├── ffmpeg/              # ffmpeg 可执行文件（需自行下载，不在版本库）
├── requirements.txt
└── 操作文档.md
```

## 开源许可证

基于 [LeRobot](https://github.com/huggingface/lerobot)（Apache 2.0）修改开发，沿用原项目许可证，详见 [LICENSE](LICENSE)。感谢 LeRobot 与 ALPHA 的开源贡献。
