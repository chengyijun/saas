import re

from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.forms import RadioSelect

from web.models import UserInfo, Project, Wiki, FileRepository, Issues, Invite
from web.utils.func import encrypt


class BootstrapStyle:
    exclude_names = []

    def __init__(self, request: WSGIRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        # 为通过 ModelForm渲染的前端表单 添加属性
        for field in iter(self.fields):
            if field in self.exclude_names:
                continue
            self.fields[field].widget.attrs.update({
                'class':
                    'form-control',
                'placeholder':
                    f"请输入{self.fields[field].label}"
            })


class RegisterModelForm(BootstrapStyle, forms.ModelForm):
    ensure_password = forms.CharField(label="确认密码",
                                      max_length=64,
                                      widget=forms.PasswordInput)
    code = forms.CharField(label="验证码", max_length=4)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        exists = UserInfo.objects.is_user_exists_by_name(username)
        if exists:
            self.add_error("username", "用户名已存在")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")

        encrypt_password = encrypt(password)

        return encrypt_password

    def clean_ensure_password(self):
        password = self.cleaned_data.get("password")
        ensure_password = encrypt(self.cleaned_data.get("ensure_password"))
        if password != ensure_password:
            self.add_error("ensure_password", "两次密码输入不一致")

    def clean_phone(self):
        # print("clean_phone")
        phone = self.cleaned_data.get("phone")
        # print("phone", phone)
        findall = re.findall(r"^1[3-9][0-9]{9}$", phone)
        # print(findall)
        if not findall:
            self.add_error("phone", "手机号格式不正确")
        return phone

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code != self.request.session.get("code"):
            self.add_error("code", "验证码不正确")
            return code

    class Meta:
        model = UserInfo
        # fields = "__all__"
        fields = [
            "username", "password", "ensure_password", "email", "phone", "code"
        ]
        widgets = {
            "password": forms.PasswordInput,
        }


class SMSLoginForm(BootstrapStyle, forms.Form):
    phone = forms.CharField(label="手机号", max_length=11)
    code = forms.CharField(label="验证码", max_length=4)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        findall = re.findall(r"^1[3-9][0-9]{9}$", phone)
        if not findall:
            self.add_error("phone", "手机号格式不正确")

        # 验证手机号是否已注册
        user_object = UserInfo.objects.filter(phone=phone).first()
        if not user_object:
            self.add_error("phone", "请先注册")
        else:
            # 将登录用户 写入session
            self.request.session.setdefault("user_id", user_object.id)
        return phone

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code != self.request.session.get("code"):
            self.add_error("code", "验证码不正确")
            return code


class LoginForm(BootstrapStyle, forms.Form):
    username = forms.CharField(label="用户名", max_length=20)
    password = forms.CharField(label="密码",
                               max_length=20,
                               widget=forms.PasswordInput())
    code = forms.CharField(label="验证码", max_length=4)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not UserInfo.objects.filter(username=username).exists():
            self.add_error("username", "请先注册")
        return username

    def clean_password(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        encrypt_password = encrypt(password)
        user = UserInfo.objects.filter(username=username,
                                       password=encrypt_password).first()
        if not user:
            self.add_error("password", "密码错误")
        # 将登录用户 写入session
        else:
            self.request.session.update({"user_id": user.id})
            self.request.session.set_expiry(60 * 60 * 24)
        return encrypt_password

    def clean_code(self):
        code = self.cleaned_data.get("code")
        session_code_str = self.request.session.get("pcode")
        if code != session_code_str:
            self.add_error("code", "验证码不正确")
            return code


class ColorRadioSelect(RadioSelect):
    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'


class ProjectModelForm(BootstrapStyle, forms.ModelForm):
    exclude_names = ["color"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Project.objects.filter(name=name,
                                  creator=self.request.tracer.user).exists():
            self.add_error("name", "项目已存在")
        return name

    class Meta:
        model = Project
        fields = ["name", "color", "desc"]
        widgets = {
            'color': ColorRadioSelect(attrs={'class': 'color-radio'}),
            "desc": forms.Textarea
        }


class WikiModelForm(BootstrapStyle, forms.ModelForm):
    exclude_names = ["content"]

    def __init__(self, request: WSGIRequest, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        wikis: QuerySet = Wiki.objects.filter(
            project=request.tracer.current_project).all()
        datas = [("", "-- 请选择 --")]
        datas.extend(wikis.values_list("id", "title"))
        self.fields["parent"].choices = datas

    class Meta:
        model = Wiki
        fields = ["title", "content", "parent"]


class FileRepositoryModelForm(BootstrapStyle, forms.ModelForm):
    class Meta:
        model = FileRepository
        fields = ["name"]


class IssuesModelForm(BootstrapStyle, forms.ModelForm):
    exclude_names = ["desc"]

    def __init__(self, request: WSGIRequest, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        old_class = self.fields["assign"].widget.attrs.get("class")
        self.fields["assign"].widget.attrs[
            "class"] = f"{old_class} selectpicker"
        self.fields["assign"].widget.attrs["data-live-search"] = "true"

        old_class = self.fields["attention"].widget.attrs.get("class")
        self.fields["attention"].widget.attrs[
            "class"] = f"{old_class} selectpicker"
        self.fields["attention"].widget.attrs["data-live-search"] = "true"
        self.fields["attention"].widget.attrs["multiple"] = "multiple"
        self.fields["attention"].widget.attrs["data-actions-box"] = "true"
        self.fields["attention"].widget.attrs[
            "data-live-search-placeholder"] = "搜索关注人"
        #      data-actions-box="true"
        # data-live-search-placeholder="搜索"
        issues: QuerySet = Issues.objects.filter(
            project=request.tracer.current_project).all()
        datas = [("", "-- 请选择 --")]
        datas.extend(issues.values_list("id", "subject"))
        self.fields["parent"].choices = datas

    class Meta:
        model = Issues
        exclude = [
            "project", "creator", "create_datetime", "last_update_datetime"
        ]


class InviteModelForm(BootstrapStyle, forms.ModelForm):
    class Meta:
        model = Invite
        fields = ["period", "count"]
