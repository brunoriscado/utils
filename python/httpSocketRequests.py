#!/usr/bin/python
import socket
import urlparse
import re
import os
import json

"""HTTP requests with no external lib dependencies"""

class MessageError(Exception): pass

class MessageReader(object):
    def __init__(self,sock):
        self.sock = sock
        self.buffer = b''

    def get_until(self,what):
        while what not in self.buffer:
            if not self._fill():
                return b''
        offset = self.buffer.find(what) + len(what)
        data,self.buffer = self.buffer[:offset],self.buffer[offset:]
        return data

    def get_bytes(self,size):
        while len(self.buffer) < size:
            if not self._fill():
                return b''
        data,self.buffer = self.buffer[:size],self.buffer[size:]
        return data

    def _fill(self):
        data = self.sock.recv(1024)
        if not data:
            if self.buffer:
                raise MessageError('socket closed with incomplete message')
            return False
        self.buffer += data
        return True

def GET(url, headers, httpVersion="1.0", socketTimeout=0.50, verbose=False):
    socket.setdefaulttimeout = socketTimeout
    urlParsed = urlparse.urlparse(url)
    path = urlParsed.path
    host = urlParsed.hostname
    port = 80 if urlParsed.port is None else urlParsed.port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    request = "GET %s HTTP/%s%s" % (path, httpVersion, "\r\n")
    for key, value in headers.items():
        request += "%s: %s\r\n" % (key, value)
    request += "\r\n"
    s.sendall(request)
    mr = MessageReader(s)
    header = mr.get_until(b'\r\n\r\n')
    m = re.search(b'Content-Length: (\d+)',header)
    response = ""
    if m:
        length = int(m.group(1))
        if length is None:
            s.shutdown(1)
            s.close()
            response = aux(s, host, port, request)
        else:
            response += mr.get_bytes(length)
            s.shutdown(1)
            s.close()
    else:
        s.shutdown(1)
        s.close()
        response = aux(s, host, port, request)
    if (verbose):
        print 'Request: ', repr(request)
        print '\n'
        print 'Response: ', repr(response)
    return response.split("\r\n\r\n")[1] if len(response.split("\r\n\r\n")) == 2 else None

def aux(s, host, port, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(request)
    response = s.recv(1000000000)
    s.shutdown(1)
    s.close()
    return response

def POST(url, bodyData, headers, httpVersion="1.0", socketTimeout=0.50, verbose=False):
    socket.setdefaulttimeout = socketTimeout
    urlParsed = urlparse.urlparse(url)
    path = urlParsed.path
    host = urlParsed.hostname
    port = 80 if urlParsed.port is None else urlParsed.port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    request = "POST %s HTTP/%s%s" % (path, httpVersion, "\r\n")
    for key, value in headers.items():
        request += "%s: %s\r\n" % (key, value)
    request += "\r\n%s" % bodyData
    s.sendall(request)
    mr = MessageReader(s)
    header = mr.get_until(b'\r\n\r\n')
    m = re.search(b'Content-Length: (\d+)',header)
    response = ""
    if m:
        length = int(m.group(1))
        if length is None:
            s.shutdown(1)
            s.close()
            response = aux(s, host, port, request)
        else:
            response += mr.get_bytes(length)
            s.shutdown(1)
            s.close()
    else:
        s.shutdown(1)
        s.close()
        response = aux(s, host, port, request)
    if (verbose):
        print 'Request: ', repr(request)
        print '\n'
        print 'Response: ', repr(response)
    return response.split("\r\n\r\n")[1] if len(response.split("\r\n\r\n")) == 2 else None