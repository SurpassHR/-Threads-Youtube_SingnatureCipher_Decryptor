# -*- coding: utf-8 -*-
# @Time : 2020/8/30 22:29
# @Author : KevinHoo
# @Site : 
# @File : decodeAllinOne.py
# @Software: PyCharm 
# @Email : hu.rui0530@gmail.com
# @Note : get decode base and get encode func

import re
import urllib.request
import execjs
import time
import os

from bs4 import BeautifulSoup
from itertools import islice


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/85.0.4183.76 Safari/537.36",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6"
}
domain = "https://www.youtube.com"
func = re.compile('.*?function\(a\){a=a.split\(""\).*?return a.join\(""\)};')
mainname = re.compile('([0-9a-zA-Z]{2})=')
sub0 = re.compile('([0-9a-zA-Z]{2})\.')
filename = './base_history/base.js'
# filename = './base_history/2020-09-22 17-42-53_base.js'
baseDownPath = './base_history/'


# 文件改名
def changeFileName():
    base_gettime = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
    srcFile = './base_history/base.js'
    dstFile = './base_history/{}_base.js.old'.format(base_gettime)
    try:
        os.rename(srcFile, dstFile)
    except Exception as e:
        print(e)
        print('rename file fail\r\n')
    else:
        print('rename file success\r\n')


# 初始化目录
def cfgDirInit(path: str) -> bool:
    """
    :param path:
    :return:
    """
    import os
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path, '创建成功')
        return True
    else:
        print(path, '目录已存在')
        return False


def askURL(url):
    res = urllib.request.Request(url=url, headers=headers)
    req = urllib.request.urlopen(res)
    html = req.read().decode('utf-8')
    return html


def parseHtml(html):
    soup = BeautifulSoup(html, 'lxml')
    basejs = soup.select('script[name="player_ias/base"]')
    return basejs


def findBaseJs(basejs):
    backdrop = re.findall('src="(.*?)"', str(basejs))[0]
    url = domain + backdrop
    jsfile = askURL(url)
    return jsfile


def writeFile(jsfile, basepath):
    changeFileName()
    with open(basepath, "w", encoding='utf-8') as f:
        f.write(jsfile)
    return '成功写入{}'.format(filename)


def getDecoderFromLine(filename, sig):
    includefun1 = ""
    try:
        f = open(filename)
        for a in islice(f, 1400, 1500):   # 主函数大概位置
            includefun1 = includefun1 + a
        f.close()
    except Exception as e:
        print(e)
    mainfunc = re.findall(func, includefun1)[0]   # 主函数体
    print(mainfunc)
    mainfuncname = re.findall(mainname, mainfunc)[0]   # 主函数名

    includefun2 = ""
    sub0funcname = re.findall(sub0, mainfunc)[0]   # 调用函数名
    sub = re.compile(sub0funcname + '=\{.*?\};', re.S)  # noqa: W605
    try:
        f = open(filename)
        for a in islice(f, 5500, 6000):   # 调用函数大概位置
            includefun2 = includefun2 + a
        f.close()
    except Exception as e:
        print(e)
    subfunc = re.findall(sub, includefun2)[0].replace('\n', '')   # 调用函数体
    print(subfunc)

    js = mainfunc + subfunc + """
        function decode(sig) {{
            return {}(sig);
        }}
    """.format(mainfuncname)
    ctx = execjs.compile(js)   # 函数 + 输出 打包

    return ctx.call("decode", sig)


def updateDB():
    url = 'https://www.youtube.com/watch?v=LXb3EKWsInQ'
    html = askURL(url)
    basejs = parseHtml(html)
    print(basejs)
    jsfile = findBaseJs(basejs)
    cfgDirInit(baseDownPath)
    print(writeFile(jsfile, filename))


def jsdecode(sig):
    return getDecoderFromLine(filename, sig)


if __name__ == '__main__':
    updateDB()
    # sig decode test
    # sig = 'AOqAOq0QJ8wRgIhAKRCMhimUm40tdI9y5jK_0kbVT06hfm8C2NMBgJA%3DWHYAiEA9K6Hcab7TnatwVbwlcxBQ2MZj4abh1J67X0sntVvtWVg'
    # print(getDecoderFromLine(filename, sig))
