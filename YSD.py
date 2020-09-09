# -*- coding: utf-8 -*-
# @Time : 2020/8/29 9:26
# @Author : KevinHoo
# @Site :
# @Title : (Threads)Youtube SingnatureCipher Decryptor
# @File : YSD.py
# @Software: PyCharm
# @Email : hu.rui0530@gmail.com

import re
import urllib.request
import time
import json
import URLdecoder
import threadsDownload

# import copy
# import dictTraversal
# import callIDMan


# 正则
urlFormat = re.compile(r'^https://www.youtube.com/watch\?v=.*|www.youtube.com/watch\?v=.*|youtube.com/watch\?v=.*')
mediaTitle = re.compile(r'<meta name="title" content="(.*?)">', re.S)
ytplayerCfg = re.compile(r'<script >var ytplayer.*?</script>', re.S)
streamingData = re.compile(r'"streamingData":{', re.S)
streamingdata1 = re.compile("'streamingData':{(.*)},'playbackTracking'", re.S)
streamingdata0 = re.compile("'streamingData':{(.*)},'playerAds'", re.S)
findVid = re.compile("'mimeType': 'video/mp4|'mimeType': 'video/webm", re.S)
findAud = re.compile("'mimeType': 'audio/mp4|'mimeType': 'audio/webm", re.S)
sigCipher = re.compile(r's=(.*?)&sp')
cipherUrl = re.compile(r'&url=(.*)')

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
}
# 错误的文件名
wrong_chara = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
# 请求头
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.76 Safari/537.36",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6"
}
# 路径
cfgPath = './log/'
vidDownPath = './video/'
audDownPath = './audio/'
baseDownPath = './base_history/'
# 日志开关
logOn = False


# url格式检测
def checkURL(url):
    if re.findall(urlFormat, url):
        return True
    elif url == '':
        print('url is empty, input correct url')
        main()
    else:
        print('incorrect format url, input correct url')
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
        print(path, '创建成功')
        return True
    else:
        print(path, '目录已存在')
        return False


# 过程文件保留
def write(file: str, filename: str) -> bool:
    """
    :param file:文件内Fv.容
    :param filename:文件名
    :return:None
    """
    cfgDirInit(cfgPath)

    logtime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    filename = logtime + '_' + filename
    f = open(cfgPath + filename, "w", encoding='utf-8')
    f.write(file)
    f.close()

    return True


# 请求原页面，timeout=30(s)
def askURL(url):
    global html

    res = urllib.request.Request(url=url, headers=headers)
    reqtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        req = urllib.request.urlopen(res, timeout=10)
        html = req.read().decode('utf-8')
        print('\n请求成功，请求时间是:{}\n'.format(reqtime))

    except Exception as e:
        print('\n请求失败，请求时间是:{}'.format(reqtime))
        print('失败原因:{}请检查网络\n'.format(e))
        main()

    if logOn:
        filename = 'oringin_video_page.html'
        write(html, filename)

    return html


# 替换掉unicode字符的页面
def prettify(html):
    for item in replace_dict:
        html = html.replace(item, replace_dict[item])

    title = re.findall(mediaTitle, html)[0]

    if logOn:
        filename = 'pre_video_page.html'
        write(html, filename)

    return html, title


# 截取含有ytplayer播放器信息的js脚本
def process2Js(pre_html):

    js_file = re.findall(ytplayerCfg, pre_html)[0]

    if logOn:
        filename = 'video_info_ytplayer_js.html'
        write(js_file, filename)

    return js_file


# 截取ytplayer中含有的流媒体信息
def process2Json(js_file):
    if not re.findall(streamingdata0, js_file):
        json_file = '{' + '"streamingData": {' + re.findall(streamingdata1, js_file)[0] + '}' + '}'
    else:
        json_file = '{' + '"streamingData": {' + re.findall(streamingdata0, js_file)[0] + '}' + '}'
    json_file = json_file.replace("'", '"')

    if logOn:
        filename = 'video_page_json.json'
        write(json_file, filename)

    return json_file


# 装载json信息并转换为py中的字典
def getInfo(json_file):
    down_link_list = []
    vid = []
    aud = []
    vidBitr = []
    audBitr = []
    mergeList = []
    lenList = []
    rtnLen = []

    video_info_dict = json.loads(json_file)
    streamingList = video_info_dict['streamingData']['adaptiveFormats']

    for item in streamingList:
        # print(item)
        if re.findall(findVid, str(item)):
            vid.append(item)
        elif re.findall(findAud, str(item)):
            aud.append(item)
    for item in vid:
        vidBitr.append(item['bitrate'])
        lenList.append(int(item['contentLength']))
    for item in aud:
        audBitr.append(item['bitrate'])
        lenList.append(int(item['contentLength']))

    vidSnumber = vidBitr.index(max(vidBitr))
    audSnumber = audBitr.index(max(audBitr)) + len(vidBitr)
    mergeList.append(vidSnumber)
    mergeList.append(audSnumber)
    rtnLen.append(lenList[vidSnumber])
    rtnLen.append(lenList[audSnumber])

    for num in mergeList:
        media = streamingList[int(num)]
        if 'signatureCipher' in media:
            noneSperator = URLdecoder.seperatorOff(media['signatureCipher'])
            sig = URLdecoder.decode(re.findall(sigCipher, noneSperator)[0])
            baseurl = re.findall(cipherUrl, noneSperator)[0]
            down_link_list.append(baseurl + '&sig=' + sig)
        elif 'url' in media:
            down_link_list.append(media['url'])

    return down_link_list, rtnLen


# idm调用时输入的链接除expire之外的参数都无法输入
def allocateURL(down_link_list, title, rtnlen):
    for item in wrong_chara:
        if item in title:
            print('存在不符合命名规范的字符，已删除')
            title = title.replace(item, '')
    print(title)
    cfgDirInit(vidDownPath)
    cfgDirInit(audDownPath)
    for i in range(len(down_link_list)):
        if i == 0:
            threadsDownload.thread(down_link_list[i], title, vidDownPath, rtnlen[i])
        else:
            threadsDownload.thread(down_link_list[i], title, audDownPath, rtnlen[i])
        # callIDMan.call(link, downPath, title)


def main():
    url = input("input video address:")
    checkURL(url)
    html = askURL(url)
    pre_html, title = prettify(html)
    js_file = process2Js(pre_html)
    json_file = process2Json(js_file)
    cfgDirInit(baseDownPath)
    down_link_list, rtnLen = getInfo(json_file)
    allocateURL(down_link_list, title, rtnLen)


if __name__ == '__main__':
    main()
