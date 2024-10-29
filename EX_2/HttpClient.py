'''
python program HttpClient
connects to socket and sends a GET request
and handles status code
'''


import socket
import sys
import re
import ssl


# function to parse response from server
def parse_response(resp):
    print("parsing response...")
    # dictionary to hold parsed data
    headers = {}
    # decode response from byte array to string 
    # ignore errors because Jupyter complained about UTF-8 not being able to decode some chars 
    response = resp.decode('utf-8',errors='ignore')
    for line in response.splitlines():
        # Thanks google for this 
        header_match = re.match(r'^([^:]+):\s*(.+)$', line)
        if header_match:
            # putting parsed data from line as key and value of dictionary
            header_name, header_value = header_match.groups()
            headers[header_name] = header_value
    return headers

# open socket connect receive response close socket and return response
# from sample in Sakai
def connect(url):
    # try connecting
    # source Sakai receources with a bit of modification
    try:
        print("trying to connect...")
        # split url in to host (eg. google.com) and path but limit to 3
        address = url.split('/',3)[-4:]
        # lets assume port is 80 fro now
        port = 80
        # check if url is https or just http and we set port accordingly
        if address[0] == "https:":
            # we set our port to 443
            port = 443
            
        # create socket
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if port is 443, it means we have an https url
        if(port == 443):
            # so we wrap socket in an ssl context
            context = ssl.create_default_context()
            soc = context.wrap_socket(soc, server_hostname=address[2])
        
        # connect to socket at host address and port
        soc.connect((address[2],port))
        # request protocol for GET
        request = "GET /"+address[3]+" HTTP/1.1\r\nHost: "+address[2]+"\r\n\r\n"
        # send request
        soc.send(request.encode())
        # receive response
        data = soc.recv(2048)
        # close socket
        soc.close()
        print("closed socket")
        return data
    except:
        print("Sorry, error parsing url, make sure url has this format : http(s)://example.com/path/to/resource...")
        exit(1)

# check if we have enough arguments
if(len(sys.argv) == 1):
    raise TypeError("Too few arguments\n")
    exit(1)
# get url from params
url = sys.argv[1]
# get response from socket
data = connect(url)
# extract status code from response data
status_code = int(data.split(b' ',4)[1])
# parse headers from response data
headers = parse_response(data)

# if we have a status code 301, we try on the new address we got from server response
while( status_code in range(299,400)):
    print("response :",status_code,"Redirecting to ", headers['Location'])
    # in this case we try to reconnect to any new address we receive fromserver
    # because when status code in the class 3 is returned, we have  location of resource sent as Location
    data = connect(headers['Location'])
    # we update status code until it becomes 200 or other none redirected status codes
    status_code = int(data.split(b' ',4)[1])
    # we also parse the headers from the response we get for further proccessing(redirecting)
    headers = parse_response(data)
    #print(headers)
    

if status_code >=500:
    print(status_code,"code 5, Server error")
    
elif status_code >= 400:
    print(status_code,"code 4, Client error")
    
elif status_code >= 200:
    print("response :",status_code," Get succeeded: printing headers \n\nHEADERS : {")
    i = 1
    for (k, v) in headers.items():
        if i + 1 == len(headers):
            print("}\n")
            break
        i = i+1
        print(k,":",v + ",")
    
else:
    print(status_code,"Information - dont give up nerd!! this is code 1, wait for response server is proccesing")
