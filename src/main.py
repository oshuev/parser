#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base_parser import BaseParser
import db
import parsers


def _parsers():
    """
    get all classes (inherited from 'BaseParser')
    from 'parsers' module except 'BaseParser'
    """
    def _class(a):
        return parsers.__dict__.get(a)

    return (_class(a) for a in dir(parsers) if
            isinstance(_class(a), type(BaseParser)) and
            _class(a).__name__ != BaseParser.__name__)


def start_parsing():
    total_post_list = []
    for parser in _parsers():
        page_posts = parser().parse_page()
        total_post_list.extend(page_posts)
    db.save_to_mysql(total_post_list)
    # db.save_to_postgresql(total_post_list)
    # db.save_to_file(total_post_list)


if __name__ == "__main__":
    start_parsing()

