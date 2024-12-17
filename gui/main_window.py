from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QComboBox, QFileDialog,
                             QListWidget, QProgressBar, QLabel, QMessageBox,
                             QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from downloader import DownloadWorker
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube视频下载器")
        self.setMinimumSize(800, 600)
        
        # 下载工作线程
        self.download_worker = None
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # URL输入区域
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入YouTube视频链接(每行一个)")
        self.url_input.setAcceptDrops(True)
        url_layout.addWidget(self.url_input)
        
        # 添加URL按钮
        add_url_btn = QPushButton("添加链接")
        add_url_btn.clicked.connect(self.add_url)
        url_layout.addWidget(add_url_btn)
        main_layout.addLayout(url_layout)
        
        # URL列表
        self.url_list = QListWidget()
        main_layout.addWidget(self.url_list)
        
        # 下载选项区域
        options_layout = QHBoxLayout()
        
        # 清晰度选择
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最高质量", "1080p", "720p", "480p", "360p", "仅音频"])
        options_layout.addWidget(QLabel("清晰度:"))
        options_layout.addWidget(self.quality_combo)
        
        # 保存路径选择
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        options_layout.addWidget(QLabel("保存路径:"))
        options_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.choose_save_path)
        options_layout.addWidget(browse_btn)
        
        main_layout.addLayout(options_layout)
        
        # 下载按钮
        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel()
        main_layout.addWidget(self.status_label)
        
        # 设置默认下载路径
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTubeDownloader")
        self.path_input.setText(default_path)
        
        # 显示免责声明
        self.show_disclaimer()
    
    def show_disclaimer(self):
        """显示免责声明"""
        disclaimer = ("免责声明:\n\n"
                     "1. 本工具仅供学习和研究使用\n"
                     "2. 请勿下载侵犯版权的内容\n"
                     "3. 使用本工具产生的一切法律责任由用户自行承担")
        QMessageBox.information(self, "免责声明", disclaimer)
    
    def add_url(self):
        """添加URL到列表"""
        urls = self.url_input.text().strip().split('\n')
        for url in urls:
            if url and url not in [self.url_list.item(i).text().split(' - ')[0] for i in range(self.url_list.count())]:
                item = QListWidgetItem(url)
                item.setData(Qt.UserRole, {'progress': 0, 'status': '等待下载'})
                self.url_list.addItem(item)
        self.url_input.clear()
    
    def choose_save_path(self):
        """选择保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择保存路径", self.path_input.text())
        if path:
            self.path_input.setText(path)
    
    def get_quality_format(self):
        """获取选择的清晰度对应的格式"""
        quality_map = {
            "最高质量": "best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "仅音频": "bestaudio/best"
        }
        return quality_map[self.quality_combo.currentText()]
    
    def start_download(self):
        """开始下载"""
        if not self.url_list.count():
            QMessageBox.warning(self, "警告", "请先添加下载链接")
            return
        
        if not self.path_input.text():
            QMessageBox.warning(self, "警告", "请选择保存路径")
            return
        
        # 如果已经在下载,则停止下载
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.stop()
            self.download_worker.wait()
            self.download_btn.setText("开始下载")
            self.status_label.setText("下载已停止")
            return
        
        # 获取所有URL
        urls = []
        for i in range(self.url_list.count()):
            item = self.url_list.item(i)
            url = item.text().split(' - ')[0]  # 去掉可能存在的进度信息
            urls.append(url)
            item.setText(url)  # 重置显示文本
        
        # 创建下载工作线程
        self.download_worker = DownloadWorker(
            urls=urls,
            save_path=self.path_input.text(),
            quality=self.get_quality_format()
        )
        
        # 连接信号
        self.download_worker.progress_updated.connect(self.update_progress)
        self.download_worker.status_updated.connect(self.update_status)
        self.download_worker.error_occurred.connect(self.handle_error)
        self.download_worker.download_finished.connect(self.handle_download_finished)
        
        # 开始下载
        self.download_worker.start()
        self.download_btn.setText("停止下载")
        self.status_label.setText("开始下载...")
        self.progress_bar.setValue(0)
    
    def update_progress(self, url, progress):
        """更新进度"""
        # 更新总进度条
        self.progress_bar.setValue(int(progress))
        
        # 更新列表项进度
        for i in range(self.url_list.count()):
            item = self.url_list.item(i)
            if url in item.text().split(' - ')[0]:
                data = item.data(Qt.UserRole)
                data['progress'] = progress
                item.setData(Qt.UserRole, data)
                item.setText(f"{url} - {progress:.1f}%")
                break
    
    def update_status(self, url, status):
        """更新状态"""
        self.status_label.setText(status)
        
        # 更新列表项状态
        for i in range(self.url_list.count()):
            item = self.url_list.item(i)
            if url in item.text().split(' - ')[0]:
                data = item.data(Qt.UserRole)
                data['status'] = status
                item.setData(Qt.UserRole, data)
                # 如果是完成状态,更新显示
                if '完成' in status:
                    item.setText(f"{url} - 已完成")
                break
    
    def handle_error(self, url, error):
        """处理错误"""
        self.status_label.setText(f"错误: {error}")
        
        # 更新列表项状态
        for i in range(self.url_list.count()):
            item = self.url_list.item(i)
            if url in item.text().split(' - ')[0]:
                item.setText(f"{url} - 下载失败")
                break
                
        QMessageBox.warning(self, "下载错误", f"下载视频时发生错误:\n{error}")
    
    def handle_download_finished(self):
        """处理下载完成"""
        self.download_btn.setText("开始下载")
        self.status_label.setText("下载完成")
        
        # 检查是否所有文件都已下载
        save_path = self.path_input.text()
        if os.path.exists(save_path) and os.listdir(save_path):
            QMessageBox.information(self, "完成", f"所有视频下载完成!\n保存在: {save_path}")
        else:
            QMessageBox.warning(self, "警告", f"下载可能未成功。\n请检查保存路径: {save_path}")