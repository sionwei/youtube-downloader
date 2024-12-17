# YouTube视频下载器

一个简单的YouTube视频下载工具,基于PyQt5和yt-dlp开发。

## 功能特点

- 支持单个或批量下载YouTube视频
- 可选择不同的视频清晰度(最高质量/1080p/720p/480p/360p/仅音频)
- 实时显示下载进度和速度
- 支持暂停/继续下载
- 简洁直观的用户界面
- 自动保存下载历史
- 支持视频格式转换

## 安装说明

1. 确保已安装Python 3.6或更高版本
2. 克隆仓库:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序:
```bash
python main.py
```

2. 在输入框中输入YouTube视频链接(每行一个)
3. 点击"添加链接"按钮将链接添加到下载列表
4. 选择保存路径和视频清晰度
5. 点击"开始下载"按钮开始下载
6. 下载过程中可以点击"停止下载"按钮暂停下载

## 项目结构

```
youtube-downloader/
├── main.py              # 主程序入口
├── requirements.txt     # 项目依赖
├── README.md           # 项目说明
├── LICENSE             # 开源协议
├── gui/                # GUI模块
│   ├── __init__.py
│   └── main_window.py  # 主窗口类
└── downloader/         # 下载模块
    ├── __init__.py
    ├── simple_downloader.py  # 下载器类
    └── download_worker.py    # 下载工作线程类
```

## 开发环境

- Python 3.6+
- PyQt5 5.15.0+
- yt-dlp 2024.3.10+
- Windows 10/11

## 注意事项

- 本工具仅供学习和研究使用
- 请勿下载侵犯版权的内容
- 使用本工具产生的一切法律责任由用户自行承担
- 如遇到下载问题,请查看日志文件 `~/Downloads/youtube_downloader.log`

## 常见问题

1. 如果下载失败,请检查:
   - 视频链接是否正确
   - 网络连接是否正常
   - 视频是否可以公开访问
   - 日志文件中的详细错误信息

2. 如果无法获取视频信息:
   - 确保视频未被删除或设为私有
   - 检查是否需要登录才能访问

## 贡献指南

欢迎提交 Pull Request 或 Issue!

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube下载库 