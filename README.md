# bilibili手机缓存视频处理工具

> For **Python 3.5+**, need **ffmpeg**

从手机中复制出 `Android\data\tv.danmaku.bili\download\` 目录下数字编号目录（建议将该工具放入复制出目录的同级目录），并执行下面命令进行混流或合并：

Windows:
```bat
py -3 bilibili_video_tool.py -d [Numbered Dir]
```

Linux / Mac:
```bash
python3 bilibili_video_tool.py -d [Numbered Dir]
```

`[Numbered Dir]`为数字编号目录的路径（绝对、相对路径均可）

**使用方法：**
```py
usage: bilibili_video_tool.py [options]

bilibili download video mixer / merger by SpaceSkyNet

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  the workspace_dir
```

# 新功能
可自动转换danmaku.xml为对应的.ass字幕。

需要从https://github.com/m13253/danmaku2ass 下载danmaku2ass.py。

并更改bilibili_video_tool.py文件第22行：danmaku2ass_path = 'D:\danmaku2ass.py'为你自己的路径。

同时，需要安装ffmpeg和ffprobe，可在https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z 下载到编译后的windows版。

ffmpeg.exe与ffprobe.exe需要在PATH环境变量中，可以直接把它们放在c:\windows\system32文件夹下。

更改了一部分代码，以适配老版本的视频缓存。

