from django.core.handlers.wsgi import WSGIRequest
from django.template import Library

from web.models import Project

register = Library()


@register.inclusion_tag("inclusion/all_project_list.html")
def all_project_list(request: WSGIRequest):
    # 获取用户最多可以创建的项目数
    max_count = request.tracer.policy.project_num
    # 获取用户已经创建了多少项目数
    total_count = Project.objects.filter(creator=request.tracer.user).count()
    is_show = total_count < max_count
    # print(total_count, max_count)
    return {"is_show": is_show}
