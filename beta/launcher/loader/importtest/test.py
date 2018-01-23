import importlib

hello = importlib.import_module('importme.hello')
print('printing hello')
print(hello)
try:
    getattr(hello, 'helloWorld')() # case sensitive
except AttributeError:
    print('cannot find pkg')

print(getattr(hello, 'sumOfList')([33,4,45,5,56,6,5,4,4,4,]))
print(getattr(hello, 'GLOBALVAL'))


# hello = importlib.import_module('..loader', package='loader')
# print('printing launcher')
# print(hello)
# getattr(hello, 'helloWorld')()