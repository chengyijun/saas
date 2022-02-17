from django.core.handlers.wsgi import WSGIRequest
from django.template import Library

from web.models import Project, ProjectUser

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


@register.inclusion_tag("inclusion/project_select.html")
def project_select(request: WSGIRequest):
    my_projects = Project.objects.filter(creator=request.tracer.user).all()
    join_projects = ProjectUser.objects.filter(user=request.tracer.user).all()
    current_enter_project = request.tracer.current_project
    current_enter_project_name = None
    if current_enter_project:
        current_enter_project_name = current_enter_project.name
    return {"my_projects": my_projects, "join_projects": join_projects,
            "current_enter_project_name": current_enter_project_name}
