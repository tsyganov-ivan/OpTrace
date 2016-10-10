def some_method(a, b, c):
    if a and b or c:
        return True
    return False


#
# def some_meyhod2():
#     print('Hello!')
#
# some_method(1, 1, 0)

# some = lambda x: x**10
# for i in range(0):
#     if i<2:
#         continue
#     if i>=2:
#         print('Break')
#         break
#     print(i)
# else:
#     print(some(1))
#     print('No break')

# from tests.test_code2 import SomeClass2
#
# class SomeClass:
#     def __init__(self):
#         self.some = SomeClass2()
#
#     def printer(self, value):
#         print('SomeClass ->', value)
#         self.some.print(value)
#
#
# var = SomeClass()
# var.printer('Hello!')

# i = 0
# x = 12
# try:
#     z = i/x
# except ZeroDivisionError:
#     print('Exception')
# except UnicodeDecodeError:
#     print('Exc 2')
# else:
#     print('no exception')
# finally:
#     print('Finally')
#
# x = [i for i in range(10) if i>9]
# print(x)


# for i in [1, 3]:
#     if i == 5:
#         break
#     print('No')
# else:
#     print('Break')

# a = 1
# b = 1
# c = 1
#
# def some_method(a, b, c):
#     if a or b or c:
#         return True
#     return False
#
# some_method(a, b, c)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# a = 'test'
# b = [1,3,5]
# c = ['a', 'b', 'c']
# print('''
#     {}\n
#     {}\n
#     {}\n
# '''.format(
#     a,
#     ''.join(str(i) for i in b if not i%2),
#     ''.join(c)
# ))

# adf = False
# def test(a, b):
#     x = 0
#     if a>0:
#         x[::1]
#     return x
#
# test(0, 4)
#
#
# import yaml
# from collections import OrderedDict
#
# class OrderedLoader(yaml.Loader):
#     fetch_alias = yaml.scanner.Scanner.fetch_plain
#
#
# class OrderedDumper(yaml.Dumper):
#     pass
#
# OrderedDumper.add_representer(
#     OrderedDict,
#     lambda dumper, data: dumper.represent_mapping(
#         yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
#         data.items()
#     )
# )  # pragma: no cover
#
# OrderedLoader.add_constructor(
#     yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
#     lambda loader, node: OrderedDict(loader.construct_pairs(node))
# )
#
# x = yaml.load('a:1', Loader=OrderedLoader)
# # y = yaml.dump(x, Dumper=OrderedDumper)
