import os
import yt_dlp
import logging
from PyQt5.QtCore import QObject, pyqtSignal

class SimpleDownloader(QObject):
    # 定义信号
    progress_signal = pyqtSignal(str, float)  # URL, 进度
    status_signal = pyqtSignal(str, str)  # URL, 状态
    error_signal = pyqtSignal(str, str)  # URL, 错误信息
    
    def __init__(self):
        super().__init__()
        self.current_url = None
        
        # 设置日志
        self.logger = logging.getLogger('simple_downloader')
        self.logger.setLevel(logging.DEBUG)
        
        # 添加控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
    
    def _progress_hook(self, d):
        """下载进度回调"""
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.progress_signal.emit(self.current_url, progress)
                    
                    # 显示下载速度
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024
                        self.status_signal.emit(self.current_url, f'正在下载... {speed_mb:.1f}MB/s')
                
            except Exception as e:
                self.logger.error(f"进度计算错误: {e}")
                
        elif d['status'] == 'finished':
            self.status_signal.emit(self.current_url, '下载完成')
            
        elif d['status'] == 'error':
            self.error_signal.emit(self.current_url, str(d.get('error', '未知错误')))
    
    def download(self, url, save_path, quality='best'):
        """下载视频"""
        try:
            self.current_url = url
            self.logger.info(f"开始下载: {url}")
            
            # 确保保存路径存在
            os.makedirs(save_path, exist_ok=True)
            
            # 基本下载选项
            ydl_opts = {
                'format': quality,
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                # 基本的重试选项
                'retries': 3,
                'fragment_retries': 3,
                # 基本的请求头
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                },
            }
            
            # 开始下载
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.status_signal.emit(url, '正在获取视频信息...')
                
                try:
                    # 获取视频信息
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        raise Exception("无法获取视频信息")
                    
                    title = info.get('title', '')
                    self.logger.info(f"视频标题: {title}")
                    
                    # 开始下载
                    self.status_signal.emit(url, '开始下载...')
                    ydl.download([url])
                    
                    # 验证文件
                    expected_file = os.path.join(save_path, f"{title}.mp4")
                    if os.path.exists(expected_file):
                        size = os.path.getsize(expected_file)
                        self.logger.info(f"下载完成: {expected_file} ({size/1024/1024:.1f}MB)")
                        return True
                    else:
                        self.logger.error(f"文件未找到: {expected_file}")
                        raise Exception("下载完成但文件未找到")
                    
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    self.logger.error(f"下载错误: {error_msg}")
                    self.error_signal.emit(url, f"下载失败: {error_msg}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"发生错误: {e}")
            self.error_signal.emit(url, f"发生错误: {str(e)}")
            return False 