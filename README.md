# 快速开始
1. 设置Windows下的环境变量Path。  
添加路径指向工程如下位置确保可执行rubberband.exe。  
```
src/rubberband/otherbuilds/x64/Debug
```  

2. 设置Pycharm的工程的源码路径包含src目录。
3. 运行t_coqui.py。
4. 运行如下命令。
```shell
vlc input\Intro2LLM.mp4 --audio-track=1 --input-slave=output\output.wav --sub-file output\Intro2LLM-cn.json.srt
```