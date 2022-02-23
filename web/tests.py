# Create your tests here.

# path = Path(__file__)
# print(path)
# print(path.parent)
# print(path.is_dir())
# print(path.is_file())

# path2 = Path("aaa")
# path2.mkdir()
from pathlib import Path

path3 = Path("abc.txt")
# # 默认为True 表示已经存在时候什么也不做
# # False 表示文件已存在就报错 FileExistsError
# path3.touch(exist_ok=False)

# 删除文件
# path3.unlink()
# 拼接文件路径
res = path3.resolve().joinpath("test")
print(res, type(res))

with open(path3, "r") as f:
    content = f.read()
    print(content)
