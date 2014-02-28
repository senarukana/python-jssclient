from jssclient import utils

def do_bucket_list(cs, args):
    objs = cs.bucket_list()
    objs = objs['Buckets']
    # print objs
    # print type(objs[0])
    utils.print_list(objs, ['Name',
                            'CreationDate',
                            'Location'])

@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the object')
def do_bucket_create(cs, args):
    cs.bucket_create(args.bucket_name)


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the object')
def do_bucket_delete(cs, args):
    cs.bucket_delete(args.bucket_name)


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the object')
@utils.arg('object_name',
    metavar='<object>',
    help='Name of object to delete')
@utils.arg('file_path',
    metavar='<file-path>',
    help='the path of file to upload to the bucket')
def do_object_put(cs, args):
    cs.object_put(args.bucket_name, args.object_name, args.file_path)


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the object')
@utils.arg('object_name',
    metavar='<object>',
    help='Name of object to delete')
@utils.arg('file_path',
    metavar='<file-path>',
    help='the path of file for the object to name')
def do_object_get(cs, args):
    cs.object_get(args.bucket_name, args.object_name, args.file_path)


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the object')
@utils.arg('object_name',
    metavar='<object>',
    help='Name of object to delete')
def do_object_delete(cs, args):
    cs.object_delete(args.bucket_name, args.object_name)


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Name of bucket for the objects')
def do_object_list(cs, args):
    bobj = cs.object_list(args.bucket_name)
    objs = bobj["Contents"]
    utils.print_list(objs, ["LastModified",
                            "ETag",
                            "Key",
                            "Size"])

@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Bucket name')
@utils.arg('object_name',
    metavar='<object>',
    help='Object name')
@utils.arg('file_path',
    metavar='<file-path>',
    help='the path of file where object write')
@utils.arg('thread_size',
    metavar='<thread-size>',
    help='the number of thread to download the object and merge them to a file')
@utils.arg('io_buffer_size',
    metavar='<io-buffer-size>',
    help='the size(bytes) of piece data for each thread')
def do_big_object_put(cs, args):
    cs.big_object_put(args.bucket_name,
                      args.object_name,
                      args.file_path,
                      int(args.thread_size),
                      int(args.io_buffer_size))


@utils.arg('bucket_name',
    metavar='<bucket>',
    help='Bucket name')
@utils.arg('object_name',
    metavar='<object>',
    help='Object name')
@utils.arg('file_path',
    metavar='<file-path>',
    help='the path of file where object write')
@utils.arg('thread_size',
    metavar='<thread-size>',
    help='the number of thread to download the object and merge them to a file')
@utils.arg('io_buffer_size',
    metavar='<io-buffer-size>',
    help='the size(bytes) of piece data for each thread')
def do_big_object_get(cs, args):
    cs.big_object_get(args.bucket_name,
                      args.object_name,
                      args.file_path,
                      int(args.thread_size),
                      int(args.io_buffer_size))
