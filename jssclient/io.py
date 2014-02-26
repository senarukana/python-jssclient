class Stream(object):

    def read(self, buffer_size):
        raise NotImplementedError('Your should implemented this method.')

    def write(self, bytes_):
        raise NotImplementedError('Your should implemented this method.')

    def close(self):
        raise NotImplementedError('Your should implemented this method.')


class FileStream(Stream):

    def __init__(self, fd):
        self.fd = fd

    def read(self, buffer_size):
        return self.fd.read(buffer_size)

    def write(self, bytes_):
        return self.fd.write(bytes)

    def close(self, bytes_):
        return self.fd.close()

class HttpStream(Stream):

    def __init__(self, http_conn):
        self.http_conn = http_conn

    def read(self, buffer_size):
        return self.http_conn.read(buffer_size)

    def write(self, bytes_):
        return self.http_conn.write(bytes_)

    def close(self):
        return self.http_conn.close()

class MemStream(Stream):

    def __init__(self, buf, offset=0):
        self.buf = buf
        self.offset = offset
        self.size = len(self.buf)

    def read(self, buffer_size):
        if self.offset + self.buffer_size >= self.size:
            buffer_size = self.size - self.offset
        bytes_ = self.buf[self.offset:  self.offset + buffer_size]
        return bytes_

    def write(self, bytes_):
        byte_size = len(bytes)
        if self.offset + byte_size >= self.size :
            byte_size = self.size - self.offset
        bytes_ = self.buf[self.offset: self.offset + byte_size]
        return bytes_

    def close(self):
        pass
