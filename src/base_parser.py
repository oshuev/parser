#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod
import settings
import logging
from os import path


REQUEST_STATUS_OK = 200


class BaseParser(object):
    url = None
    encoding = None
    logger = None

    "need for @abstractmethod"
    __metaclass__ = ABCMeta

    @abstractmethod
    def _get_post_list(self, soup):
        return []

    @abstractmethod
    def _get_href(self, tag):
        return ''

    @abstractmethod
    def _get_title(self, tag):
        return ''

    @abstractmethod
    def _get_date(self, tag):
        return ''

    @staticmethod
    def _init_logger(log_level):
        if not BaseParser.logger:
            BaseParser.logger = logging.getLogger(__name__)

            logging_level = log_level if log_level else logging.INFO
            BaseParser.logger.setLevel(logging_level)

            file_encoding = 'utf-8'
            file_path = path.join(settings.log_path, 'parser.log')

            ch = logging.FileHandler(file_path, encoding=file_encoding)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            BaseParser.logger.addHandler(ch)

            'logging.ERROR'
            ch = logging.FileHandler(path.join(settings.log_path, 'parser_error.log'),
                                     encoding=file_encoding)
            ch.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            BaseParser.logger.addHandler(ch)

    @staticmethod
    def _get_proxy():
        return settings.proxy if settings.use_proxy else None

    def __init__(self, log_level=None):
        self.posts_num = settings.posts_num
        self._init_logger(log_level)

    @property
    def _class_name(self):
        return self.__class__.__name__

    def parse_page(self):
        post_list = []
        try:
            page_text, status = self._get_page()

            if status == REQUEST_STATUS_OK:
                post_list = self._parse_page(page_text)

                if post_list:
                    self.logger.info(u'OK: {0}'.format(self._class_name))
                else:
                    self.logger.warning(u'FAIL: {0}'.format(self._class_name))
            else:
                self.logger.warning(u'Request returned status: {0}'.format(status))
        except requests.RequestException as err:
            self.logger.error(u'RequestException: {0}\t{1}'.format(self._class_name, err.message))
        return post_list

    def _get_page(self):
        # can use 'fake_useragent.UserAgent instead 'settings.request_headers'
        r = requests.get(self.url,
                         headers=settings.request_headers,
                         proxies=self._get_proxy(),
                         timeout=settings.request_timeout,
                         )
        # r.encoding = 'utf-8'
        r.encoding = self.encoding if self.encoding else r.apparent_encoding
        return r.text, r.status_code

    def _collect_post_data(self, post):
        post_data = dict()
        try:
            href = self._get_href(post)
            title = self._get_title(post)
            date = self._get_date(post)

            if href and title and date:
                post_data = {
                    'href': self._get_href(post),
                    'title': self._get_title(post),
                    'date': self._get_date(post),
                }
            else:
                self.logger.error(u'ParseError: {0}\t Empty value returned in [{1}]'.format(
                    self._class_name, post,))
                return
        except (LookupError, AttributeError) as err:
            self.logger.error(u'ParseError: {0}\t[{1}] in [{2}]'.format(
                self._class_name, err.message, post,))
        return post_data

    def _parse_page(self, page):
        if not page:
            return []

        soup = BeautifulSoup(page, 'lxml')
        post_tag_list = self._get_post_list(soup)

        post_data_list = []
        for post_tag in post_tag_list:
            post_data = self._collect_post_data(post_tag)
            if post_data:
                post_data_list.append(post_data)
        return post_data_list
