import os
import sys
from pathlib import Path

import django

# ------------------------------ 环境 -------------------------------------


base_dir = Path(__file__).resolve().parent.parent
sys.path.append(base_dir)
print("scipt init")
# 加载配置文件，并启动一个虚拟的django服务
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saas.settings")
django.setup()

# ------------------------------ 脚本 ----------------------------------------

from web.models import PricePolicy

PricePolicy.objects.create(
    category=1,
    title="个人免费版",
    price=0,
    project_num=2,
    project_member=5,
    project_space=10,
    project_file_size=2,
)
print("价格策略初始化完毕")
