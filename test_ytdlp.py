import yt_dlp
import sys
import os

def test_youtube_dl(url):
    """测试yt-dlp功能"""
    print(f"Python版本: {sys.version}")
    print(f"yt-dlp版本: {yt_dlp.version.__version__}")
    
    # 测试视频信息获取
    print("\n1. 测试视频信息获取:")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("尝试获取视频信息...")
            info = ydl.extract_info(url, download=False)
            if info:
                print(f"视频标题: {info.get('title')}")
                print(f"视频ID: {info.get('id')}")
                print(f"视频时长: {info.get('duration')}秒")
                print("视频信息获取成功!")
            else:
                print("无法获取视频信息!")
    except Exception as e:
        print(f"获取视频信息失败: {str(e)}")
    
    # 测试格式列表获取
    print("\n2. 测试格式列表获取:")
    try:
        with yt_dlp.YoutubeDL() as ydl:
            print("尝试获取格式列表...")
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            print(f"可用格式数量: {len(formats)}")
            for f in formats[:3]:  # 只显示前3个格式
                print(f"格式ID: {f.get('format_id')}, "
                      f"分辨率: {f.get('height')}p, "
                      f"扩展名: {f.get('ext')}")
    except Exception as e:
        print(f"获取格式列表失败: {str(e)}")
    
    # 测试最简单的下载
    print("\n3. 测试简单下载:")
    save_path = os.path.join(os.path.expanduser("~"), "Downloads", "test_video.mp4")
    ydl_opts = {
        'format': 'best',
        'outtmpl': save_path,
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("尝试下载视频...")
            ydl.download([url])
            if os.path.exists(save_path):
                print(f"下载成功! 文件保存在: {save_path}")
                # 删除测试文件
                os.remove(save_path)
            else:
                print("下载失败: 文件未找到")
    except Exception as e:
        print(f"下载失败: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入要测试的YouTube视频URL: ")
    
    test_youtube_dl(url) 