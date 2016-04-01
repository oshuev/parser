#!/usr/bin/env python
# -*- coding: utf-8 -*-

mysql_config = {
  'user': 'parser_user',
  'password': 'password',
  'host': '127.0.0.1',
  # 'database': 'test',
  # 'raise_on_warnings': True,
}

postgresql_config = {
    'dbname': 'new_db',
    'user': 'postgres',
    'host': '127.0.0.1',
    'port': 5439,
    'password': '',
}

# SQL_INSERT_POST = "INSERT INTO test.parser_tbl(datetime, url, title)" \
#                   "VALUES(%(datetime)s, %(url)s, %(title)s)"

# or use cur.callproc if pocudure is created in db
SQL_INSERT_POST = "INSERT INTO test.parse_tbl(datetime, url, title) " \
                  "VALUES(%s, %s, %s);"

# select posts for last two days
SQL_POSTGRESQL_SELECT_POSTS = "select title from test.parse_tbl " \
                              "where datetime > current_date-2;"

# https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL


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
        cur.execute(SQL_POSTGRESQL_SELECT_POSTS)
        titles = cur.fetchall()

        titles = [n[0].decode(conn.encoding) for n in titles]

        for post_data in post_list:
            if post_data['title'] not in titles:
                cur.execute(SQL_INSERT_POST, (post_data['date'], post_data['href'], post_data['title']))

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
        for post_data in post_list:
            data_post = {
                'datetime': post_data['date'],
                'url': post_data['href'],
                'title': post_data['title']
            }
            cur.execute(SQL_INSERT_POST, data_post)
        cur.commit()
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

# @staticmethod
# def _save_to_file(data_list):
#     with codecs.open('../out/output.txt', 'a', 'utf-8') as file_:
#         for data in data_list:
#             file_.write(data['href'] + '\n')
#             file_.write(data['title'] + '\n')
#             file_.write(data['date'] + '\n')
#             file_.write('-' * 70 + '\n')


"""
try:
  cnx = mysql.connector.connect(user='scott',
                                database='testt')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cnx.close()
"""

"""
import datetime
import mysql.connector

cnx = mysql.connector.connect(user='scott', database='employees')
cursor = cnx.cursor()

query = ("SELECT first_name, last_name, hire_date FROM employees "
         "WHERE hire_date BETWEEN %s AND %s")

hire_start = datetime.date(1999, 1, 1)
hire_end = datetime.date(1999, 12, 31)

cursor.execute(query, (hire_start, hire_end))

for (first_name, last_name, hire_date) in cursor:
  print("{}, {} was hired on {:%d %b %Y}".format(
    last_name, first_name, hire_date))

cursor.close()
cnx.close()
"""


"""
-- CREATE SCHEMA test AUTHORIZATION postgres;
-- CREATE TABLE test.parse_tbl
-- (
--     id SERIAL PRIMARY KEY NOT NULL,
--     datetime TIMESTAMP NOT NULL,
--     url VARCHAR(255) NOT NULL,
--     title TEXT NOT NULL
-- );

select * from test.parse_tbl;
-- insert INTO test.parse_tbl (datetime, url, title) values ('2016-02-29', 'dfgdg', 'dhdhd');
select title from test.parse_tbl
where datetime > current_date-2;

select current_date-1;
"""