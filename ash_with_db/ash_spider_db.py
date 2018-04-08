# coding:utf-8

import re
import os
import time
import sqlite3
import threadpool
import requests as rq
import pypinyin as pp
from bs4 import BeautifulSoup


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Referer': 'http://m.ashvsash.com/',

    }

page_links = []
finish_num = 0
get_num = 0


def progressbar(num, num_all, num_block=40, blockstyle='█', space_len=2, line_feed=False):
    progress_str = '%s/%d |%s| %s%%' % (
        str(num).rjust(len(str(num_all))),
        num_all,
        blockstyle * int(num / num_all * num_block) + ' ' * space_len * (num_block - int(num / num_all * num_block)),
        str(int(num / num_all * 100)).rjust(len(str(num_all)))
    )
    if line_feed:
        print(progress_str)
    else:
        print(progress_str, end='')
        print('\b' * 200, end='', flush=True)


def get_links(url_num):
    global page_links, finish_num
    url = 'http://m.ashvsash.com/page/' + url_num
    r_n = rq.get(url, headers=headers)
    soup_n = BeautifulSoup(r_n.content, "html.parser")
    article = soup_n.find_all(class_='thumbnail')
    for each in article:
        page_links.append(each.a['href'])
    finish_num += 1


# 多线程获取资源
def get_links_mul(url):
    r = rq.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    end_page = soup.find(class_='extend')['href']
    end_num = int(end_page.split('/')[-1])
    url_nums = [str(i) for i in range(1, end_num + 1)]
    print('共', end_num, '页')
    pool = threadpool.ThreadPool(30)
    requests = threadpool.makeRequests(get_links, url_nums)
    [pool.putRequest(req) for req in requests]
    while finish_num < end_num:
        progressbar(finish_num, end_num)
        time.sleep(1)
    progressbar(finish_num, end_num, line_feed=True)
    pool.wait()


def get_source(url):
    # 获取资源
    global get_num
    try:
        r = rq.get(url, headers=headers)
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        # type_ = soup.find(rel="category tag").string
        title = soup.find('title').string.split('|')[0]
        p = r'(?:https*://pan\.baidu\.com/s/[A-z|0-9]{6,8})'
        links = re.findall(p, html)
        # print(title, type_, links)
        for i in range(len(links)):
            # 找密码
            a = html.find(links[i])
            b = html.find('密码', a, a + 255)
            psw = html[b:b + 8]
            psw = psw.partition('<')[0]
            # 合集找小标题
            title_l = ''
            if len(links) > 1:
                c = html.find('>', a + 1, a + 255)
                title_l = html[c:c + 64]
                if title_l != '' and title_l.find('>') != -1:
                    # title_l = title_l.split('>')[1].split('<')[0].strip()
                    temp = title_l.split('>')
                    title_l = (temp[1].split('<')[0].strip()) if '</strong' in temp\
                        else (temp[2].split('<')[0].strip())
                if title_l.endswith('点我'):
                    title_l = title_l[:-2]
            # if title_l != '':
            #     print(title_l, end='  ')
            # print(links[i] + '\t' + psw)
            # print(title, title_l, url, links[i], psw)
            conn = sqlite3.connect('movie.db')
            cursor = conn.cursor()
            cursor.execute('insert into dlinks (title, title2, p_link, d_link, pwd) values (?, ?, ?, ?, ?)', (title, title_l, url, links[i], psw))
            cursor.close()
            conn.commit()
            conn.close()
        # 设置已经获取
        conn = sqlite3.connect('movie.db')
        cursor = conn.cursor()
        cursor.execute('update movie set get=1 where p_link=?', (url,))
        cursor.close()
        conn.commit()
        conn.close()
        # print('获取成功 %s %s' % (title, url))
    except Exception as e:
        # print('获取失败 %s %s ' % (url, e))
        pass
    finally:
        get_num += 1


# 多线程获取资源
def get_source_mul(links):
    pool = threadpool.ThreadPool(30)
    requests = threadpool.makeRequests(get_source, links)
    [pool.putRequest(req) for req in requests]
    num_all = len(links)
    while get_num < num_all:
        progressbar(get_num, num_all)
        time.sleep(1)
    progressbar(get_num, num_all, line_feed=True)
    pool.wait()


def main(update=False, get_dlink=True):
    # update:是否更新数据， get_dlink:是否获取未获取的下载链接
    url = 'http://m.ashvsash.com'
    # 连接数据库
    conn = sqlite3.connect('movie.db')
    cursor = conn.cursor()
    tables = [each[1] for each in cursor.execute("select * from sqlite_master").fetchall()]
    # 建表语句
    if 'movie' not in tables:
        cursor.execute('create table movie (p_link varchar(30), get boolean)')
    if 'dlinks' not in tables:
        cursor.execute('create table dlinks (title varchar(30), title2 varchar(30), p_link varchar(30), d_link varchar(30), pwd varchar(10))')
    # 更新基础数据
    if update:
        print('正在更新，请稍侯......')
        get_links_mul(url)
        count = 0
        # global page_links
        for each in page_links:
            cursor.execute('select * from movie where p_link=?', (each,))
            if len(cursor.fetchall()) == 0:
                count += 1
                cursor.execute('insert into movie (p_link, get) values (?, 0)', (each,))
        conn.commit()
        print('更新完成，本次新增%d条数据。' % count)
    cursor.close()
    conn.commit()
    conn.close()
    # 获取未获取的下载链接
    if get_dlink:
        print('正在获取下载链接，请稍侯......')
        conn = sqlite3.connect('movie.db')
        cursor = conn.cursor()
        cursor.execute('select * from movie where get=0')
        links = [x[0] for x in cursor.fetchall()]
        cursor.close()
        conn.close()
        # print(links)
        # links = ['http://m.ashvsash.com/2018/02/15954/?', 'http://m.ashvsash.com/2017/01/1690/?']
        get_source_mul(links)
        print('获取完成，本次获取%d条数据。' % len(links))
    # conn = sqlite3.connect('movie.db')
    # cursor = conn.cursor()
    # print(cursor.execute('SELECT * FROM dlinks').fetchall())
    # cursor.close()
    # conn.close()


def search(string):
    string_pinyin = ''.join(pp.lazy_pinyin(string))
    string_pinyin_firstletter = ''.join([each[0] for each in pp.pinyin(string, style=pp.Style.FIRST_LETTER)])
    string_list = {string, string_pinyin, string_pinyin_firstletter}
    # print(string_list)
    conn = sqlite3.connect('movie.db')
    cursor = conn.cursor()
    data = list()
    for each in string_list:
        cursor.execute("SELECT * FROM dlinks WHERE title LIKE '%" + each + "%'")
        data += cursor.fetchall()
    if len(data) > 0:
        print('共查询到%d条数据：' % len(data))
        for i, each in enumerate(data):
            print('第%d条：' % (i + 1))
            print('%s %s %s %s\n' % (each[0], each[1], each[3], each[4]))
    else:
        print('未查询到。')
    cursor.close()
    conn.close()


if __name__ == '__main__':
    if not os.path.exists('movie.db'):
        print('未找到数据库，请先更新数据！')
    while True:
        choice = input('请选择：\n1.查询；\n2.更新数据。\n')
        if choice == '1' or choice.strip() == '':
            search(input('请输入搜索关键词:\n'))
        elif choice == '2':
            main(True, True)
        os.system('pause')
