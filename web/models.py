from django.contrib import admin
from django.db import models
from django.db.models import Manager


class UserInfoManager(Manager):
    @staticmethod
    def is_user_exists_by_name(username: str):
        """
        根据用户名查询用户是否已存在
        :param username:
        :return:
        """
        return UserInfo.objects.filter(username=username).exists()


# Create your models here.
class UserInfo(models.Model):
    """用户"""
    username = models.CharField(verbose_name="用户名", max_length=20)
    password = models.CharField(verbose_name="密码", max_length=64)
    email = models.EmailField(verbose_name="邮箱")
    phone = models.CharField(verbose_name="手机号", max_length=11)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    objects = UserInfoManager()


class PricePolicy(models.Model):
    """价格策略"""
    category_choices = (
        (1, "免费版"),
        (2, "收费版"),
        (3, "其他"),
    )
    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)
    title = models.CharField(verbose_name="标题", max_length=32)
    price = models.PositiveIntegerField(verbose_name="价格")
    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_member = models.PositiveIntegerField(verbose_name="项目成员数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间")
    project_file_size = models.PositiveIntegerField(verbose_name="单文件大小")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Transaction(models.Model):
    """交易记录"""
    status_choices = (
        (1, "未支付"),
        (2, "已支付"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name="价格策略", to="PricePolicy", on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name="数量（年）", help_text="0表示无限期")
    price = models.IntegerField(verbose_name="实际支付价格")
    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Project(models.Model):
    """项目表"""
    COLOR_CHOICES = (
        (1, "#56b8eb"),
        (2, "#f28033"),
        (3, "#ebc656"),
        (4, "#a2d148"),
        (5, "#20bfa4"),
        (6, "#7461c2"),
        (7, "#20bfa3"),
    )
    name = models.CharField(verbose_name="项目名", max_length=32)
    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name="项目描述", max_length=255, null=True, blank=True)
    user_space = models.IntegerField(verbose_name="项目已使用空间", default=0)
    star = models.BooleanField(verbose_name="星标", default=False)
    join_count = models.SmallIntegerField(verbose_name="参与人数", default=1)
    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo", on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class ProjectUser(models.Model):
    """项目参与者"""
    user = models.ForeignKey(verbose_name="参与者", to="UserInfo", on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name="项目", to=Project, on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name="星标", default=False)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Wiki(models.Model):
    """wiki文章"""
    title = models.CharField(verbose_name="标题", max_length=32)
    content = models.TextField(verbose_name="内容")
    project = models.ForeignKey(verbose_name="所属项目", to=Project, on_delete=models.CASCADE)
    parent = models.ForeignKey(verbose_name="父级文章", to="self", on_delete=models.CASCADE, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return self.title


# 注册模型类 让django自带的后台可以进行管理
admin.site.register([UserInfo, PricePolicy, Transaction, Project, ProjectUser, Wiki])
