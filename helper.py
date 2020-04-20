import os


def parse_request_urls(urls):
    # urls: GET /htmldog.com/examples/images1.html HTTP/1.1
    urls = urls.split()
    method = urls[0]  # get
    destaddress = urls[1][1:]  # /htmldog.com/examples/images1.html
    httpversion = urls[-1]
    tmp = destaddress.split('/')  # htmldog.com/examples/images1.html
    tmp = [item for item in tmp if item]
    # get url
    url = '/'.join(str(e) for e in tmp[1:])  # examples/images1.html
    hostname = tmp[:1][0]  # htmldog.com'
    # get filename
    filename = tmp[-1]  # images1.html
    return method, destaddress, httpversion, url, hostname, filename


def build_request_header(subpath, hostname):
    header = ''
    header += f'GET /{subpath} HTTP/1.1\r\n'
    header += f'Host: {hostname}\r\n'
    header += f'Connection: close\r\n'
    header += f'Upgrade-Insecure-Requests: 1\r\n'
    header += f'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:75.0) Gecko/20100101 Firefox/75.0\r\n'
    header += f'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n'
    header += f'Accept-Encoding: gzip, deflate, br\r\n'
    header += f'Accept-Language: en-US,en;q=0.9\r\n'
    header += f'MUIDB:1D3W2ADW1S32S1S41Q23B2Y2N1K3O\r\n'
    header += '\r\n'
    return header


# a socket disconnect when data returned is empty string
# means all data was done being sent.
def recv_parse_header(the_socket):
    all_data = b''
    while True:
        rev_data = the_socket.recv(4096)
        if not rev_data:
            break
        all_data += rev_data

    header = all_data.split(b'\r\n\r\n')[0].decode()

    return header, all_data


# save files to local disk
def save_files_to_local_disk(data, filename):
    path = f'cache'
    # if not directory
    if not os.path.exists(path):
        os.mkdir(path)

    with open(f'{path}/{filename}', 'wb') as file:
        file.write(data)

    return


def save_to_cache_dict(destaddress, filename, cache_dict):
    cache_address = 'cache/' + filename
    cache_dict.setdefault(destaddress, cache_address)
    return


def check_cache(destaddress, cache_dict):
    if destaddress in cache_dict.keys():
        return True
    else:
        return False


def read_cache_from_disk(destaddress, cache_dict):
    all_data = None
    with open(cache_dict[destaddress], 'rb') as f:
        all_data = f.read()

    header = all_data.split(b'\r\n\r\n')[0].decode()

    return header, all_data

