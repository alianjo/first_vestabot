from django.test import TestCase
from time import sleep

from threading import Thread

from .views import auto_search_sepehr, Person

# p1 = Person("John", 36)
# p1.myfunc()

obj = auto_search_sepehr()
s = obj.autoSearch()

print(f"s = {s}")


# def show(count, line):
#     partline = line.split(",")
#     sleep(3)
#     print(f'{count}: Origin: {partline[0]}, Destination: {partline[1]}')
#
#
# with open('sepehr/routes.txt', 'r') as file:
#     lines = file.readlines()
#     count = 1
#     for line in lines:
#         print(count)
#         t1 = Thread(target=show, args=(count, line))
#         t1.start()
#         count += 1
#     t1.join()
# t2 = Thread(target=show, args=("Two",))
# t2.start()
# t2.join()


# def show1(name):
#     print(f'Starting {name} ...')
#     sleep(3)
#     print(f'Finishing {name} ...')
#
# t1 = Thread(target=show1, args=("One",))
# t2 = Thread(target=show1, args=("Two",))
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# print("end")