import socket

sock = socket.socket()
sock.bind(('localhost', 50008))
sock.listen(1)
print('listening...')
conn, addr = sock.accept()
with conn:
    print(f'Connected to {addr}')
    buff = ''
    while True:
        buff += conn.recv(1024).decode()
        new_msg = ''
        if not 'STOP' in buff:
            continue
        else:
            msgs = buff.split('-STOP')
            new_msg = msgs[0]
            buff = msgs[1]

            print(new_msg)
