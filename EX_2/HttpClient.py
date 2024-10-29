import socket
import sys
import re
import json

if(len(sys.argv) == 1):
    raise TypeError("Too few arguments\n")
    exit(1)

url = sys.argv[1]

def parse_response(resp):

    headers = {}
    response = resp.decode('utf-8',errors='ignore')
    for line in response.splitlines():
        header_match = re.match(r'^([^:]+):\s*(.+)$', line)
        if header_match:
            header_name, header_value = header_match.groups()
            headers[header_name] = header_value

    return headers

def connect(url):
    try:
        host, path = url.split('/',3)[-2:]
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host,80))
        
        request = "GET /"+path+" HTTP/1.1\r\nHost: "+host+"\r\n\r\n"
        soc.send(request.encode())
        data = soc.recv(2024)
        # close socket
        soc.close()
        # decode and print response
        #print(data)
        return data
    except:
        print("Ein Fehler ist aufgetreten, url : ", url) 


data = connect(url)
response = int(data.split(b' ',4)[1])
headers = parse_response(data)
while( response in range(299,400)):
    print("response :",response,"Redirecting to ", headers['Location'])
    data = connect(headers['Location'])
    response = int(data.split(b' ',4)[1])
    headers = parse_response(data)
    #print(headers)
    

if response >=500:
    print(response,"code 5, Server error")
    
elif response >= 400:
    print(response,"code 4, Client error")
    
elif response >= 200:
    print("response :",response," Get succeeded: printing headers \n\nHEADERS : {")
    i = 1;
    for (k, v) in headers.items():
        if i + 1 == len(headers):
            print("}\n")
            break
        i = i+1
        print(k,v + ",")
    
else:
    print(response,"Information - give up nerd!!")



