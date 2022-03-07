"""saas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from web import views

app_name = "web"
urlpatterns = [
    # 以下不登陆就能访问
    path("", views.IndexView.as_view(), name="index"),
    path("index/", views.IndexView.as_view(), name="index"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("sendsms/", views.SendSMSView.as_view(), name="sendsms"),
    path("smslogin/", views.SMSLoginView.as_view(), name="smslogin"),
    path("code/", views.CodeView.as_view(), name="code"),
    # path("showcode/", views.ShowCodeView.as_view(), name="showcode"),
    path("login/", views.LoginView.as_view(), name="login"),

    # 以下必须登陆才能访问
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("project/list/", views.ProjectListView.as_view(),
         name="project_list"),
    path("project/<int:project_id>/star/",
         views.ProjectStarView.as_view(),
         name="project_star"),
    path("project/<int:project_id>/unstar/",
         views.ProjectUnstarView.as_view(),
         name="project_unstar"),
    path(
        "project/<int:project_id>/",
        include([
            path("wiki/", views.WIKIView.as_view(), name="wiki"),
            path("wiki/add/", views.WIKIAddView.as_view(), name="wiki_add"),
            path("wiki/<int:wiki_id>/edit/",
                 views.WIKIEditView.as_view(),
                 name="wiki_edit"),
            path("wiki/<int:wiki_id>/show/",
                 views.WIKIShowView.as_view(),
                 name="wiki_show"),
            path("file/<int:parent_id>/",
                 views.FileView.as_view(),
                 name="file"),
            path("file/diradd/",
                 views.FileDirAddView.as_view(),
                 name="dir_add"),
            path("file/<int:file_id>/delete",
                 views.FileDeleteView.as_view(),
                 name="file_delete"),
            path("file/<int:file_id>/download",
                 views.FileDownloadView.as_view(),
                 name="file_download"),
            path("issues/", views.IssuesView.as_view(), name="issues"),
            path("issues/<int:issue_id>/detail/",
                 views.IssuesDetailView.as_view(),
                 name="issues_detail"),
            path("issues/<int:issue_id>/update/",
                 views.IssuesUpdateView.as_view(),
                 name="issues_update"),
            path("reply/<int:issue_id>/",
                 views.ReplyView.as_view(),
                 name="reply"),
            path("tree/", views.DirectoryTreeView.as_view(), name="tree"),
            path("wiki/mdupload/",
                 views.MduploadView.as_view(),
                 name="mdupload"),
            path("wiki/mddownload/<str:filename>/",
                 views.MddownloadView.as_view(),
                 name="mddownload"),

            path("invite/",
                 views.InviteView.as_view(),
                 name="invite"),

            path("dashboard/",
                 views.DashboardView.as_view(),
                 name="dashboard"),
            path("dashboard/charts/",
                 views.DashboardChartsView.as_view(),
                 name="dashboard_charts"),

            path("statistics/",
                 views.StatisticsView.as_view(),
                 name="statistics"),

            path("statistics/chart1/",
                 views.StatisticsChart1View.as_view(),
                 name="statistics_chart1"),
        ])),
    path("join/project/<str:code>/",
         views.JoinProjectView.as_view(),
         name="join_project"),
]
