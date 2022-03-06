# import sqlite3
#
# print(sqlite3.sqlite_version)
#
# data = {"name": "abel", "age": 12}
#
# # data.setdefault("name", "rox")
# # print(data)
# data.update({"name": "tank"})
#
# print(data)
# a = {'one': 1, 'two': 2, 'three': 3}
# a.update({'one': 4.5, 'four': 9.3})
# print(a)

# targets = [0, 1, 2, 3]
# print(targets.pop(2))
# print(targets)
# print(targets.remove(2))
# print(targets)

# td = {"name": "abel", "age": 12, "gender": True}
# print(td.pop("age"))
# print(td)
# 字典没有remove()方法 只有pop()方法 而列表这个两个方法都有
# print(td.remove("age"))
# print(td)
# import time
#
# ts = time.time()
# print(ts)
# lt = time.localtime()
# print(lt)
# print(time.strftime("%Y-%m-%d", lt))
#
# print(datetime.datetime.now().date())
#
# print(time.mktime(lt) * 1000)
import time

a = "2018-04-27 17:49:00"

# 转化为数组

timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")

# 转换为时间戳

timeStamp = int(time.mktime(timeArray))  # 1524822540

print(timeArray)
print(timeStamp)
