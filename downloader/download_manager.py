import os
from PyQt5.QtCore import QObject, pyqtSignal
import yt_dlp
import logging
import json
import time

class DownloadManager(QObject):
    # 定义信号
    progress_signal = pyqtSignal(str, float)  # URL, 进度
    status_signal = pyqtSignal(str, str)  # URL, 状态
    error_signal = pyqtSignal(str, str)  # URL, 错误信息
    
    def __init__(self):
        super().__init__()
        self.ydl_opts = None
        self.current_url = None
        
        # 设置日志
        self.logger = logging.getLogger('youtube_downloader')
        self.logger.setLevel(logging.DEBUG)
        
        # 添加控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        # 添加文件处理器
        log_file = os.path.join(os.path.expanduser("~"), "Downloads", "youtube_downloader.log")
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    
    def _progress_hook(self, d):
        """下载进度回调"""
        if d['status'] == 'downloading':
            try:
                # 计算下载进度
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes_estimate', 100)
                    progress = (downloaded / total) * 100 if total > 0 else 0
                
                # 发送进度信号
                self.progress_signal.emit(self.current_url, progress)
                
                # 更新状态信息
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024  # 转换为MB/s
                    status = f'正在下载... {speed_mb:.1f}MB/s'
                    self.status_signal.emit(self.current_url, status)
                
                # 记录下载信息
                self.logger.debug(f"下载进度: {progress:.1f}%, 速度: {speed_mb:.1f}MB/s")
                
            except Exception as e:
                self.error_signal.emit(self.current_url, f"进度计算错误: {str(e)}")
            
        elif d['status'] == 'finished':
            filename = d.get('filename', '')
            self.logger.info(f"文件下载完成: {filename}")
            self.status_signal.emit(self.current_url, '下载完成,正在处理...')
            
        elif d['status'] == 'error':
            error = d.get('error', '未知错误')
            self.logger.error(f"下载错误: {error}")
            self.error_signal.emit(self.current_url, str(error))
    
    def download_video(self, url, save_path, quality='best', proxy=None):
        """下载单个视频"""
        try:
            self.current_url = url
            self.logger.info(f"开始下载视频: {url}")
            
            # 确保保存路径存在
            save_path = os.path.abspath(save_path)
            if not os.path.exists(save_path):
                try:
                    os.makedirs(save_path)
                    self.logger.info(f"创建保存目录: {save_path}")
                except Exception as e:
                    self.logger.error(f"创建目录失败: {str(e)}")
                    self.error_signal.emit(url, f"创建保存目录失败: {str(e)}")
                    return
            
            # 检查路径权限
            if not os.access(save_path, os.W_OK):
                self.logger.error(f"没有写入权限: {save_path}")
                self.error_signal.emit(url, f"没有写入权限: {save_path}")
                return
            
            # 简化质量选择
            if quality in ['1080p', '720p', '480p', '360p']:
                height = quality[:-1]  # 移除'p'
                format_str = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}]'
            elif quality == '仅音频':
                format_str = 'bestaudio[ext=m4a]/bestaudio'
            else:  # 最高质量
                format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            
            # 设置下载选项
            self.ydl_opts = {
                'format': format_str,
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'merge_output_format': 'mp4',
                'quiet': False,
                'no_warnings': False,
                'verbose': True,  # 添加详细输出
                'ignoreerrors': False,
                'nocheckcertificate': True,
                'noplaylist': True,
                'extract_flat': False,
                'writeinfojson': True,  # 保存视频信息
                'writethumbnail': True,  # 下载缩略图
                # 添加更多选项来解决403错误
                'extractor_retries': 5,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'rm_cachedir': True,
                'no_color': True,  # 禁用颜色输出
                # 添加请求头
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                },
                # 添加cookies支持
                'cookiesfrombrowser': ('chrome',),
                # 添加更多下载选项
                'buffersize': 1024 * 1024 * 16,  # 16MB缓冲区
                'concurrent_fragment_downloads': 8,  # 增加并发下载数
                'file_access_retries': 5,
                'throttledratelimit': None,
                'socket_timeout': 60,
                'sleep_interval': 2,  # 重试间隔
                'max_sleep_interval': 5,
                # ffmpeg设置
                'prefer_ffmpeg': True,
                'ffmpeg_location': None,
                'keepvideo': True,  # 保留源文件
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }, {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }, {
                    'key': 'EmbedThumbnail',  # 嵌入缩略图
                }],
            }
            
            # 如果提供了代理,添加代理设置
            if proxy:
                if proxy.startswith('http://') or proxy.startswith('https://'):
                    self.ydl_opts['proxy'] = proxy
                else:
                    self.ydl_opts['proxy'] = f'http://{proxy}'
                self.logger.info(f"使用代理: {self.ydl_opts['proxy']}")
            
            # 开始下载
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                self.status_signal.emit(url, '正在获取视频信息...')
                try:
                    self.logger.info("获取视频信息...")
                    # 先尝试提取信息
                    info = ydl.extract_info(url, download=False)
                    if info:
                        self.logger.info(f"视频标题: {info.get('title')}")
                        self.logger.info(f"视频格式: {format_str}")
                        self.logger.info(f"可用格式: {json.dumps(info.get('formats', []), indent=2)}")
                        
                        # 等待一下再开始下载
                        time.sleep(2)
                        
                        self.status_signal.emit(url, '开始下载...')
                        # 开始下载
                        ydl.download([url])
                        
                        # 验证文件是否存在
                        expected_file = os.path.join(save_path, f"{info.get('title')}.mp4")
                        if os.path.exists(expected_file):
                            self.logger.info(f"文件已成功保存: {expected_file}")
                            file_size = os.path.getsize(expected_file)
                            self.logger.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB")
                        else:
                            self.logger.error(f"文件未找到: {expected_file}")
                            # 检查是否有其他格式的文件
                            files = os.listdir(save_path)
                            self.logger.info(f"目录内容: {files}")
                            self.error_signal.emit(url, "下载完成但文件未找到,可能是格式转换失败")
                    else:
                        self.logger.error("无法获取视频信息")
                        self.error_signal.emit(url, '无法获取视频信息')
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    self.logger.error(f"下载错误: {error_msg}")
                    if '403' in error_msg:
                        if proxy:
                            self.error_signal.emit(url, f"使用代理 {proxy} 访问被拒绝(403错误),请尝试:\n1. 检查代理是否可用\n2. 尝试使用其他代理\n3. 等待一段时间后重试")
                        else:
                            self.error_signal.emit(url, "访问被拒绝(403错误),请尝试:\n1. 检查网络连接\n2. 使用代理\n3. 等待一段时间后重试")
                    elif 'Sign in to confirm your age' in error_msg:
                        self.error_signal.emit(url, "需要年龄验证,请在Chrome浏览器中登录YouTube账号后重试")
                    elif 'This video is unavailable' in error_msg:
                        self.error_signal.emit(url, "视频不可用,可能已被删除或设为私有")
                    elif 'Video unavailable' in error_msg:
                        self.error_signal.emit(url, "视频不可用,请检查链接是否正确")
                    else:
                        self.error_signal.emit(url, f"下载失败: {error_msg}")
                except Exception as e:
                    self.logger.error(f"未知错误: {str(e)}")
                    self.error_signal.emit(url, f"下载失败: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"发生错误: {str(e)}")
            self.error_signal.emit(url, f"发生错误: {str(e)}")
    
    def get_available_formats(self, url):
        """获取可用的视频格式"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                for f in info['formats']:
                    if 'height' in f and 'ext' in f:
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'height': f['height'],
                            'filesize': f.get('filesize', 'N/A')
                        })
                return formats
        except Exception as e:
            self.logger.error(f"获取格式失败: {str(e)}")
            return [] 