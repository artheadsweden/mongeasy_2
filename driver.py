from mongeasy import create_document_class, DESCENDING, ASCENDING
import random

User = create_document_class('User', 'users')
# names = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve', 'Frank', 'Grace', 'Hannah', 'Ivan', 'Judy', 'Karl', 'Linda', 'Mike', 'Nancy', 'Oscar', 'Peggy', 'Quinn', 'Ralph', 'Steve', 'Tina', 'Ursula', 'Victor', 'Wendy', 'Xavier', 'Yvonne', 'Zach']
# for name in names:
#     User(name=name, age=random.randint(18, 65)).save()
# user_dict = {'name': 'Wokie', 'age': 56}
# User(user_dict).save()

# users = User.all(limit=4, skip=2)
# for user in users:
#     print(user.name)

# users = User.all(sort=[('age', ASCENDING)])
# for user in users:
#     print(user)

# user = User.find_one({'name': 'Wokie'})
# user.age = 57
# print(user.has_changed())

users_dicts = [
    {'name': 'Alice', 'age': 18},
    {'name': 'Bob', 'age': 19},
    {'name': 'Charlie', 'age': 20},
    {'name': 'Dave', 'age': 21},
    {'name': 'Eve', 'age': 22},
    {'name': 'Frank', 'age': 23},
    {'name': 'Grace', 'age': 24},
    {'name': 'Hannah', 'age': 25},
    {'name': 'Ivan', 'age': 26},
    {'name': 'Judy', 'age': 27},
    {'name': 'Karl', 'age': 28},
    {'name': 'Linda', 'age': 29},
    {'name': 'Mike', 'age': 30},
    {'name': 'Nancy', 'age': 31},
    {'name': 'Oscar', 'age': 32},
    {'name': 'Peggy', 'age': 33},
    {'name': 'Quinn', 'age': 34},
    {'name': 'Ralph', 'age': 35},
    {'name': 'Steve', 'age': 36},
    {'name': 'Tina', 'age': 37},
    {'name': 'Ursula', 'age': 38},
    {'name': 'Victor', 'age': 39},
    {'name': 'Wendy', 'age': 40},
    {'name': 'Xavier', 'age': 41},
    {'name': 'Yvonne', 'age': 42},
    {'name': 'Zach', 'age': 43},
]
#User.insert_many(users_dicts)

# users = User.find({'age': {'$gt': 30}})
# print(len(users))
# User.delete({'age': {'$gt': 30}})
# users = User.find({'age': {'$gt': 30}})
# print(len(users))
u = User.find_by_id('642409e87f768856f3b50841')
u.age = 99
print(u)
u.reload()
print(u)