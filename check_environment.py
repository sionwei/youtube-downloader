import sys
import os
import platform
import subprocess
import pkg_resources
import requests

def check_python():
    """检查Python环境"""
    print("\n=== Python环境 ===")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"系统平台: {platform.platform()}")
    print(f"系统架构: {platform.architecture()}")

def check_packages():
    """检查Python包"""
    print("\n=== Python包 ===")
    required_packages = ['yt-dlp', 'PyQt5', 'ffmpeg-python', 'requests']
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"{package}: 已安装 (版本 {version})")
        except pkg_resources.DistributionNotFound:
            print(f"{package}: 未安装")

def check_ffmpeg():
    """检查ffmpeg"""
    print("\n=== FFmpeg ===")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"FFmpeg已安装: {version}")
        else:
            print("FFmpeg未安装或无法运行")
    except FileNotFoundError:
        print("FFmpeg未安装")

def check_network():
    """检查网络连接"""
    print("\n=== 网络连接 ===")
    test_urls = [
        ('YouTube', 'https://www.youtube.com'),
        ('Google', 'https://www.google.com'),
    ]
    
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"{name}: 可访问")
            else:
                print(f"{name}: 无法访问 (状态码: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"{name}: 无法访问 ({str(e)})")

def check_write_permission():
    """检查写入权限"""
    print("\n=== 写入权限 ===")
    test_paths = [
        os.path.expanduser("~/Downloads"),
        os.path.join(os.path.expanduser("~"), "Downloads", "YouTubeDownloader"),
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            if os.access(path, os.W_OK):
                print(f"{path}: 有写入权限")
            else:
                print(f"{path}: 无写入权限")
        else:
            try:
                os.makedirs(path)
                print(f"{path}: 已创建并可写入")
                if path.endswith("YouTubeDownloader"):
                    os.rmdir(path)  # 删除测试创建的目录
            except Exception as e:
                print(f"{path}: 无法创建 ({str(e)})")

def main():
    """主函数"""
    print("=== 系统环境检查 ===")
    check_python()
    check_packages()
    check_ffmpeg()
    check_network()
    check_write_permission()

if __name__ == "__main__":
    main() 