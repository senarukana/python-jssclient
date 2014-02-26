import lz4
import struct
import binascii

int_struct = struct.Struct('!i')

class BytesError(Exception):
    pass

class CompressAlgorithm(object):

    def compress(self, buf):
        raise NotImplemented('You should implemented this method.')

    def decompress(self, buf):
        raise NotImplemented('You should implemented this method.')

    def encode_head(self):
        x = (self.version & 0xf) << 4
        y = self.value & 0xf
        return int_struct.pack((x | y) & 0xff)

    @staticmethod
    def decode_head(buf, offset=0):
        int_v = int_struct.unpack(buf, offset)[0]
        version, value = (int_v >> 4) & 0xf, int_v & 0xf
        return version, value

    @staticmethod
    def load_cls(buf, offset=0):
        version, value = CompressAlgorithm.decode_head(buf, offset)
        if (version, value) == (1, 1):
            return Lz4
        if (version, value) == (1, 2):
            return Gzip
        if (version, value) == (1, 3):
            return Quicklz
        raise Exception('No such compress algorithm.')


def encode(compress_func, buf):
    result = bytearray()
    cbuf = compress_func(buf)

    crc32 = binascii.crc32(cbuf) & 0xffffffff
    result.extend(int_struct.pack(crc32))

    len32 = len(cbuf)
    result.extend(int_struct.pack(len32))

    result.extend(cbuf)
    return result


class Lz4(CompressAlgorithm):
    version = 1
    value = 1

    def compress(self, buf):
        return encode(lz4.compress, buf)

    def decompress(self, buf):
        return lz4.decompress(buf)


class Gzip(CompressAlgorithm):
    version = 1
    value = 2

    def compress(self, buf):
        pass

    def decompress(self, buf):
        pass


class Quicklz(CompressAlgorithm):
    version = 1
    value = 3

    def compress(self, buf):
        pass

    def decompress(self, buf):
        pass


class CompressObjectPut(object):

    def __init__(self, jsscli, bucket_name, object_name, compress_cls=Lz4):
        self.jsscli = jsscli
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.compress_obj = compress_cls()

    def start(self):
        self.conn = self.jsscli.object_put_conn(self.bucket_name, self.object_name)
        self.conn.write(self.compress_obj.encode_head())

    def put(self, buf):
        cbuf = self.compress_obj.compress(buf)
        self.conn.write(cbuf)

    def end(self):
        self.conn.close()


class CompressObjectGet(object):

    def __init__(self, jsscli, bucket_name, object_name):
        self.jsscli = jsscli
        self.bucket_name = bucket_name
        self.object_name = object_name

    def start(self):
        self.conn = self.jsscli.object_get_conn(self.bucket_name, self.object_name)
        buf = self.conn.read(1)
        self.compress_obj = CompressAlgorithm.load_cls(buf)

    def get(self):
        buf = self.conn.read(1)
        crc32 = int_struct.unpack(buf, 0)[0]

        buf = self.conn.read(1)
        len32 = int_struct.unpack(buf, 0)[0]

        buf = self.conn.read(len32)
        if crc32 != binascii.crc32(buf) & 0xffffffff:
            raise BytesError('CRC32 not matched.')
        return self.compress_obj.decompress(buf)

    def close(self):
        self.conn.close()

