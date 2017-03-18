import urllib.request as u
import os


def url_open(url):
    req = u.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    res = u.urlopen(req)
    html = res.read()
    return html
    
def make_folder(folder,remake):
    try:
        os.mkdir(folder)
        os.chdir(folder)
        print('文件夹%s不存在，将创建%s文件夹......' % (folder,folder))
    except:
        if(remake):
            folder_new = folder + '_1'
            print('文件夹%s已存在,将保存在%s文件夹 ......' % (folder,folder_new))
            make_folder(folder_new,True)
        else:
            os.chdir(folder)
            print('文件夹%s已存在 ......'% folder)

def get_page(url):
    html = url_open(url).decode('utf-8')
    a = html.find('current-comment-page')+23
    b = html.find(']',a)
    print(html[a:b])
    return html[a:b]

def find_images(url):
    html = url_open(url).decode('utf_8')
    img_addrs=[]
    a = html.find('img src=')
    while a != -1:
        b = html.find('.jpg',a,a+255)
        if b != -1:
            temp = html[a+9:b+4]
            if temp[0] == '/':
                temp = 'http:'+ temp
            if temp[0:4] == 'http' and temp[-4:-1] == '.jp':
                img_addrs.append(temp)
        else:
            b = a + 9
        a = html.find('img src=',b)
    for i in range(3):
        img_addrs.pop()
    return img_addrs
            

def save_images(addrs):
    for each in addrs:
        filename = each.split('/')[-1]
        with open(filename,'wb') as f:
            print('已保存：' + filename)
            img = url_open(each)
            f.write(img)


def downloads(folder = 'images',pages = 1):
    make_folder(folder,False)

    url = 'http://jandan.net/ooxx'
    page_num = int(get_page(url))
    index = page_num
    
    for i in range(pages):
        print('--------------------------------------------------')
        print('------------------page%s----------------------------' % page_num)
        if index!=page_num:
            os.chdir('..')
        page_n = 'page'+str(page_num)
        make_folder(page_n,True)
        url_new = url+'/page-'+str(page_num)+'#comments'
        imgs_addrs = find_images(url_new)
        save_images(imgs_addrs)
        print('--------------------------------------------------')
        page_num -= 1

if __name__=='__main__':
    folder = input('请输入要保存的文件夹名（不输入则默认为images）：')
    num = input('请输入要下载的页数（不输入则默认为1）：')
    if folder ==  '':
        folder = 'images'
    if num == '':
        num = '1'
    downloads(folder,int(num))
    print('下载完成......')
