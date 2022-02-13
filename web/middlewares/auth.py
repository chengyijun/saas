from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from web.models import UserInfo


class Tracer:
    def __init__(self):
        self.user = None


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
