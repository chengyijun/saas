# Create your views here.
import datetime
from io import BytesIO
from pathlib import Path
from pprint import pprint
from wsgiref.util import FileWrapper

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from django.views import View

from web.forms import RegisterModelForm, SMSLoginForm, LoginForm, ProjectModelForm, WikiModelForm, \
    FileRepositoryModelForm
from web.models import Transaction, PricePolicy, Project, ProjectUser, Wiki, FileRepository
from web.utils.func import send_sms, create_png, get_order


class SendSMSView(View):
    def get(self, request: WSGIRequest):
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
        form = RegisterModelForm(request, data=request.POST)
        is_valid = form.is_valid()
        if not is_valid:
            return JsonResponse({
                "status": False,
                "msg": "fail add",
                "errors": form.errors
            })
        instance = form.save()
        # 给注册用户 设置一个免费版的交易记录
        price_policy = PricePolicy.objects.filter(
            category=1).order_by("id").first()

        Transaction.objects.create(status=2,
                                   order=get_order(),
                                   user=instance,
                                   price_policy=price_policy,
                                   count=0,
                                   price=0,
                                   start_datetime=datetime.datetime.now())
        return JsonResponse({
            "status": True,
            "msg": "success add",
            "data": reverse("web:login")
        })


class SMSLoginView(View):
    def get(self, request: WSGIRequest):
        form = SMSLoginForm(request)
        return render(request, "smslogin.html", {"form": form})

    def post(self, request: WSGIRequest):
        form = SMSLoginForm(request, data=request.POST)
        is_valid = form.is_valid()
        if not is_valid:
            return JsonResponse({
                "status": False,
                "msg": "fail add",
                "errors": form.errors
            })
        return JsonResponse({
            "status": True,
            "msg": "success login",
            "data": reverse("web:index")
        })


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
        # 字典 新增键值对 有update()和setdefault()两种方法
        # 但尤其要注意的是 当setdefault()要添加的键值对在字典中已经存在的情况下 就不更新了
        request.session.update({"pcode": code})
        print(code)
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
            return JsonResponse({
                "status": False,
                "msg": "fail add",
                "errors": form.errors
            })
        return JsonResponse({
            "status": True,
            "msg": "success login",
            "data": reverse("web:index")
        })


class ProjectListView(View):
    def get(self, request: WSGIRequest):
        # 查询出我创建的项目
        own_projects = Project.objects.filter(
            creator=request.tracer.user).all()
        own_projects_star = []
        own_projects_nostar = []
        for p in own_projects:
            if p.star:
                own_projects_star.append(p)
            else:
                own_projects_nostar.append(p)
        # 查询出我参加的项目
        join_projects = ProjectUser.objects.filter(
            user=request.tracer.user).all()
        join_projects_star = []
        join_projects_nostar = []
        for p in join_projects:
            if p.star:
                join_projects_star.append(p)
            else:
                join_projects_nostar.append(p)
        form = ProjectModelForm(request)
        return render(
            request, "project_list.html", {
                "form": form,
                "own_projects": own_projects_nostar,
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
        form = WikiModelForm(request)
        return render(request, "wiki_add.html", {
            "form": form,
            "project_id": project_id
        })

    def post(self, request: WSGIRequest, project_id: int):
        form = WikiModelForm(request, data=request.POST)
        if not form.is_valid():
            return JsonResponse({"status": False, "errors": form.errors})

        form.instance.project = request.tracer.current_project
        form.save()
        return JsonResponse({"status": True})


class WIKIAddView(View):
    def get(self, request: WSGIRequest, project_id: int):
        form = WikiModelForm(request)
        return render(request, "wiki_form.html", {
            "form": form,
            "project_id": project_id,
            "wiki_id": 0
        })


class WIKIShowView(View):
    def get(self, request: WSGIRequest, project_id: int, wiki_id: int):
        form = WikiModelForm(request)
        wiki = Wiki.objects.filter(id=wiki_id).first()
        return render(
            request, "wiki_show.html", {
                "form": form,
                "project_id": project_id,
                "wiki": wiki,
                "wiki_id": wiki_id
            })


class WIKIEditView(View):
    def get(self, request: WSGIRequest, project_id: int, wiki_id: int):
        instance = Wiki.objects.filter(id=wiki_id).first()
        form = WikiModelForm(request, instance=instance)
        return render(request, "wiki_form.html", {
            "form": form,
            "project_id": project_id,
            "wiki_id": wiki_id
        })

    def post(self, request: WSGIRequest, project_id: int, wiki_id: int):
        instance = Wiki.objects.filter(id=wiki_id).first()
        form = WikiModelForm(request, instance=instance, data=request.POST)
        if not form.is_valid():
            return JsonResponse({"status": False, "errors": form.errors})
        form.save()
        return JsonResponse({"status": True})


class FileView(View):
    def get(self, request: WSGIRequest, project_id: int, parent_id: int):
        # 查询出所有文、文件夹
        if parent_id == 0:
            files = FileRepository.objects.filter(
                project=request.tracer.current_project,
                parent_id__isnull=True).all()
        else:
            files = FileRepository.objects.filter(
                project=request.tracer.current_project,
                parent_id=parent_id).all()
        # 构造面包屑导航
        breads = []
        if parent_id != 0:
            file: FileRepository = FileRepository.objects.filter(
                id=parent_id).first()
            breads.insert(0, {"id": parent_id, "name": file.name})
            current = file
            while current.parent:
                breads.insert(0, {
                    "id": current.parent.id,
                    "name": current.parent.name
                })
                current = current.parent
            else:
                breads.insert(0, {"id": 0, "name": "/"})
        else:
            breads.insert(0, {"id": 0, "name": "/"})

        form = FileRepositoryModelForm(request)

        return render(
            request, "file.html", {
                "project_id": project_id,
                "parent_id": parent_id,
                "files": files,
                "breads": breads,
                "form": form
            })

    def post(self, request: WSGIRequest, project_id: int, parent_id: int):

        file: InMemoryUploadedFile = request.FILES.get("file")
        uploads = Path("uploads")
        target_file = uploads.resolve().joinpath(file.name)
        with open(target_file, "wb") as f:
            for chuck in file.chunks():
                f.write(chuck)
        if parent_id == 0:
            parent_id = None
        data = {
            "file_type": 1,
            "name": file.name,
            "file_size": target_file.stat().st_size,
            "file_path": f"/{file.name}/",
            "parent_id": parent_id,
            "project": request.tracer.current_project,
            "update_user": request.tracer.user
        }

        # 将文件信息写入数据库
        FileRepository.objects.create(**data)
        return JsonResponse({"status": True})


class FileDirAddView(View):
    def post(self, request: WSGIRequest, project_id: int):
        post_dict = request.POST.dict()

        parent_id = int(post_dict.get(
            "parent_id")) if post_dict.get("parent_id") != '0' else None

        data = {
            "file_type": 2,
            "name": post_dict.get("name"),
            "file_size": 0,
            "file_path": f"/{post_dict.get('name')}/",
            "parent_id": parent_id,
            "project": request.tracer.current_project,
            "update_user": request.tracer.user
        }
        pprint(data)
        # 将文件信息写入数据库
        FileRepository.objects.create(**data)
        return JsonResponse({"status": True})


class FileDeleteView(View):
    def get(self, request: WSGIRequest, project_id: int, file_id: int):
        file: FileRepository = FileRepository.objects.filter(
            id=file_id).first()
        if file:
            parent_id = file.parent.id if file.parent else 0
            # 删除文件
            if file.file_type == 1:
                Path(f"uploads/{file.name}").unlink()
            # 删除文件 数据库记录
            file.delete()
            return redirect(
                reverse("web:file",
                        kwargs={
                            "project_id": project_id,
                            "parent_id": parent_id
                        }))


class FileDownloadView(View):
    def get(self, request: WSGIRequest, project_id: int, file_id: int):
        file: FileRepository = FileRepository.objects.filter(
            id=file_id).first()
        if file:
            file_path = Path(f"uploads/{file.name}")
            try:
                response = FileResponse(open(file_path, 'rb'))
                response['content_type'] = "application/octet-stream"
                # 告诉浏览器 文件的的大小 这很重要
                response['Content-Length'] = file_path.stat().st_size
                response[
                    'Content-Disposition'] = 'attachment; filename=' + escape_uri_path(
                        file.name)
                return response
            except Exception:
                raise Http404


class IssuseView(View):
    def get(self, request: WSGIRequest, project_id: int):
        return render(request, "issuse.html")


class ProjectStarView(View):
    def get(self, request: WSGIRequest, project_id: int):
        """我创建的项目 星标"""
        obj: Project = Project.objects.filter(creator=request.tracer.user,
                                              id=project_id,
                                              star=False).first()
        if obj:
            obj.star = True
            obj.save()
        """我参与的项目 星标"""
        obj2: ProjectUser = ProjectUser.objects.filter(
            user=request.tracer.user, project_id=project_id,
            star=False).first()
        if obj2:
            obj2.star = True
            obj2.create_time = datetime.datetime.now()
            obj2.save()
        return JsonResponse({})


class ProjectUnstarView(View):
    def get(self, request: WSGIRequest, project_id: int):
        """我创建的项目 取消星标"""
        obj: Project = Project.objects.filter(creator=request.tracer.user,
                                              id=project_id,
                                              star=True).first()
        if obj:
            obj.star = False
            obj.save()
        """我参与的项目 取消星标"""
        obj2: ProjectUser = ProjectUser.objects.filter(
            user=request.tracer.user, project_id=project_id,
            star=True).first()
        if obj2:
            obj2.star = False
            obj2.create_time = datetime.datetime.now()
            obj2.save()
        return JsonResponse({})


class DirectoryTreeView(View):
    def get(self, request: WSGIRequest, project_id: int):
        wikis = Wiki.objects.filter(project_id=project_id).all()
        datas = [model_to_dict(wiki) for wiki in wikis]
        return JsonResponse({"status": True, "datas": datas})


class MduploadView(View):
    def post(self, request: WSGIRequest, project_id: int):
        file: InMemoryUploadedFile = request.FILES.get("editormd-image-file")
        uploads = Path("uploads")
        target_file = uploads.resolve().joinpath(file.name)
        with open(target_file, "wb") as f:
            for chuck in file.chunks():
                f.write(chuck)

        # markdown-editor 消息通知的固定格式
        res = {
            "success": 1,
            "message": "success!",
            "url":
            f"http://127.0.0.1:8000/project/1/wiki/mddownload/{file.name}/"
        }
        response = JsonResponse(res)
        # 设置此消息头 放行frame的跨域问题 markdown-editor要求的
        response['X-Frame-Options'] = "ALLOWALL"
        return response


class MddownloadView(View):
    def get(self, request: WSGIRequest, project_id: int, filename: str):
        target_file = Path("uploads").resolve().joinpath(filename)
        return FileResponse(FileWrapper(open(target_file, "rb")))
