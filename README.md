# -Threads-Youtube_SingnatureCipher_Decryptor
requests库/多线程/默认最高质量音轨和图像

环境：python3
第三方库：requests

## 使用方法：

1.下载zip文件后解压

2.在当前目录打开cmd命令提示窗

3.输入`pip install -r requirements.txt`回车，自动配置（实际上除requests之外都是更新）

4.仍然是cmd，输入`python YSD.py`

5.出现`input video address:`后，输入ytb地址

6.在提示`用时...`后表示已经下载完成

7.目录下出现video和audio两个文件夹，音频视频分别保存，自动命名

## 说明

1.该项目修改自`Youtube_SingnatureCipher_Decryptor`，增加了多线程下载、自动规范命名格式，修复了多线程文件合并后导致的只能播放一半的问题

2.下载速度取决于网络，在push仓库之前的测试中平均下载速度为10m每秒，峰值20m，可以自行修改线程数及其上限`threadsDownload.py line:96 # if all_thread > 10:`（按照文件大小每5m开启一个线程，酌情更改），但会增加cpu占用

3.默认开启了日志，可以在`YSD.py line:57 # logOn = True`将`True`改为`False`，然后删除目录下的`log`文件夹即可

### 下载示范：
![](https://imgchr.com/i/wCfaPf)
![](https://imgchr.com/i/wCfdG8)
