import datetime

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from web.models import UserInfo, Transaction, PricePolicy, Project, ProjectUser


class Tracer:
    def __init__(self):
        self.user = None
        self.policy = None
        self.current_project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request: WSGIRequest):
        # print("全局认证中间件")
        # /index/
        # print(request.path_info)
        user_id = request.session.get("user_id", 0)
        user = UserInfo.objects.filter(id=user_id).first()
        # 判断用户是否登录
        # 已下白名单是免认证就可以访问的
        if not any([user, request.path_info in settings.AUTH_WHITE_LIST]):
            return redirect(reverse("web:login"))
        tracer = Tracer()
        tracer.user = user
        # print(tracer)
        request.tracer = tracer

        # 获取登录用户的价格策略 并绑定到 request.tracer对象上
        transaction_obj: Transaction = Transaction.objects.filter(user=request.tracer.user).order_by("-id").first()
        # 判断最后一笔交易记录 是否是付费版
        policy_obj = None
        if transaction_obj:
            policy_obj = transaction_obj.price_policy

            if policy_obj.category == 2:
                # 付费版
                if transaction_obj.end_datetime and transaction_obj.end_datetime < datetime.datetime.now():
                    # 已过期
                    policy_obj = PricePolicy.objects.filter(category=1).order_by("id").first()
            else:
                # 免费版
                policy_obj = PricePolicy.objects.filter(category=1).order_by("id").first()
        tracer.policy = policy_obj
        # if policy_obj:
        #     print("*********", policy_obj.project_num)

    def process_view(self, request: WSGIRequest, view_func, view_args, view_kwargs):

        project_id = view_kwargs.get("project_id")
        if request.path_info.startswith("/project/") and project_id:
            my_project: Project = Project.objects.filter(id=project_id, creator=request.tracer.user).first()
            join_project: ProjectUser = ProjectUser.objects.filter(project_id=project_id,
                                                                   user=request.tracer.user).first()

            if my_project:
                request.tracer.current_project = my_project
            elif join_project:
                request.tracer.current_project = join_project.project
            # else:
            # return redirect(reverse("web:project_list"))
        # print("当前进入项目", request.tracer.current_project)
