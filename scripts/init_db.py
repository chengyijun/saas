import os
import sys

import django

# ------------------------------ 环境 -------------------------------------

# 将项目目录task_platform加入到环境变量


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
print("scipt init")
# 加载配置文件，并启动一个虚拟的django服务
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saas.settings")
django.setup()

# ------------------------------ 脚本 ----------------------------------------

from web.models import PricePolicy

# UserInfo.objects.create(
#     username="abel",
#     password="123",
#     email="cyjmmy@qq.com",
#     phone="13178458956"
# )

# obj = UserInfo.objects.filter(pk=1).update(username="jock")
PricePolicy.objects.create(
    category=1,
    title="个人免费版",
    price=0,
    project_num=2,
    project_member=5,
    project_space=10,
    project_file_size=2,

)
