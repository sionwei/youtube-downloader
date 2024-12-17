from PyQt5.QtCore import QThread, pyqtSignal
from .simple_downloader import SimpleDownloader

class DownloadWorker(QThread):
    # 定义信号
    progress_updated = pyqtSignal(str, float)  # URL, 进度
    status_updated = pyqtSignal(str, str)  # URL, 状态
    error_occurred = pyqtSignal(str, str)  # URL, 错误信息
    download_finished = pyqtSignal()  # 所有下载完成信号
    
    def __init__(self, urls, save_path, quality='best'):
        super().__init__()
        self.urls = urls
        self.save_path = save_path
        self.quality = quality
        self.is_running = True
        
        # 创建下载器
        self.downloader = SimpleDownloader()
        
        # 连接信号
        self.downloader.progress_signal.connect(self._on_progress)
        self.downloader.status_signal.connect(self._on_status)
        self.downloader.error_signal.connect(self._on_error)
    
    def run(self):
        """开始下载任务"""
        try:
            success_count = 0
            total_count = len(self.urls)
            
            for url in self.urls:
                if not self.is_running:
                    break
                
                self.status_updated.emit(url, '准备下载...')
                if self.downloader.download(url, self.save_path, self.quality):
                    success_count += 1
            
            if success_count == total_count:
                self.status_updated.emit('', f'全部下载完成 ({success_count}/{total_count})')
            else:
                self.status_updated.emit('', f'部分下载完成 ({success_count}/{total_count})')
            
            self.download_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit('general', str(e))
    
    def stop(self):
        """停止下载"""
        self.is_running = False
    
    def _on_progress(self, url, progress):
        """处理进度更新"""
        self.progress_updated.emit(url, progress)
    
    def _on_status(self, url, status):
        """处理状态更新"""
        self.status_updated.emit(url, status)
    
    def _on_error(self, url, error):
        """处理错误"""
        self.error_occurred.emit(url, error) 