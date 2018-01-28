SERVICE = "test"
import requests
import sys

def pwn(ip):
    print(ip)
    return ip


if __name__ == '__main__':
    pwn(sys.argv(1))