# coding=utf-8
from __future__ import unicode_literals
import os
import sys

__author__ = 'kirill'
from threading import Thread, Event
import select
import socket
import logging

from common import methods, russian_alphabet, translit_alphabet, PORT

LOG = logging.getLogger(__name__)

def start_server(port=PORT):
    s = socket.socket()
    s.bind(('localhost', port))
    LOG.info("Running on {0}".format(port))
    s.listen(0)
    thread_count = 0
    while 1:
        client_socket, client_address = s.accept()
        ConnectionThread(client_socket, client_address, thread_count).start()
        thread_count += 1

    s.close()


class ConnectionThread(Thread):
    def __init__(self, client_socket, client_address, thread_number):
        Thread.__init__(self)
        self._stop = Event()
        self.client_socket = client_socket
        self.client_address = client_address
        self.thread_number = thread_number

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        LOG.debug("Thread {0} started".format(self.thread_number))
        LOG.debug("{0}: Socket: {1}, address: {2}".format(self.thread_number, self.client_socket, self.client_address))
        client_buffer = ""
        newline = 0
        while 1:
            client_buffer += self.client_socket.recv(4096)
            newline = client_buffer.find('\n')
            if newline != -1:
                break

        header = client_buffer[:newline]
        client_buffer = client_buffer[newline + 1:]
        method, host, protocol = header.split(' ')
        if method not in methods:
            return

        host = host[7:]
        path_index = host.find('/')
        path = host[path_index:]
        host = host[:path_index]

        port_index = host.find(':')
        if port_index == -1:
            port = 80
        else:
            port = int(host[port_index+1:])
            host = host[:port_index]

        LOG.debug("{0} Open {1}:{2}/{3}".format(self.thread_number, host, port, path))

        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        LOG.debug("{0}: Open {1}".format(self.thread_number, address))

        target_socket = socket.socket(soc_family)
        target_socket.connect(address)
        target_socket.send('{0} {1} {2}\n'.format(method, path, protocol) + client_buffer)

        select_timeout = 3
        rlist = [target_socket, self.client_socket]

        count = 0
        while 1:
            count += 1
            ready_to_read, _, error = select.select(rlist, [], [], 3)
            if error:
                break
            if ready_to_read:
                for sock in ready_to_read:
                    data = sock.recv(4096)
                    if sock is target_socket:
                        out = self.client_socket
                        #if data:
                        #    print data
                    else:
                        out = target_socket
                    if data:
                        #data = data.replace('android'.encode('utf-8'), 'vedroid'.encode('utf-8'))
                        #for letter in russian_alphabet:
                        #    pass
                        #    #data = data.replace(letter.encode('utf-8'), translit_alphabet[russian_alphabet.index(letter)])
                        out.send(data)
                        count = 0
            if count > 3:
                break

        self.client_socket.close()
        target_socket.close()
        LOG.debug("Thread {0} finished".format(self.thread_number))


def main():
    def unhandled_exc_log(*exc_info):
        LOG.error("Unhandled exception: ", exc_info=exc_info)

    sys.excepthook = unhandled_exc_log
    logger = logging.getLogger()
    file_handler = logging.FileHandler(os.path.expanduser("~/translierator.log") ,'w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG if __debug__ else logging.WARNING)

    start_server()

if __name__ == '__main__':
    main()
