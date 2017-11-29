#what I have so far
import socket
import requests
import random

def sendRandomRequests(host, port):         
        try:  
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
                print('Failed to create socket')
                sys.exit()
           
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()
            
        s.connect((remote_ip , port))

        site = 'http://'+remote_ip+':'+port

        #request = "GET / HTTP/1.0\r\n\r\n"
        request = requests.get(site)

        put = site+'/put'
        post = site+'/post'
        delete = site+'/delete'
        head = site+'/get'
        options = site+'/get'
  
        for x in range(0, 10000):
            try:
                s.sendall(request)
            except socket.error:
                print('Send failed')
                sys.exit()
            reply = s.recv(4096)

            sel = random.choice(4)
            if sel == 0:
                r = requests.put(put)
            if sel == 1:
                r = requests.post(post)
            if sel == 2:
                r = requests.delete(delete)
            if sel == 3:
                r = requests.head(head)
            if sel == 4:
                r = requests.options(options)
