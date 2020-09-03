# -*- coding: utf-8 -*-
# @Time : 2020/9/3 9:41
# @Author : KevinHoo
# @Site : 
# @File : threadsDownload.py
# @Software: PyCharm 
# @Email : hu.rui0530@gmail.com

# import os, sys
from urllib.request import *
import threading
import time, datetime
import requests


# def download(url, savepath, threadnum, filesize, cachesize, startpos, endpos, _id):
#     vidDownPath = './video/'
#     audDownPath = './audio/'
#     if _id == threadnum - 1:
#         # 是最后一个线程，下载完剩余的全部
#         endpos = filesize
#     post = ''
#     if savepath == vidDownPath:
#         post = '.mp4'
#     elif savepath == audDownPath:
#         post = '.mp3'
#     download_size = endpos - startpos  # 总下载大小
#     download_num = download_size // cachesize  # 需要下载次数
#     # end_download_size = 0 if download_num*cachesize == download_size else download_size - download_num*cachesize #最后一次读取的大小，如果为0则代表总下载大小整除缓存数 (方便理解)
#     end_download_size = download_size % cachesize
#     # 请求访问文件
#     reqfile = Request(url, headers={"range": "bytes=%s-%s" % (startpos, endpos)})
#     reqfile = urlopen(reqfile)
#     print("[Thread-%s] 开始下载.下载范围:%s-%s." % (_id, startpos, endpos))
#     with open("%s-%s%s" % (savepath, _id, post), 'wb') as sf:
#         n = 0
#         while download_num > n:
#             sf.write(reqfile.read(cachesize))  # 读取并写入到文件中
#             n += 1
#         if not end_download_size == 0:  # 还有剩余部分
#             sf.write(reqfile.read(end_download_size))  # 读取写入
#     print("下载完成")
#
# def init(url, savepath, filesize):
#
#     threadnum = 2  # 开启线程数
#     cachesize = 4096  # 缓存大小
#
#     threadpool = []  # 线程池
#
#     thread_size = filesize // threadnum  # 每个线程下载的大小
#
#     for i in range(threadnum):  # 开启线程
#         x = Thread(target=download, args=(url, savepath, threadnum, filesize, cachesize, i * thread_size, (i + 1) * thread_size, i))
#         threadpool.append(x)
#         for t in threadpool:
#             t.start()
#         for t in threadpool:
#             t.join()


def thread(url, filename, downpath, file_size):

  vidDownPath = './video/'
  audDownPath = './audio/'
  post = ''

  if downpath == vidDownPath:
    post = '.mp4'
  elif downpath == audDownPath:
    post = '.mp3'

  headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.76 Safari/537.36",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6"
  }
  r = requests.get(url, headers=headers, stream=True, timeout=30)

  all_thread = 1
  # 获取视频大小
  # file_size = int(r.headers['content-length'])
  # 如果获取到文件大小，创建一个和需要下载文件一样大小的文件
  if file_size:
    fp = open(downpath + filename + post, 'wb')
    fp.truncate(file_size)
    print('视频大小：' + str(int(file_size / 1024 / 1024)) + "MB")
    fp.close()
  # 每个线程每次下载大小为5M
  size = 5242880
  # 当前文件大小需大于5M
  if file_size > size:
    # 获取总线程数
    all_thread = int(file_size / size)
    # 设最大线程数为10，如总线程数大于10
    # 线程数为10
    if all_thread > 10:
      all_thread = 10
  part = file_size // all_thread
  threads = []
  starttime = datetime.datetime.now().replace(microsecond=0)
  for i in range(all_thread):
    # 获取每个线程开始时的文件位置
    start = part * i
    # 获取每个文件结束位置
    if i == all_thread - 1:
      end = file_size
    else:
      end = start + part
    if i > 0:
      start += 1
    headers = headers.copy()
    headers['Range'] = "bytes=%s-%s" % (start, end)
    t = threading.Thread(target=Handler, name='线程-' + str(i),
               kwargs={'start': start, 'end': end, 'url': url, 'filename': downpath + filename + post, 'headers': headers})
    t.setDaemon(True)
    threads.append(t)
  # 线程开始
  for t in threads:
    time.sleep(0.2)
    t.start()
  # 等待所有线程结束
  for t in threads:
    t.join()
  endtime = datetime.datetime.now().replace(microsecond=0)
  print('用时：%s' % (endtime - starttime))


def Handler(start, end, url, filename, headers):
  tt_name = threading.current_thread().getName()
  print(tt_name + ' 启动')
  r = requests.get(url, headers=headers, stream=True)
  total_size = end - start
  downsize = 0
  startTime = time.time()
  with open(filename, 'r+b') as fp:
    fp.seek(start)
    var = fp.tell()
    for chunk in r.iter_content(204800):
      if chunk:
        fp.write(chunk)
        downsize += len(chunk)
        line = tt_name + '-downloading %d KB/s - %.2f MB， 共 %.2f MB'
        line = line % (
          downsize / 1024 / (time.time() - startTime), downsize / 1024 / 1024,
          total_size / 1024 / 1024)
        print(line, end='\r')


if __name__ == '__main__':
  url = input('input address(resouce)：')
  thread(url)
