# -*- coding: utf-8 -*-
# @Time : 2020/8/30 22:29
# @Author : KevinHoo
# @Site : 
# @File : decodeAllinOne.py
# @Software: PyCharm 
# @Email : hu.rui0530@gmail.com
# @Note : get decode base and get encode func

import execjs
from re import findall, compile, S
from urllib import request
from time import strftime, localtime
from io import BytesIO
from gzip import GzipFile
from zlib import decompress, error, MAX_WBITS
from itertools import islice

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6",
    "Accept-Encoding": "gzip, deflate"
}
domain = "https://www.youtube.com"
script_pat = compile(r'<script src="(.*?)"')
func = compile(r'.*?function\(a\){a=a.split\(""\).*?return a.join\(""\)};')
mainname = compile('([0-9a-zA-Z]{2})=')
sub0 = compile(r'([0-9a-zA-Z]{2})\.')
filename = './base_history/base.js'
baseDownPath = './base_history/'


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
        print('\n' + path, '创建成功')
        return True
    else:
        print('\n' + path, '目录已存在')
        return False


def parse_html(res, html):
    encoding = res.info().get('Content-Encoding')
    if encoding == 'gzip':
        html = gzip(html)
    elif encoding == 'deflate':
        html = deflate(html)

    return html


def gzip(data):
    buff = BytesIO(data)
    f = GzipFile(fileobj=buff)

    return f.read().decode('utf-8')


def deflate(data):
    try:
        return decompress(data, -MAX_WBITS)
    except error:
        return decompress(data)


def askURL(url):
    req_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    try:
        req = request.Request(url=url, headers=headers)
        res = request.urlopen(req)
        html = res.read()
        html = parse_html(res, html)

        return html

    except Exception as e:
        print('\n请求失败，时间:{}'.format(req_time))
        print('\n失败原因:{}'.format(e))


def findBaseJs(html):
    basejs_src = ''
    backdrop = findall(script_pat, html)
    for link in backdrop:
        if 'base.js' in link:
            basejs_src = link
    url = domain + basejs_src
    jsfile = askURL(url)

    return jsfile


def writeFile(jsfile, basepath):
    with open(basepath, "w", encoding='utf-8') as f:
        f.write(jsfile)

    return '\n成功写入{}'.format(filename)


def getDecoderFromLine(sig):
    includefun1 = ""
    try:
        f = open(filename)
        for a in islice(f, 1400, 1500):  # 主函数大概位置
            includefun1 = includefun1 + a
        f.close()
    except Exception as e:
        print(e)
    mainfunc = findall(func, includefun1)[0]  # 主函数体
    mainfuncname = findall(mainname, mainfunc)[0]  # 主函数名

    includefun2 = ""
    sub0funcname = findall(sub0, mainfunc)[0]  # 调用函数名
    sub = compile(sub0funcname + '={.*?};', S)  # noqa: W605

    try:
        f = open(filename)
        for a in islice(f, 5000, 7000):  # 调用函数大概位置
            includefun2 = includefun2 + a
        f.close()
    except Exception as e:
        print(e)
    subfunc = findall(sub, includefun2)[0].replace('\n', '')  # 调用函数体

    js = mainfunc + subfunc + """
        function decode(sig) {{
            return {}(sig);
        }}
    """.format(mainfuncname)
    ctx = execjs.compile(js)  # 函数 + 输出 打包

    return ctx.call("decode", sig)


def updateDB():
    url = 'https://www.youtube.com/watch?v=t2pooIWrbVk&t=7s'
    html = askURL(url)
    jsfile = findBaseJs(html)
    cfgDirInit(baseDownPath)
    print(writeFile(jsfile, filename))


def jsdecode(sig):
    return getDecoderFromLine(sig)


if __name__ == '__main__':
    # updateDB()
    print(jsdecode('e=AZlvmBiZ=P6vM9bUmD1nSOzXm2rLsJoIQ2EjAMi-ahvAiAds9S8FTxEsHYnR-rteGA4PU'
                   '-mY7MM4DNwcmFCA0n2FKAhIQRw8JQ0qOAqOjqOjj'))
