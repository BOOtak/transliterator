# coding=utf-8
from __future__ import unicode_literals
import os
import requests
import sys
import threading

__author__ = 'kirill'
from threading import Thread, Event
import select
import socket
import logging

from common import russian_alphabet, translit_alphabet, PORT, connection_timeout, max_attempts, methods

LOG = logging.getLogger(__name__)


def start_server(port=PORT):
    s = socket.socket()
    s.bind(('localhost', port))
    #LOG.info("Running on {0}".format(port))
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
        self.connections = {self.client_socket: self.client_address}
        self.thread_number = thread_number
        self.connections_lock = threading.Lock

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def append_connection(self, client_socket, client_address):
        with self.connections_lock:
            self.connections.update({client_socket: client_address})

    def parse_request(self, request):

        headers = {}

        request = request.replace('\r', '')
        newline = request.find('\n')
        header = request[:newline]
        request = request[newline + 1:]
        method, host, protocol = header.split(' ')
        request_lines = request.split('\n')
        for line in request_lines:
            semicolon = line.find(':')
            if semicolon != -1:
                key = line[:semicolon]
                value = line[semicolon + 2:]  # +1 for ':' and +1 for ' '
                headers.update({key: value})
        return method, host, protocol, headers

    def make_response_header(self, version, status, reason, headers):
        headers.pop('content-encoding', 0)
        return "{0} {1} {2}\r\n".format(version, status, reason) \
               + "".join(key + ': ' + value + '\r\n' for key, value in headers.iteritems()) \
               + '\r\n'

    def run(self):
        LOG.debug("Thread {0} started".format(self.thread_number))
        LOG.debug("{0}: Socket: {1}, address: {2}".format(self.thread_number, self.client_socket, self.client_address))
        received_data = ""

        ready_to_read, _, _ = select.select([self.client_socket], [], [], 10)
        if ready_to_read:
            received_data += self.client_socket.recv(4096)

        if received_data == "":
            self.finish_thread()
            return

        #LOG.debug(received_data)

        method, host, protocol, headers = self.parse_request(received_data)

        response = methods[method](host, headers=headers)
        response_header = self.make_response_header("HTTP/1.0", response.status_code, response.reason, response.headers)

        self.client_socket.send(response_header)
        self.client_socket.send(response.content)
        self.finish_thread()

    def finish_thread(self):
        LOG.debug("Thread {0} finished".format(self.thread_number))
        self.client_socket.close()

def main():
    def unhandled_exc_log(*exc_info):
        LOG.error("Unhandled exception: ", exc_info=exc_info)

    sys.excepthook = unhandled_exc_log
    logger = logging.getLogger()
    file_handler = logging.FileHandler(os.path.expanduser("~/translierator.log"), 'w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG if __debug__ else logging.WARNING)

    start_server()


if __name__ == '__main__':
    main()
