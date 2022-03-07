# -*- coding:utf-8 -*-
# 作者: 程义军
# 时间: 2022/3/7 11:30 

from django.template import Library

register = Library()


@register.simple_tag()
def show_project_user_space(capacity: int):
    if capacity < 1024:
        return f"{capacity} B"
    elif capacity < 1024 * 1024:
        return f"{capacity / 1024:.2f} KB"
    elif capacity < 1024 * 1024 * 1024:
        return f"{capacity / (1024 * 1024):.2f} M"
    else:
        return f"{capacity / (1024 * 1024 * 1024):.2f} G"
