#what I have so far

import socket
import requests

    for host in hostlist:         
        for port in portList:
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
            request = "GET / HTTP/1.0\r\n\r\n"
            
            try:
                s.sendall(request)
            except socket.error:
                print('Send failed')
                sys.exit()
            reply = s.recv(4096)
