import sqlite3

print(sqlite3.sqlite_version)

data = {"name": "abel", "age": 12}

# data.setdefault("name", "rox")
# print(data)
data.update({"name": "tank"})

print(data)
a = {'one': 1, 'two': 2, 'three': 3}
a.update({'one': 4.5, 'four': 9.3})
print(a)
