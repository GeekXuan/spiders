import mysql.connector as ms

# USER = 'root'
# PWD = 'root'
# HOST = 'localhost'
HOST = '58.87.92.68'
USER = 'myuser'
PWD = 'password'
DB = 'v22_db'


def execute(func):
    def wrapper(*args):
        conn = ms.connect(host=HOST, user=USER, password=PWD, database=DB)
        cursor = conn.cursor()
        for sql in func(*args):
            try:
                cursor.execute(sql)
            except ms.errors.DataError as e:
                continue
            except (ms.errors.ProgrammingError, ms.errors.InterfaceError) as e:
                print(e)
                continue
        conn.commit()
        cursor.close()
        conn.close()

    return wrapper


def query_keyword():
    conn = ms.connect(host=HOST, user=USER, password=PWD, database=DB)
    cursor = conn.cursor()
    cursor.execute('SELECT `id`, `keyword` FROM keyword_info where `get` = 0 limit 100')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


def query_main():
    conn = ms.connect(host=HOST, user=USER, password=PWD, database=DB)
    cursor = conn.cursor()
    cursor.execute('SELECT `id`, `url` FROM main_info where `status` = 0 limit 100')
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


@execute
def insert_keyword(keywords):
    sql = "INSERT INTO `keyword_info` (`keyword`, `status`, `get`) VALUES ('%s', '0', '0')"
    sql_list = []
    for keyword in keywords:
        sql_list.append(sql % keyword)
    return sql_list


@execute
def update_keyword(info):
    sql_update_y = '''UPDATE `keyword_info` 
                      SET `page` = '%d', `count` = '%d', `status` = '1', `get` = '1' 
                      WHERE (`id` = '%d')'''
    sql_update_n = '''UPDATE `keyword_info` 
                      SET `status` = '0', `get` = '1' 
                      WHERE (`id` = '%d')'''
    sql_insert_info = '''INSERT INTO `main_info` (`keyword_id`, `url`, `status`) VALUES ('%d', '%s', '0')'''
    sql_list = []
    status = info[0]
    if status:
        page, count, urls, keyword_id = info[1:]
        for url in urls:
            sql_list.append(sql_insert_info % (keyword_id, url))
        sql_list.append(sql_update_y % (page, count, keyword_id))
    else:
        keyword_id = info[1]
        sql_list.append(sql_update_n % keyword_id)
    return sql_list


@ execute
def update_main(data):
    sql_update_main = '''UPDATE `main_info`
                         SET `code` = '%s', `title` = '%s', `director` = '%s',
                         `actor` = '%s', `date` = '%s', `length` = '%s',
                         `producer` = '%s', `publisher` = '%s', `score` = '%s',
                         `type` = '%s', `img` = '%s', `img_url` = '%s', status = 1
                         WHERE (`id` = '%d')'''
    sql_insert_comment = '''INSERT INTO `comment` (`info_id`, `context`, `is_bit`) VALUES ('%d', '%s', '%d');'''
    sql_list = []
    for comment in data['comments']:
        is_bit = 1 if 'magnet:?' in comment else 0
        sql_list.append(sql_insert_comment % (data['main_id'], comment, is_bit))
    sql_list.append(sql_update_main %
                    (data['code'], data['title'], data['director'], data['actor'], data['date'],
                     data['length']+'min', data['producer'], data['publisher'], data['score'],
                     data['type'], data['img'], data['img_url'], data['main_id'])
                    )
    return sql_list


@ execute
def update_main_404(main_id):
    sql_update_main = '''UPDATE `main_info`
                         SET `status` = 2
                         WHERE (`id` = '%d')'''
    return [sql_update_main % main_id]


if __name__ == '__main__':
    pass
