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

from bs4 import BeautifulSoup
from itertools import islice

filename = './base_history/base.js'
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.76 Safari/537.36",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6"
}
domain = "https://www.youtube.com"
func = re.compile('.*?function\(a\){a=a.split\(""\).*?return a.join\(""\)};')
mainname = re.compile('([0-9a-zA-Z]{2})=')
sub0 = re.compile('([0-9a-zA-Z]{2})\.')


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
    with open(basepath, "w", encoding='utf-8') as f:
        f.write(jsfile)
    return


def getDecoderFromLine(filename, sig):
    includefun1 = ""
    f = open(filename)
    for a in islice(f, 1400, 1500): # 主函数大概位置
        includefun1 = includefun1 + a
    f.close()
    mainfunc = re.findall(func, includefun1)[0] # 主函数体
    mainfuncname = re.findall(mainname, mainfunc)[0] # 主函数名

    includefun2 = ""
    sub0funcname = re.findall(sub0, mainfunc)[0] # 调用函数名
    sub = re.compile(sub0funcname + '=\{.*?};', re.S)
    f = open(filename)
    for a in islice(f, 5500, 5700): # 调用函数大概位置
        includefun2 = includefun2 + a
    f.close()
    subfunc = re.findall(sub, includefun2)[0].replace('\n', '') # 调用函数体

    js = mainfunc + subfunc + """
        function decode(sig) {{
            return {}(sig);
        }}
    """.format(mainfuncname)
    ctx = execjs.compile(js) # 函数 + 输出 打包

    return ctx.call("decode", sig)


def updateDB():
    url = 'https://www.youtube.com/watch?v=LXb3EKWsInQ&t=3s'
    html = askURL(url)
    basejs = parseHtml(html)
    jsfile = findBaseJs(basejs)
    writeFile(jsfile, filename)


def jsdecode(sig):
    return getDecoderFromLine(filename, sig)


if __name__ == '__main__':
    updateDB()