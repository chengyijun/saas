# -*- coding:utf-8 -*-
# 作者: 程义军
# 时间: 2022/3/1 14:50
from math import ceil


class Pagination:

    def __init__(self,
                 current_page: int,
                 total_count: int,
                 prefix_url: str,
                 query_param: dict,
                 page_size: int = 1):
        self.current_page = current_page
        self.prefix_url = prefix_url
        self.query_param = query_param
        self.page_size = page_size
        self.page_max = ceil(total_count / self.page_size)

        self.check_current_page(current_page)

    def check_current_page(self, current_page):
        if current_page > self.page_max:
            self.current_page = self.page_max
        elif self.current_page < 1:
            self.current_page = 1

    @property
    def start(self):
        return (self.current_page - 1) * self.page_size

    @property
    def end(self):
        return self.current_page * self.page_size

    def get_html(self):
        p2 = ""
        p1 = ""
        n1 = ""
        n2 = ""
        sy = ""
        wy = ""
        self.check_current_page(self.current_page)
        sy = f'<li><a href="{self.prefix_url}?page=1">首页</a></li>'
        if self.current_page > 2:
            p2 = f'<li><a href="{self.prefix_url}?page={self.current_page - 2}">{self.current_page - 2}</a></li>'
        if self.current_page > 1:
            p1 = f'<li><a href="{self.prefix_url}?page={self.current_page - 1}">{self.current_page - 1}</a></li>'
        cp = f'<li class="active"><a href="{self.prefix_url}?page={self.current_page}">{self.current_page}</a></li>'
        if self.current_page < self.page_max:
            n1 = f'<li><a href="{self.prefix_url}?page={self.current_page + 1}">{self.current_page + 1}</a></li>'
        if self.current_page + 1 < self.page_max:
            n2 = f'<li><a href="{self.prefix_url}?page={self.current_page + 2}">{self.current_page + 2}</a></li>'

        wy = f'<li><a href="{self.prefix_url}?page={self.page_max}">尾页</a></li>'
        return f"{sy}{p2}{p1}{cp}{n1}{n2}{wy}"
