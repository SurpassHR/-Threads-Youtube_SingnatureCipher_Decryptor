# -*- coding: utf-8 -*-
# @Time : 2020/8/29 9:26
# @Author : KevinHoo
# @Site :
# @Title : (Threads)Youtube SingnatureCipher Decryptor
# @File : main.py
# @Software: PyCharm
# @Email : hu.rui0530@gmail.com
import dictTraversal
import json
import configparser
from os import system
from re import compile, findall, S
from urllib import request
from time import strftime, localtime
from io import BytesIO
from gzip import GzipFile
from zlib import decompress, error, MAX_WBITS
from dictTraversal import get_dict_allkeys
from URLdecoder import seperatorOff
from decodeAllinOne import jsdecode, updateDB
from threadsDownload import thread

# 正则
urlFormat = compile(r'^https://www.youtube.com/watch\?v=.*|www.youtube.com/watch\?v=.*|youtube.com/watch\?v=.*')
mediaTitle = compile(r'<meta name="title" content="(.*?)">', S)
ytplayerCfg = compile(r'<script >var ytplayer.*?</script>', S)
streamingData = compile(r'"streamingData":({.*}),"playerAds"', S)
sigCipher = compile(r's=(.*?)&sp')
cipherUrl = compile(r'&url=(.*)')

# Unicode字符集
replace_dict = {
    r'\\\"': '',
    r'\\u0026': '&',
    r'\u0026': '&',
    r'\\"': "'",
    r'\"': r"'",
    r'\\': '',
    r'\/': '/',
    r'\u003c': '<',
    r'\u003e': '>',
    r'\u0027': "'"
}
# 错误的文件名
wrong_chara = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
# 请求头
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6",
    "Accept-Encoding": "gzip, deflate"
}
# 路径
cfgPath = './log/'
vidDownPath = './video/'
audDownPath = './audio/'
mergeVidPath = './merge/'
baseDownPath = './base_history/'
# 日志开关
logOn = False


def wConfig():
    config = configparser.ConfigParser()
    if not config.read('proxy_conf.ini'):
        config['proxy'] = {
            'isAgent': 'False',
            'httpProxy': ''
        }
        config['base'] = {
            'baseGot': 'False'
        }
        with open('proxy_conf.ini', 'w') as f:
            config.write(f)  # 不同于file.write()这是configparser自带的文件写入
    isAgent = config['proxy'].getboolean('isAgent')
    baseGot = config['base'].getboolean('baseGot')
    if not baseGot:
        updateDB()
        print('\nbase.js完成更新')
        updateTime = strftime("%Y-%m-%d", localtime())
        config['base'] = {
            'baseGot': 'True',
            'gotDate': updateTime
        }
        with open('proxy_conf.ini', 'w') as f:
            config.write(f)
    if not isAgent:
        print('\n未读取到代理配置')
        key, words = setProxy('')
        config['proxy'][key] = words
        config['proxy']['isAgent'] = 'True'
        with open('proxy_conf.ini', 'w') as f:
            config.write(f)  # 不同于file.write()这是configparser自带的文件写入
    elif isAgent:
        httpProxy = config['proxy']['httpProxy']
        setProxy(httpProxy)


# 设置代理
def setProxy(proxy):
    if proxy == '':
        http_proxy = input("\n第一次使用请输入你的代理地址服务器和端口号(xxx.xxx.xxx.xxx:xxxx):")
        system("set http_proxy=http://" + http_proxy)
        system("set http_proxys=http://" + http_proxy)
        system('chcp 65001')
        system('netsh winhttp show proxy')
        return "httpProxy", http_proxy
    else:
        print('\n已读取系统代理配置')


# url格式检测
def checkURL(url):
    if findall(urlFormat, url):
        return True
    elif url == '':
        print('\nurl is empty, input correct url')
        main()
    else:
        print('\nincorrect format url, input correct url')
        main()


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


# 过程文件保留
def write(file: str, filename: str) -> bool:
    """
    :param file:文件内Fv.容
    :param filename:文件名
    :return:None
    """
    cfgDirInit(cfgPath)

    logtime = strftime("%Y-%m-%d_%H-%M-%S", localtime())

    filename = logtime + '_' + filename
    f = open(cfgPath + filename, "w", encoding='utf-8')
    f.write(file)
    f.close()

    return True


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


# 请求原页面，timeout=30(s)
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


# 替换掉unicode字符的页面
def prettify(html):
    for item in replace_dict:
        html = html.replace(item, replace_dict[item])

    title = findall(mediaTitle, html)[0]

    if logOn:
        filename = 'pre_video_page.html'
        write(html, filename)

    return html, title


# 截取ytplayer中含有的流媒体信息
def process2Json(page):
    load = findall(streamingData, page)[0]
    write(load, '123.json')

    return load


# 装载json信息并转换为py中的字典
def getInfo(json_file):
    """
    :param json_file:
    :return: down_link_list[num]  下载链接
             rtn_len[num]  文件大小
    """

    down_link_list = []
    vid = []
    aud = []

    video_info_dict = json.loads(json_file)
    streaming_list = video_info_dict['adaptiveFormats']
    itag_list = get_dict_allkeys('itag', streaming_list)
    dictTraversal.rtnList = []
    rtn_len = get_dict_allkeys('contentLength', streaming_list)
    dictTraversal.rtnList = []

    for item in streaming_list:
        if findall('video/', str(item)):
            vid.append(item)
        elif findall('audio/', str(item)):
            aud.append(item)
    aud_start = len(vid)  # 音频链接的开始序号，默认下载最高品质的音频

    # 带有signatureCipher键的为带有加密的链接
    if 'signatureCipher' in str(streaming_list):
        print('\n这是签名加密过的视频，需进行链接解密')

        rtn_list = get_dict_allkeys('signatureCipher', streaming_list)
        dictTraversal.rtnList = []

        for sig in rtn_list:
            noseperator = seperatorOff(sig)  # 百分号解码
            sig = findall(sigCipher, noseperator)[0]  # 链接加密部分
            baseurl = findall(cipherUrl, noseperator)[0]  # sigcipher中视频源链接
            desig = jsdecode(sig)  # 按照js中的加密算法解码
            down_link_list.append(baseurl + '&sig=' + desig)  # 实际视频源链接

        print('\n-----------------------------------------------------------------------------------')
        # 只打印了视频信息
        for item in vid:
            for i in item:
                if i == 'signatureCipher':
                    continue
                print(i + ': ' + str(item[i]))
            print('\n-----------------------------------------------------------------------------------')

    # 普通视频链接
    else:
        print('\n这是未签名加密过的视频，可以直接下载')

        down_link_list = get_dict_allkeys('url', streaming_list)

        print('\n-----------------------------------------------------------------------------------')
        # 只打印了视频信息
        for item in vid:
            for i in item:
                if i == 'url':
                    continue
                print(i + ': ' + str(item[i]))
            print('\n-----------------------------------------------------------------------------------')

    itag = input('\n输入itag的值下载对应视频:')
    if itag not in itag_list:
        print("\n输入了错误的itag值")
    num = itag_list.index(int(itag))
    print('\n' + down_link_list[num])

    return down_link_list[num], down_link_list[aud_start], rtn_len[num]


def processTitle(title):
    for item in wrong_chara:
        if item in title:
            print('\n存在不符合命名规范的字符，已删除')
            title = title.replace(item, '')

    return title


# idm调用时输入的链接除expire之外的参数都无法输入
def allocateURL(down_link_list, title, rtnlen):
    print('\n' + title)
    cfgDirInit(vidDownPath)
    cfgDirInit(audDownPath)
    cfgDirInit(mergeVidPath)
    thread(down_link_list[0], title, vidDownPath, rtnlen)
    thread(down_link_list[1], title, audDownPath, rtnlen)
    # callIDMan.call(link, downPath, title)


def mergeVid(title):
    choice = input('\n是否要合并音视频(y/n):')
    if choice.upper() == 'Y':
        system('ffmpeg -i "{}" -i "{}" -vcodec copy -acodec copy "{}"'.format(
            vidDownPath+title+'.mp4', audDownPath+title+'.mp3', mergeVidPath+title+'.mp4'))


def main():
    wConfig()
    url = input("\ninput video address:")
    checkURL(url)
    html = askURL(url)
    pre_html, title = prettify(html)
    title = processTitle(title)
    json_file = process2Json(pre_html)
    cfgDirInit(baseDownPath)
    vid_down_link, aud_down_link, rtn_len = getInfo(json_file)
    allocateURL([vid_down_link, aud_down_link], title, int(rtn_len))
    mergeVid(title)


if __name__ == '__main__':
    main()
