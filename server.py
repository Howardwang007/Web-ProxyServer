import socket, sys
from helper import parse_request_urls, build_request_header, check_cache, \
    recv_parse_header, save_files_to_local_disk, save_to_cache_dict, read_cache_from_disk

# to restore cache name and path
cache_dict = {}


def runServer(HOST, PORT):
    # CREAT a socket object, AF_INET: IPV4, SOCK_STREAM: TCP type
    socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # BIND local address e.g. 127.0.0.1:5050
    socketServer.bind((HOST, PORT))

    # LISTEN and set the number of backlog
    socketServer.listen(5)

    # Starting receive message from client
    print('WEB PROXY SERVER IS NOW LISTENING \n')

    return socketServer


def connection_handler(socketServer):
    """
    main function
    :param socketServer: socket object
    :return:
    """
    destination_hostname = None

    while True:
        connection, addr = socketServer.accept()
        # connection(socket object) send and receive data on the connection
        # addr is address bound to the socket on the other end of the connection.
        print(f'WEB PROXY SERVER CONNECTED WITH  {addr[0]}:{addr[1]}  \n')

        # Data received from client
        data = connection.recv(1024).decode().strip()
        print(f'MESSAGE RECEIVED FROM CLIENT:')
        print(data, '\n')
        print(f'END OF MESSAGE RECEIVED FROM CLIENT \n')

        # parse message header
        print(f'[PARSE MESSAGE HEADER]:')
        request_urls = data.split('\r\n')

        # parse first line
        method, destaddress, httpversion, url, hostname, filename = parse_request_urls(request_urls[0])
        if method == 'GET':
            # for 1st time to retrieve page
            if destination_hostname is None:
                destination_hostname = hostname
            else:  # for retrieve assets: images
                url = destaddress
                hostname = destination_hostname

            print(f' METHOD = {method}, DESTADDRESS = {destaddress}, HTTPVersion = {httpversion} \n')

            # # check if request content in the cache system
            if check_cache(destaddress, cache_dict):

                header, all_data = read_cache_from_disk(destaddress, cache_dict)
                print(f'[LOOK UP IN THE CACHE]: FOUND IN THE CACHE: FILE =cache/{filename}')
                # construct message to client
                new_header_method = header.split('\r\n')[0]
                new_header_content_length = '\n'.join(
                    [str(line) for line in header.split('\r\n') if 'Content-Length' in line])
                new_header_content_type = '\n'.join(
                    [str(line) for line in header.split('\r\n') if 'Content-Type' in line])
                print(f'RESPONSE HEADER FROM PROXY TO CLIENT: ')
                print(new_header_method)
                print(new_header_content_length)
                print(new_header_content_type)
                print(f'\nEND OF HEADER\n')
                # sent all message to browser
                connection.sendall(all_data)

            else:
                print(f'[LOOK UP IN THE CACHE]: NOT FOUND, BUILD REQUEST TO SEND TO ORIGINAL SERVER')
                print(f'[PARSE REQUEST HEADER]: HOSTNAME IS ', hostname)
                if url and filename:
                    print(f'[PARSE REQUEST HEADER]: URL IS ', url)
                    print(f'[PARSE REQUEST HEADER]: FILENAME IS ', filename)

                # Not in cache, build request to remote server
                print(f'\nREQUEST MESSAGE SENT TO ORGINAL SERVER:')
                request_header = build_request_header(url, hostname)
                print('\n'.join([str(line) for line in request_header.split('\r\n') if line]))
                print(f'\nEND OF MESSAGE SENT TO ORIGINAL SERVER\n')

                # request and get response from remote server
                header, all_data = None, None
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmpSocket:
                        tmpSocket.connect((hostname, 80))
                        tmpSocket.sendall(request_header.encode('utf-8'))
                        header, all_data = recv_parse_header(tmpSocket)
                        request_urls = header.split('\r\n')

                except (socket.timeout, socket.gaierror) as error:
                    sys.stdout.write(f'Error: {error}' + '\n')

                # output response
                print(f'RESPONSE HEADER FROM ORGINAL SERVER:')
                print('\n'.join([str(line) for line in header.split('\r\n') if line]))
                print(f'END OF HEADER\n')

                # write files to cache
                if ('302' not in request_urls[0]) and ('404' not in request_urls[0]):
                    save_to_cache_dict(destaddress, filename, cache_dict)
                    save_files_to_local_disk(all_data, filename)
                    print(f'WRITE FILE INTO CACHE: cache/{filename}\n')

                # construct message to client
                print(f'RESPONSE HEADER FROM PROXY TO CLIENT: ')
                print('\n'.join([str(line) for line in header.split('\r\n') if line]))
                print(f'END OF HEADER\n')

                # sent all message to browser
                connection.sendall(all_data)

        # if method it not get
        else:
            pass

        connection.close()  # close connection


if __name__ == '__main__':
    # server address
    # port to listen
    host = '127.0.0.1'
    port = 5005
    socket_Server = runServer(host, port)
    connection_handler(socket_Server)
