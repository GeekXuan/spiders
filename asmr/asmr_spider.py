# coding:utf-8

import os
import re
import sqlite3
import threading
import threadpool
import subprocess
import requests as rq
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',

    }
lock = threading.Lock()

db_path = os.getcwd()

# 得到分类
def get_list(url):
    r = rq.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    nav = soup.find(class_='sitenav')
    num = 0
    mylist = []
    for each in nav.ul:
        if num >= 3:
            break
        if hasattr(each, 'li'):
            num += 1
            type_ = each.a.text
            for x in each:
                if hasattr(x, 'li') and x.li != None:
                    for y in x:
                        if hasattr(y, 'li'):
                            temp = re.findall(r'<a href="(.*)">(.*)</a>', str(y))
                            mylist.append((temp[0][1], temp[0][0], type_))
    return mylist


# 得到具体页面
def get_source(mylist):
    sourcelist = []
    for each in mylist:
        url = each[1]
        r = rq.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        if soup.find(class_='pagination pagination-multi'):
            pages = re.findall(r'共 (\d) 页', str(soup.find(class_='pagination pagination-multi').ul))[0][0]
            for page in (1, int(pages)):
                url_n = url + '/page/%d' % (page + 1)
                r_n = rq.get(url_n, headers=headers)
                soup_n = BeautifulSoup(r_n.content, "html.parser")
                articles_n = soup_n.find_all('article')
                for art in articles_n:
                    title = art.h2.text
                    link = art.a.get('href')
                    sourcelist.append([title, link, each[2], each[0]])
        articles = soup.find_all('article')
        for art in articles:
            title = art.h2.text
            link = art.a.get('href')
            sourcelist.append([title, link, each[2], each[0]])
    return sourcelist


# 得到下载链接
def get_link(sourcelist):
    for each in sourcelist:
        url = each[1]
        r = rq.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        d_link = soup.iframe.get('src').split('?url=')[-1]
        each.append(d_link)
    return sourcelist


# 下载
def download(info, pro=False):
    title = info[0]
    dir = info[2]
    d_link = info[4]
    # 命令行下载
    print('正在下载', title)
    # -o设置下载路径 -O设置文件名
    cmd = 'you-get -o %s -O %s %s' % (dir, title, d_link)
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro:
        # 显示过程
        os.system(cmd)
    else:
        # 不显示执行过程
        temp = output.stdout.read()
        # print(temp)
        if temp == b'':
            print('下载失败', title, d_link)
        else:
            print('下载成功', title, d_link)
            conn = sqlite3.connect(os.path.join(db_path, 'asmr.db'))
            cursor = conn.cursor()
            cursor.execute('update asmr set download=1 where title=?', (title,))
            cursor.close()
            conn.commit()
            conn.close()



# 多线程下载
def download_mul(prelist):
    func_var = []
    for each in prelist:
        func_var.append(([each, False], None))
    pool = threadpool.ThreadPool(20)
    requests = threadpool.makeRequests(download, func_var)
    [pool.putRequest(req) for req in requests]
    pool.wait()

# 主程序
def main(update=False, down=True, d_reset=False):
    # 连接数据库
    conn = sqlite3.connect('asmr.db')
    cursor = conn.cursor()
    # 建表语句
    # cursor.execute('create table asmr (title varchar(30), type varchar(20), author varchar(20), p_link varchar(50), d_link varchar(50), download boolean)')
    # 更新
    if update:
        print('正在更新数据，请稍侯......')
        url = 'https://www.asmrba.net/'
        final_list = get_link(get_source(get_list(url)))
        count = 0
        for data in final_list:
            cursor.execute('select * from asmr where title=?', (data[0],))
            if len(cursor.fetchall()) == 0:
                count += 1
                cursor.execute('insert into asmr (title, type, author, p_link, d_link, download) values (?, ?, ?, ?, ?, 0)', (data[0], data[2], data[3], data[1], data[4]))
        conn.commit()
        print('更新完成，本次新增%d条数据。' % count)
    # 全部重置为未下载
    if d_reset:
        cursor.execute('update asmr set download=0 where download=?', (1,))
        conn.commit()
    # 下载未完成的
    if down:
        cursor.execute('select * from asmr where download=?', (0,))
        prelist = cursor.fetchall()
        print('共有%d条数据未下载。' % len(prelist))
        os.chdir('H:')
        if not os.path.exists('downloads'):
            os.mkdir('downloads')
        os.chdir('downloads')
        download_mul(prelist)
    cursor.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main(1, 1, 0)
