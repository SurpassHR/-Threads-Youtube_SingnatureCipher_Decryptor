# -Threads-Youtube_SingnatureCipher_Decryptor

requests库/多线程/默认最高质量音轨和图像

环境：python3
第三方库：requests pyexecjs

js运行环境：Nodejs

#### @Note 2020-09-05 推翻了之前的一个猜想，base.js加密文件的覆写日期并不等于其过期日期，一般3到5天进行一次更新，在未格式化的文件中，算法的主函数位于1400-1500行之间，调用的类方法在5000-7000行之间，利用正则表达式可以获取算法函数的内容；函数每次变换的是顺序或者操作次数或者函数、变量名，并不会更改调用函数的内容，通过运行`getDecodeBase.py`可以得到算法的完整内容。

#### @Note 2020-09-07 根据之前推翻的猜想，重新设计了解密算法的生成部分，当解密失效时，通过运行`decodeAllinOne.py`来更新解密算法。至此，YSD在短时间内拥有了独立解析链接+下载的能力，更新也告一段落，必要时(闲的蛋疼时)会继续完成[To-Do](#To-Do)中的剩余更新。但也因为增添了新的第三方库和js解释器，使得程序的易用性降低，程序的功能主要对开发者开放，以便于其维护和学习。

#### @Note 2021-02-06 签名破解部分的算法依然是有效的，重写了爬虫部分的算法，增加了`config.ini`，可以记录`base.js`是否为最新状态，以及是否设置了本地代理。



## What you should do to build the environment

1.`pip install -r requirement.txt`

2.[Node.js官网](https://nodejs.org/en/)下载Node.js并按照默认设置安装



## 使用方法：

1.下载zip文件后解压

2.在当前目录打开cmd命令提示窗

3.输入`pip install -r requirements.txt`回车，自动配置（实际上除requests之外都是更新）

4.cmd输入`py decodeAllinOne.py`，待录入完成后关闭，出现`base_history`文件夹，算法源文件

5.仍然是cmd，输入`py YSD.py`

6.出现`input video address:`后，输入ytb地址

7.在提示`用时...`后表示已经下载完成

8.目录下出现`video`和`audio`两个文件夹，音频视频分别保存，自动命名

## 说明：

1.该项目修改自`Youtube_SingnatureCipher_Decryptor`，增加了多线程下载、自动规范命名格式，修复了多线程文件合并后导致的只能播放一半的问题

2.下载速度取决于网络，在push仓库之前的测试中平均下载速度为10m每秒，峰值20m，可以自行修改线程数及其上限`threadsDownload.py line:96 # if all_thread > 10:`（按照文件大小每5m开启一个线程，酌情更改），但会增加cpu占用

3.默认开启了日志，可以在`YSD.py line:57 # logOn = True`将`True`改为`False`，然后删除目录下的`log`文件夹即可

4.本程序只用作学习用途

### 下载示范：

![wCfaPf.png](https://s1.ax1x.com/2020/09/03/wCfaPf.png)
![wCfdG8.png](https://s1.ax1x.com/2020/09/03/wCfdG8.png)

## To-Do:

- [x] 多线程
- [ ] GUI
- [x] 编译可执行文件