# -*- coding:utf-8 -*-
# 作者: 程义军
# 时间: 2022/3/1 8:54
from django.template import Library

register = Library()


@register.simple_tag()
def get_id_just(id: int):
    return f"#{str(id).rjust(3, '0')}"
