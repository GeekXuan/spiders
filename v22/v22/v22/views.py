import json
import random
import mysql.connector as ms
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from v22.settings import HOST, PORT, USER, PASSWORD, DATABASE


def welcome(request):
    return render(request, 'main.html')


def try_one(request):
    sql = '''SELECT t1.id, t1.code, t1.title, t1.director, t1.actor, t1.`date`, t1.`length`,
             t1.producer, t1.publisher, ifnull(t1.score, ''), t1.`type`, t1.img_url
             FROM main_info  AS t1 
             JOIN (SELECT ROUND(RAND() * ((SELECT MAX(id) FROM `main_info`)-(SELECT MIN(id) FROM `main_info`))
             +(SELECT MIN(id) FROM `main_info`)) AS id) AS t2 
             WHERE t1.id >= t2.id 
             ORDER BY t1.id LIMIT 1;
             '''
    sql_comment = '''select context from comment where info_id=%d and is_bit=1'''
    conn = ms.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()[0]
    cursor.execute(sql_comment % res[0])
    comments = cursor.fetchall()
    if comments:
        comments = comments[0]
    cursor.close()
    context = {
        'id_': res[0],
        'code': res[1],
        'title': res[2],
        'director': res[3],
        'actor': res[4],
        'date_': res[5],
        'length': res[6],
        'producer': res[7],
        'publisher': res[8],
        'score': res[9],
        'type_': res[10],
        'link': res[11],
        'comments': comments,
    }
    return render(request, 'info.html', context)


def info(request, info_id):
    sql = '''select id, code, title, director, actor, `date`, `length`,
             producer, publisher, ifnull(score, ''), `type`, img_url
             from main_info where id=%d''' % info_id
    sql_comment = '''select context from comment where info_id=%d and is_bit=1''' % info_id
    conn = ms.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()[0]
    cursor.execute(sql_comment)
    comments = cursor.fetchall()
    if comments:
        comments = comments[0]
    cursor.close()
    context = {
        'id_': res[0],
        'code': res[1],
        'title': res[2],
        'director': res[3],
        'actor': res[4],
        'date_': res[5],
        'length': res[6],
        'producer': res[7],
        'publisher': res[8],
        'score': res[9],
        'type_': res[10],
        'link': res[11],
        'comments': comments,
    }
    return render(request, 'info.html', context)


@csrf_exempt
def search(request):
    if request.method == 'GET' and request.is_ajax():
        draw = int(request.GET['draw'])
        start = int(request.GET['start'])
        length = int(request.GET['length'])
        info_id = request.GET.get('id_', None)
        code = request.GET.get('code', None)
        title = request.GET.get('title', None)
        actor = request.GET.get('actor', None)
        type_ = request.GET.get('type_', None)
        director = request.GET.get('director', None)
        producer = request.GET.get('producer', None)
        publisher = request.GET.get('publisher', None)
        score = request.GET.get('score', None)
        sql = '''select `id`, code, title, actor, `type`, `date`, ifnull(score, ''), director, producer, publisher
                 from main_info where'''
        sql_count = 'select count(id) from main_info where'
        sql += ' where'
        sql_count += ' where'
        if score != '-1':
            sql += ' score>=%d' % float(score)
            sql_count += ' score>=%d' % float(score)
        else:
        	sql += ' status=1'
            sql_count += ' status=1'
        if info_id:
            sql += ' and id=%d' % int(info_id)
            sql_count += ' and id=%d' % int(info_id)
        if code:
            sql += ' and code like "%%%s%%"' % code
            sql_count += ' and code like "%%%s%%"' % code
        if title:
            sql += ' and title like "%%%s%%"' % title
            sql_count += ' and title like "%%%s%%"' % title
        if actor:
            sql += ' and actor like "%%%s%%"' % actor
            sql_count += ' and actor like "%%%s%%"' % actor
        if type_:
            sql += ' and type like "%%%s%%"' % type_
            sql_count += ' and type like "%%%s%%"' % type_
        if director:
            sql += ' and director like "%%%s%%"' % director
            sql_count += ' and director like "%%%s%%"' % director
        if producer:
            sql += ' and producer like "%%%s%%"' % producer
            sql_count += ' and producer like "%%%s%%"' % producer
        if publisher:
            sql += ' and publisher like "%%%s%%"' % publisher
            sql_count += ' and publisher like "%%%s%%"' % publisher
        sql += ' limit %d,%d' % (start, start + length)
        conn = ms.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
        cursor = conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.execute(sql_count)
        count = cursor.fetchall()[0][0]
        cursor.close()
        conn.close()
        data = []
        for each in res:
            data.append({
                'id_': each[0], 'code': each[1], 'title': each[2], 'actor': each[3], 'type_': each[4],
                'date_': each[5], 'score': each[6], 'director': each[7], 'producer': each[8],
                'publisher': each[9],
                'operation': '<a class="btn btn-primary btn-xs" href="/info/%d/" target="_blank">查看详细</a>' % each[0]
            })
        data_json = {"draw": draw, "recordsTotal": count, "recordsFiltered": count, "data": data}
        return HttpResponse(json.dumps(data_json))
