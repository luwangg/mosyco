import socket
import pandas as pd
import pickle

class Inspector:
    def __init__(self, server_address=('localhost', 10000), buffer_size=4096):
        self.server_address = server_address
        self.buffer_size = buffer_size

    def dummy(self):
        return

    def run(self):
        print('listening on port {}'.format(self.server_address[1]))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.server_address)
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(self.buffer_size)
                    if not data: break
                    # print(row)
                    obj = pickle.loads(data)
                    print(obj)
                    # do work here
                    # conn.sendall(row)

if __name__ == '__main__':
    inspector = Inspector()
    inspector.run()
