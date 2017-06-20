"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
import socket
import pandas as pd
import pickle
from asyncio import sleep

class Reader:

    # TODO: what server address to use?
    def __init__(self, server_address=('localhost', 10000), buffer_size=4096):
        self.server_address = server_address
        self.buffer_size = buffer_size

        # CSV file contains simulated and multiple versions of actual data
        # for a single product

        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now pretend that these values come from a system:
        df = pd.read_csv('../data/produktA-data.csv')
        # TODO: proper naming conventions for columns
        self.dataframe = df.drop(['Unnamed: 0'], axis=1)


    def run(self):
        print('connecting to {} on port {}'.format(*self.server_address))
        with socket.create_connection(self.server_address) as sock:
            for i, row in self.dataframe.iterrows():
                # TODO: split data into simulated and actual here and push them separately?
                data = pickle.dumps(row)
                # sock.sendall(row.to_json().encode())
                sock.sendall(data)
                sleep(0.5)
        print('the reader has finished sending data...')


if __name__ == '__main__':
    reader = Reader()
    reader.run()
