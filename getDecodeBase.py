# -*- coding: utf-8 -*-
# @Time : 2020/8/30 22:29
# @Author : KevinHoo
# @Site : 
# @File : getDecodeBase.py
# @Software: PyCharm 
# @Email : hu.rui0530@gmail.com
# @Note : get decode base and get encode func

import re
import time
import urllib.request

from bs4 import BeautifulSoup

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


def getDecoderFromLine(filename):

    from itertools import islice
    s = ""

    f = open("./base_history/base2020-09-05_16-48-02.js")
    for a in islice(f, 1400, 1500):
        s = s + a
    f.close()

    mainfunc = re.findall(func, s)[0]

    print(mainfunc)  # 主函数

    mainfuncname = re.findall(mainname, mainfunc)[0]
    print(mainfuncname)  # 主函数名

    sub0funcname = re.findall(sub0, mainfunc)[0]
    sub = re.compile(sub0funcname + '=\{.*?};', re.S)

    f = open(filename)
    for a in islice(f, 5500, 5700):
        s = s + a
    f.close()
    subfunc = re.findall(sub, s)[0].replace('\n', '')
    print(subfunc)  # 副函数

    import execjs

    sig = '6N6NPpl9RVpIj-77jp3F3oTSZ6FvGk0rlRrFZeHszUibBICIb5LMtsKEfjVCK-7oGAr8oQGOJsvSK7_qRGHuPBa1lVgIARw8JQ0qOAA'

    js = mainfunc + subfunc + """
        function decode(sig) {{
            return {}(sig);
        }}
    """.format(mainfuncname)

    ctx = execjs.compile(js)
    # print(ctx)

    print(ctx.call("decode", sig))


def main(update_time):
    url = 'https://www.youtube.com/watch?v=LXb3EKWsInQ&t=3s'
    basepath = './base_history/'
    filename = basepath + 'base' + update_time + '.js'
    html = askURL(url)
    basejs = parseHtml(html)
    jsfile = findBaseJs(basejs)
    writeFile(jsfile, filename)
    getDecoderFromLine(filename)


if __name__ == '__main__':
    update_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    main(update_time)
