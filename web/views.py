# Create your views here.
import datetime
from io import BytesIO

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from web.forms import RegisterModelForm, SMSLoginForm, LoginForm, ProjectModelForm
from web.models import Transaction, PricePolicy, Project, ProjectUser
from web.utils.func import send_sms, create_png, get_order


class SendSMSView(View):
    def get(self, request: WSGIRequest):
        # print("sms get")
        phone = request.GET.dict().get("phone")
        # code = random.randint(1000, 9999)
        code = "1111"
        send_sms(phone, code)
        request.session.setdefault("code", code)
        return JsonResponse({"phone": phone, "code": code})


class RegisterView(View):
    def get(self, request):
        form = RegisterModelForm(request)
        return render(request, "register.html", {"form": form})

    def post(self, request: WSGIRequest):
        # print("register post method")
        # print(request.POST.dict())
        form = RegisterModelForm(request, data=request.POST)
        is_valid = form.is_valid()
        if not is_valid:
            # print(form.errors)
            return JsonResponse({"status": False, "msg": "fail add", "errors": form.errors})
        instance = form.save()
        # 给注册用户 设置一个免费版的交易记录
        Transaction.objects.create(
            status=2,
            order=get_order(),
            user=instance,
            price_policy=PricePolicy.objects.filter(pk=1).first(),
            count=0,
            price=0,
            start_datetime=datetime.datetime.now()
        )
        return JsonResponse({"status": True, "msg": "success add", "data": reverse("web:login")})


class SMSLoginView(View):
    def get(self, request: WSGIRequest):
        form = SMSLoginForm(request)
        return render(request, "smslogin.html", {"form": form})

    def post(self, request: WSGIRequest):
        form = SMSLoginForm(request, data=request.POST)
        is_valid = form.is_valid()
        if not is_valid:
            # print(form.errors)
            return JsonResponse({"status": False, "msg": "fail add", "errors": form.errors})
        return JsonResponse({"status": True, "msg": "success login", "data": reverse("web:index")})


class IndexView(View):
    def get(self, request: WSGIRequest):
        return render(request, "index.html")


class LogoutView(View):
    def get(self, request: WSGIRequest):
        request.session.flush()
        return redirect(reverse("web:index"))


class CodeView(View):
    def get(self, request: WSGIRequest):
        img, code = create_png()
        request.session.delete("pcode")
        request.session.setdefault("pcode", code)
        f = BytesIO()
        img.save(f, "png")
        return HttpResponse(f.getvalue())


# class ShowCodeView(View):
#     def get(self, request: WSGIRequest):
#         return render(request, "showcode.html")


class LoginView(View):
    def get(self, request: WSGIRequest):
        form = LoginForm(request)
        return render(request, "login.html", {"form": form})

    def post(self, request: WSGIRequest):
        form = LoginForm(request, data=request.POST)
        is_valid = form.is_valid()
        if not is_valid:
            # print(form.errors)
            return JsonResponse({"status": False, "msg": "fail add", "errors": form.errors})
        return JsonResponse({"status": True, "msg": "success login", "data": reverse("web:index")})


class ProjectListView(View):
    def get(self, request: WSGIRequest):
        # 查询出我创建的项目
        own_projects = Project.objects.filter(creator=request.tracer.user).all()
        own_projects_star = []
        own_projects_nostar = []
        for p in own_projects:
            if p.star:
                own_projects_star.append(p)
            else:
                own_projects_nostar.append(p)
        # 查询出我参加的项目
        join_projects = ProjectUser.objects.filter(user=request.tracer.user).all()
        join_projects_star = []
        join_projects_nostar = []
        for p in join_projects:
            if p.star:
                join_projects_star.append(p)
            else:
                join_projects_nostar.append(p)
        form = ProjectModelForm(request)
        return render(request, "project_list.html",
                      {"form": form, "own_projects": own_projects_nostar,
                       "star_projects": own_projects_star,
                       "join_projects_star": join_projects_star,
                       "join_projects": join_projects_nostar
                       })

    def post(self, request: WSGIRequest):
        form = ProjectModelForm(request, data=request.POST)

        if not form.is_valid():
            return JsonResponse({"status": False, "errors": form.errors})
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})


class WIKIView(View):
    def get(self, request: WSGIRequest, project_id: int):
        return render(request, "wiki.html")


class FileView(View):
    def get(self, request: WSGIRequest, project_id: int):
        return render(request, "file.html")


class IssuseView(View):
    def get(self, request: WSGIRequest, project_id: int):
        return render(request, "issuse.html")


class ProjectStarView(View):
    def get(self, request: WSGIRequest, project_id: int):
        """我创建的项目 星标"""
        obj: Project = Project.objects.filter(creator=request.tracer.user, id=project_id, star=False).first()
        if obj:
            obj.star = True
            obj.save()
        """我参与的项目 星标"""
        obj2: ProjectUser = ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id,
                                                       star=False).first()
        if obj2:
            # print(obj2.project.id)
            obj2.star = True
            obj2.create_time = datetime.datetime.now()
            obj2.save()
        return JsonResponse({})


class ProjectUnstarView(View):
    def get(self, request: WSGIRequest, project_id: int):
        """我创建的项目 取消星标"""
        obj: Project = Project.objects.filter(creator=request.tracer.user, id=project_id, star=True).first()
        if obj:
            obj.star = False
            obj.save()
        """我参与的项目 取消星标"""
        obj2: ProjectUser = ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id,
                                                       star=True).first()
        if obj2:
            # print(obj2.project.id)
            obj2.star = False
            obj2.create_time = datetime.datetime.now()
            obj2.save()
        return JsonResponse({})
