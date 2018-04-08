import threadpool
import time, random, os

al = []
num_ = 0
# progressStr = ''


def progressbar(num, num_all, num_block=50, blockstyle='█', space_len=2, line_feed=False):
    progress_str = '%s/%d |%s| %s%%' % (
        str(num).rjust(len(str(num_all))),
        num_all,
        blockstyle * int(num / 100 * num_block) + ' ' * space_len * (num_block - int(num / num_all * num_block)),
        str(int(num / num_all * 100)).rjust(len(str(num_all)))
    )
    if line_feed:
        print(progress_str)
    else:
        print(progress_str, end='')
        print('\b' * 200, end='', flush=True)


def a():
    # global progressStr
    pool = threadpool.ThreadPool(3)
    requests = threadpool.makeRequests(b, [i for i in range(5800)])
    [pool.putRequest(req) for req in requests]
    while num_ < 100:
        progressbar(num_, 100)
        time.sleep(1)
    progressbar(100, 100, line_feed=True)
    pool.wait()
    os.system('pause')


def b(i):
    global num_
    al.append(i)
    time.sleep(random.random())
    al.append(str(i)+'=')
    time.sleep(random.random())
    al.append(str(i)+'==')
    time.sleep(random.random())
    al.append(str(i)+'===')
    num_ += 1


def c():
    a()
    print(al)

c()