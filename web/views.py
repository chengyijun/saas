# Create your views here.
import datetime
import json
from io import BytesIO
from pathlib import Path
from typing import Tuple
from uuid import uuid4
from wsgiref.util import FileWrapper

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet, Field
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from django.utils.safestring import mark_safe
from django.views import View

from web.forms import RegisterModelForm, SMSLoginForm, LoginForm, ProjectModelForm, WikiModelForm, \
    FileRepositoryModelForm, IssuesModelForm, InviteModelForm
from web.models import Transaction, PricePolicy, Project, ProjectUser, Wiki, FileRepository, IssuesType, Issues, \
    IssuesReply, UserInfo, Invite
from web.utils.func import send_sms, create_png, get_order
from web.utils.pagination import Pagination


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
        instance = form.save()
        objs = []
        obj1 = IssuesType(title="缺陷", project=instance)
        obj2 = IssuesType(title="任务", project=instance)
        obj3 = IssuesType(title="需求", project=instance)
        objs.append(obj1)
        objs.append(obj2)
        objs.append(obj3)
        IssuesType.objects.bulk_create(objs)
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
                # missing_ok=True 表示如果删除的文件不存在 则什么也不做 不报错
                Path(f"uploads/{file.name}").unlink(missing_ok=True)
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


class SelectFilter2:

    def __init__(self, name: str, datas: Tuple, request: WSGIRequest):
        self.name = name
        self.datas = datas
        self.request = request

    def __iter__(self):
        selected_datas = self.request.GET.getlist(self.name)

        yield mark_safe('<select class="c1" multiple="multiple" style="width:100%;">')

        for k, v in self.datas:
            selected = ""
            if str(k) in selected_datas:
                selected = "selected"
                try:
                    selected_datas.remove(str(k))
                except:
                    pass
            else:
                selected_datas.append(str(k))
            target_dict = self.request.GET.copy()
            target_dict._mutable = True
            target_dict.setlist(self.name, selected_datas)
            url = f"{self.request.path_info}?{target_dict.urlencode()}"

            yield mark_safe(f'<option {selected} value="{url}">{v}</option>')
            try:
                selected_datas.remove(str(k))
            except:
                pass
        yield mark_safe('</select>')


class SelectFilter:

    def __init__(self, name: str, datas: Tuple, request: WSGIRequest):
        self.name = name
        self.datas = datas
        self.request = request

    def __iter__(self):
        for k, v in self.datas:
            checked = ""
            selected_datas = self.request.GET.getlist(self.name)

            if str(k) in selected_datas:
                checked = "checked"
                selected_datas.remove(str(k))
            else:
                selected_datas.append(str(k))

            target_dict = self.request.GET.copy()
            target_dict._mutable = True
            target_dict.setlist(self.name, selected_datas)
            url = f"{self.request.path_info}?{target_dict.urlencode()}"

            yield mark_safe(
                f'<a id="id_{k}" href="{url}"><input  type="checkbox" {checked}/><label for="id_{k}">{v}</label></a>'
            )


class IssuesView(View):

    def get(self, request: WSGIRequest, project_id: int):
        objs = None
        pagination_html = ""
        # 查询出所有issues
        # 允许的查询参数
        query_dict = {}
        allowed_params = ["issues_type", "status", "priority", "assign", "attention"]
        for allowed_param in allowed_params:
            getlist = request.GET.getlist(allowed_param)
            if getlist:
                query_dict[f"{allowed_param}__in"] = getlist

        issues: QuerySet = Issues.objects.filter(project_id=project_id).filter(
            **query_dict)
        form = IssuesModelForm(request)
        if issues:
            query_param = request.GET
            current_page = int(query_param.get("page", 1))
            pagination = Pagination(current_page=current_page,
                                    total_count=issues.count(),
                                    prefix_url=request.path_info,
                                    query_param=query_param,
                                    page_size=10)

            objs = issues[pagination.start:pagination.end]

            pagination_html = pagination.get_html()

        # 构造 issues_type 二位元组
        issues_type_objs: QuerySet = IssuesType.objects.filter(
            project_id=project_id).all()
        issues_type_datas = tuple(issues_type_objs.values_list("id", "title"))

        # 构造 assign filter 的数据
        issues: QuerySet = Issues.objects.filter(project_id=project_id)
        assign_datas = list(set(issues.values_list("assign__id", "assign__username")))
        joins = ProjectUser.objects.filter(project_id=project_id)
        if joins:
            assign_datas.extend(list(set(joins.values_list("user_id", "user__username"))))
        assign_datas.remove((None, None))

        # 创建邀请的表单
        invite_form = InviteModelForm(request)

        return render(
            request, "issues.html", {
                "form":
                    form,
                "project_id":
                    project_id,
                "issues":
                    objs,
                "pagination_html":
                    pagination_html,
                "status_filter":
                    SelectFilter("status", Issues.status_choices, request),
                "priority_filter":
                    SelectFilter("priority", Issues.priority_choices, request),
                "issues_type_filter":
                    SelectFilter("issues_type", issues_type_datas, request),
                "assign_filter":
                    SelectFilter2("assign", assign_datas, request),
                "attention_filter":
                    SelectFilter2("attention", assign_datas, request),
                "invite_form": invite_form,
            })

    def post(self, request: WSGIRequest, project_id: int):
        form = IssuesModelForm(request, data=request.POST)
        if not form.is_valid():
            return JsonResponse({"status": False, "errors": form.errors})
        form.instance.project = request.tracer.current_project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})


class IssuesDetailView(View):

    def get(self, request: WSGIRequest, project_id: int, issue_id: int):
        instance = Issues.objects.filter(
            id=issue_id,
            creator__project=request.tracer.current_project).first()
        form = IssuesModelForm(request, instance=instance)
        return render(request, "issues_detail.html", {
            "form": form,
            "project_id": project_id,
            "issue_id": issue_id
        })


class IssuesUpdateView(View):

    def post(self, request: WSGIRequest, project_id: int, issue_id: int):
        post_dict = json.loads(request.body.decode("utf-8"))

        name = post_dict.get("name")
        value = post_dict.get("value")
        instance: Issues = Issues.objects.filter(
            id=issue_id, project_id=project_id).first()
        field: Field = Issues._meta.get_field(name)

        if name in ["subject", "desc", "start_date", "end_date"]:
            # 处理文本字段
            if not value:
                # 用户输入为空
                if not field.null:
                    # 字段不能为空
                    return JsonResponse({
                        "status": False,
                        "error": {
                            "name": name,
                            "value": "字段不能为空"
                        }
                    })
                setattr(instance, name, None)
                instance.save()
                content = f"{field.verbose_name}修改为了空值"
            else:
                # 用户输入不为空
                setattr(instance, name, value)
                instance.save()
                content = f"{field.verbose_name}修改为了{value}"
        elif name in ["priority", "status", "mode"]:
            # 处理CH字段
            # 判断 传递过来的choice文本是否合法
            for k, v in field.choices:
                if value == str(k):
                    # 合法
                    setattr(instance, name, value)
                    instance.save()
                    content = f"{field.verbose_name}更新为了 {v}"
                    break
            else:
                return JsonResponse({"status": False, "error": "数据非法"})
        elif name in ["issues_type", "module", "assign", "parent"]:
            if name == "assign":
                if not value:
                    if not field.null:
                        return JsonResponse({
                            "status": False,
                            "error": {
                                "name": name,
                                "value": "不能为空值"
                            }
                        })
                    setattr(instance, name, None)
                    instance.save()
                    content = f"{field.verbose_name}更新为 空值"
                else:
                    # 处理fk是assign的情况
                    target_obj = field.related_model.objects.filter(
                        id=int(value)).first()
                    if target_obj:
                        pus = ProjectUser.objects.filter(
                            project_id=project_id).all()
                        ids = [pu.user_id for pu in pus]
                        # 判断是不是项目创建者
                        if request.tracer.current_project.creator.id == target_obj.id:
                            setattr(instance, name, target_obj)
                            instance.save()
                            content = f"{field.verbose_name}更新为 {str(target_obj)}"
                        # 判断是不是项目参与者
                        elif target_obj.id in ids:
                            setattr(instance, name, target_obj)
                            instance.save()
                            content = f"{field.verbose_name}更新为 {str(target_obj)}"
                        else:
                            return JsonResponse({
                                "status": False,
                                "error": {
                                    "name": name,
                                    "value": "既不是创建者也不是参与者"
                                }
                            })
                    else:
                        return JsonResponse({
                            "status": False,
                            "error": {
                                "name": name,
                                "value": "非法数据"
                            }
                        })

            else:
                # 处理FK字段
                # 合法性校验
                if not value:
                    if not field.null:
                        return JsonResponse({
                            "status": False,
                            "error": {
                                "name": name,
                                "value": "不能为空值"
                            }
                        })
                    setattr(instance, name, None)
                    instance.save()
                    content = f"{field.verbose_name}更新为 空值"
                else:
                    rel_obj = field.related_model.objects.filter(
                        id=int(value), project_id=project_id).first()
                    if rel_obj:
                        if str(instance) == str(rel_obj):
                            return JsonResponse({
                                "status": False,
                                "error": {
                                    "name": name,
                                    "value": "不能选择自身"
                                }
                            })
                        setattr(instance, name, rel_obj)
                        instance.save()
                        content = f"{field.verbose_name}更新为 {str(rel_obj)}"
                    else:
                        return JsonResponse({
                            "status": False,
                            "error": {
                                "name": name,
                                "value": "数据非法"
                            }
                        })
        elif name in ["attention"]:
            # 处理M2M字段
            if not isinstance(value, list):
                return JsonResponse({
                    "status": False,
                    "error": {
                        "name": name,
                        "value": "数据非法"
                    }
                })
            if not value:
                instance.attention.set(value)
                content = f"{field.verbose_name}更新为 空值"

            else:
                instance.attention.set(value)
                names = [
                    str(UserInfo.objects.filter(id=int(v)).first())
                    for v in value
                ]
                names_str = ",".join(names)
                content = f"{field.verbose_name}更新为 {names_str}"
        # 创建一条操作记录
        reply_obj: IssuesReply = IssuesReply.objects.create(
            reply_type=1,
            issues=instance,
            content=content,
            creator=request.tracer.user)
        reply = model_to_dict(reply_obj)

        return JsonResponse({"status": True, "reply": reply})


class ReplyView(View):

    def get(self, request: WSGIRequest, project_id: int, issue_id: int):
        # 查询所有问题回复
        issues_replies: QuerySet = IssuesReply.objects.filter(
            issues_id=issue_id)
        return JsonResponse({
            "status": True,
            "replies": list(issues_replies.values())
        })

    def post(self, request: WSGIRequest, project_id: int, issue_id: int):
        post_dict = request.POST.dict()

        IssuesReply.objects.create(reply_type=2,
                                   content=post_dict.get("content"),
                                   creator=request.tracer.user,
                                   issues_id=issue_id,
                                   reply_id=post_dict.get("reply_id"))

        return JsonResponse({
            "status": True,
        })


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


class InviteView(View):
    def post(self, request: WSGIRequest, project_id: int):
        form = InviteModelForm(request, data=request.POST)
        if not form.is_valid():
            return JsonResponse({
                "status": False,
                "errors": form.errors
            })
        form.instance.project = request.tracer.current_project
        code = str(uuid4())
        form.instance.code = code
        form.instance.creator = request.tracer.user
        form.save()
        uri = reverse('web:join_project', kwargs={'code': code})
        invite_url = f"{request.scheme}://{request.get_host()}{uri}"
        return JsonResponse({
            "status": True,
            "invite_url": invite_url
        })


class JoinProjectView(View):
    def get(self, request: WSGIRequest, code: str):
        # code 不合法
        invite = Invite.objects.filter(code=code).first()
        if not invite:
            return render(request, "join_project.html", {"error": "邀请码不存在"})
        # code 过期失效
        max_datetime = invite.create_datetime + datetime.timedelta(minutes=invite.period)
        now = datetime.datetime.now()
        if max_datetime < now:
            return render(request, "join_project.html", {"error": "邀请码已经过期"})
        # 当前用户是创建者不需要加入
        if invite.project.creator == request.tracer.user:
            return render(request, "join_project.html", {"error": "您是该项目创建者 无需加入"})
        # 当前用户已经加入过 不能重复加入
        if ProjectUser.objects.filter(project=invite.project, user=request.tracer.user).exists():
            return render(request, "join_project.html", {"error": "您已经加入了该项目 无需重复加入"})
        # 项目成员 超过了 价格策略允许的最大成员数
        creator = invite.project.creator
        transaction = Transaction.objects.filter(user=creator).order_by("-id").first()
        allow_member = transaction.price_policy.project_member
        if invite.project.join_count > allow_member:
            return render(request, "join_project.html", {"error": "项目允许人数已达上限"})
        # 设置了要求次数
        if invite.count:
            if invite.count <= invite.use_count:
                # 已邀请人数 大于 设置的邀请次数
                return render(request, "join_project.html", {"error": "邀请码 邀请次数超限"})
        # use_count+=1
        # 更新邀请表的 已邀请人数
        invite.use_count += 1
        invite.save()
        # 更新 ProjectUser表
        ProjectUser.objects.create(project=invite.project, user=request.tracer.user)
        # 更新项目参与人数
        invite.project.join_count += 1
        invite.project.save()

        return render(request, "join_project.html", {"error": None})


class DashboardView(View):
    def get(self, request: WSGIRequest, project_id: int):
        return render(request, "dashboard.html", {})
