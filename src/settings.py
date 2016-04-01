#!/usr/bin/env python
# -*- coding: utf-8 -*-

request_headers = {'user-agent':
                   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/49.0.2623.108 Safari/537.36'}
request_timeout = 10

proxy = {'http': 'proxy:port',
         'https': 'proxy:port'}
use_proxy = False

log_path = '../out'
posts_num = 4
