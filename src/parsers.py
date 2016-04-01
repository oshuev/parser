#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base_parser import BaseParser
import re
from datetime import datetime, timedelta


def strip_text(func):
    def wrapped(*attr):
        val = func(*attr)
        return val.strip() if val else ''
    return wrapped


def date_to_datetime(func):
    def wrapped(*attr):
        text_date = func(*attr)
        try:
            date = datetime.strptime(text_date, '%d.%m.%Y')
            date_time = datetime.combine(date, datetime.now().time())
        except ValueError:
            date_time = ''
        return date_time
    return wrapped


def time_to_datetime(func):
    def wrapped(*attr):
        text_time = func(*attr)
        try:
            time = datetime.strptime(text_time, '%H:%M').time()
            date = datetime.today()
            # previous day
            if time > datetime.now().time():
                date = datetime.now() - timedelta(days=1)
            date_time = datetime.combine(date, time)
        except ValueError:
            date_time = ''
        return date_time
    return wrapped


# /-----------------------------------------------------------/


""" //- Class Template -//

class <ClassName>(BaseParser):
    url = <site_url>
    # encoding = <manual set site encoding>

    # def __init__(self):
    #     super(self.__class__, self).__init__(log_level)
    #     self.posts_num = <manual set number of posts>
    #     self.encoding = <manual set encoding>

    def _get_post_list(self, soup):
        return <return posts list>

    def _get_href(self, tag):
        return <return post href>

    def _get_title(self, tag):
        return <return post title>

    def _get_date(self, tag):
        return <return post date>
"""


# /-----------------------------------------------------------/


class HvylyaNetNewsDigest(BaseParser):
    url = "http://hvylya.net/category/news/digest/"
    __pattern_date = '(\d{2}\.\d{2}\.20\d{2})'

    def __init__(self, log_level=None):
        super(self.__class__, self).__init__(log_level)
        self.pattern = re.compile(self.__pattern_date)

    def _parse_date(self, string):
        res = self.pattern.search(string)
        return res.group(0) if res else ''

    def _get_post_list(self, soup):
        return soup.find_all(class_='post-content', limit=self.posts_num)

    def _get_href(self, tag):
        return tag.h2.a['href']

    def _get_title(self, tag):
        return tag.h2.a.contents[0]

    @date_to_datetime
    def _get_date(self, tag):
        date_string = tag.div.span.nextSibling.nextSibling.string
        return self._parse_date(date_string)


# /-----------------------------------------------------------/


class VestiUkrComPolitica(BaseParser):
    url = "http://vesti-ukr.com/politika"

    def _get_post_list(self, soup):
        tag = soup.find(class_='list-newsfeed')
        return tag.find_all('li', limit=self.posts_num)

    def _get_href(self, tag):
        return tag.a['href']

    @strip_text
    def _get_title(self, tag):
        return tag.a.contents[0]

    @time_to_datetime
    def _get_date(self, tag):
        return tag.find(class_='time').contents[0]


# /-----------------------------------------------------------/


class KorrespondentNet(BaseParser):
    url = 'http://korrespondent.net/'

    def _get_post_list(self, soup):
        tag = soup.find(class_='time-articles')
        return tag.find_all(class_='article', limit=self.posts_num)

    def _get_href(self, tag):
        return tag.find(class_='article__title').a['href']

    def _get_title(self, tag):
        # print tag
        return tag.find(class_='article__title').a.contents[-1]

    @time_to_datetime
    def _get_date(self, tag):
        return tag.find(class_='article__time').contents[0]


# /-----------------------------------------------------------/


if __name__ == '__main__':
    # for parser testing
    page_class = HvylyaNetNewsDigest

    log_on = True
    if log_on:
        import logging
        cls = page_class(logging.DEBUG)
    else:
        # log off
        cls = page_class(100)

    from db import save_to_file

    post_list = cls.parse_page()
    save_to_file(post_list)
