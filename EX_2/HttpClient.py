'''
python program HttpClient
connects to socket and sends a GET request
and handles status code
'''


import socket
import sys
import re
import ssl

SIZE_OF_CHUNK = 4096


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
        match = re.match(r'^([^:]+):\s*(.+)$', line)
        if match:
            # putting parsed data from line as key and value of dictionary
            header_name, header_value = match.groups()
            headers[header_name] = header_value

    return headers

# open socket connect receive response close socket and return response
# from sample in Sakai
def connect(url):
    # try connecting
    # source Sakai receources with a bit of modification
    try:
        # split url in to host (eg. google.com) and path but limit to 3
        address = url.split('/',3)[-4:]

        # file name, because we want this to work for any file type,
        # I am trying to get file type dynamically
        # but this only works if url ends in file extension, else we will have to manualy add file extension
        full_path = address[3].split('/')
        file_name = full_path[len(full_path)-1]

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
        # additional headers found from SO
        # @ https://stackoverflow.com/questions/51806006/python-sockets-download-jpg-over-http
        request = "GET /" + address[3] + " HTTP/1.1\r\nHost: "+address[2]+"\r\n"\
                            "Accept: image/jpg,image/png,image/*,*/*;q=0.8\r\n" \
                            +"Accept-Language: en-US,en;q=0.9\r\n" +"Accept-Encoding: gzip, deflate, br\r\n\r\n"
        #request = "GET /"+address[3]+" HTTP/1.1\r\nHost: "+address[2]+"\r\n\r\n"
        # send request
        soc.send(request.encode())
        # receive response
        data = bytearray()
        while  True:
            chunk = soc.recv(SIZE_OF_CHUNK)
            data.extend(chunk)
            if not chunk:
                break
        # close socket
        soc.close()
        # splitting response to headers and body
        # SO here https://stackoverflow.com/questions/51806006/python-sockets-download-jpg-over-http
        headers= data.split(b'\r\n\r\n')[0]
        image = data[len(headers)+4:]
        #print(raw)
        f = open("./"+file_name, 'wb')
        soc.close()
        f.write(image)
        f.close()

        print("closed socket")
        return headers, image
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
#data = connect(url)
header,body = connect(url)
headers = parse_response(header)
# extract status code from response data
status_code = int(header.split(b' ',4)[1])
# parse headers from response data
#headers = parse_response(data)

# if we have a status code 301, we try on the new address we got from server response

while( status_code in range(299,400)):
    print("response :",status_code,"Redirecting to ", headers['Location'])
    # in this case we try to reconnect to any new address we receive fromserver
    # because when status code in the class 3 is returned, we have  location of resource sent as Location
    header,body = connect(headers['Location'])
    # we update status code until it becomes 200 or other none redirected status codes
    status_code = int(header.split(b' ',4)[1])
    # we also parse the headers from the response we get for further proccessing(redirecting)
    headers = parse_response(header)
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
        print(k," : ",v + ",")

else:
    print(status_code,"Information - dont give up nerd!! this is code 1, wait for response server is proccesing")
