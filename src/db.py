#!/usr/bin/env python
# -*- coding: utf-8 -*-

mysql_config = {
  'host': '127.0.0.1',
  'port': 3306,
  'database': 'test',
  'user': 'root',
  'password': '',
  # 'raise_on_warnings': True,
}

postgresql_config = {
    'host': '127.0.0.1',
    'port': 5439,
    'dbname': 'new_db',
    'user': 'postgres',
    'password': '',
}

# SQL_INSERT_POST = "INSERT INTO test.parser_tbl(datetime, url, title)" \
#                   "VALUES(%(datetime)s, %(url)s, %(title)s)"

# or use cur.callproc if pocudure is created in db
SQL_INSERT_POST = "INSERT INTO test.parser_tbl(datetime, title, url) " \
                  "VALUES(%s, %s, %s);"

# select posts for last two days
SQL_SELECT_POSTS = "select title from test.parser_tbl " \
                   "where (datetime > current_date-2);"


def save_to_postgresql(post_list):
    if not post_list:
        return
    try:
        import psycopg2
    except:
        pass

    conn = psycopg2.connect(**postgresql_config)
    cur = conn.cursor()
    try:
        cur.execute(SQL_SELECT_POSTS)
        titles = cur.fetchall()

        titles = [n[0].decode(conn.encoding) for n in titles]

        for post_data in post_list:
            if post_data['title'] not in titles:
                cur.execute(SQL_INSERT_POST, (post_data['date'], post_data['title'], post_data['href']))

                titles.append(post_data['title'])
        conn.commit()
    finally:
        if not cur.closed:
            cur.close()
        if not conn.closed:
            conn.close()


def save_to_mysql(post_list):
    if not post_list:
        return
    try:
        import mysql.connector
    except:
        pass

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    try:
        cur.execute(SQL_SELECT_POSTS)
        titles = cur.fetchall()

        # titles = [n[0].decode(conn.charset) for n in titles]
        titles = [n[0] for n in titles]

        for post_data in post_list:
            if post_data['title'] not in titles:
                cur.execute(SQL_INSERT_POST, (post_data['date'], post_data['title'], post_data['href']))

                titles.append(post_data['title'])
        conn.commit()
        # if exception rollback() not needed
    finally:
        cur.close()
        conn.close()


def save_to_file(post_list):
    from settings import log_path
    from datetime import datetime
    import codecs
    import os

    file_path = os.path.join(log_path, 'out.txt')
    with codecs.open(file_path, 'w', 'utf-8') as _file:
        for post_data in post_list:
            _file.write(post_data['href'] + '\n')
            _file.write(post_data['title'] + '\n')

            test_date = post_data['date']
            if isinstance(test_date, datetime):
                test_date = datetime.strftime(post_data['date'], '%Y.%m.%d %H:%M')
            _file.write(test_date + '\n')
            _file.write('-' * 70 + '\n')
