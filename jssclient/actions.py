import json
from jssclient import utils


def do_bucket_list(cs, args):
    objs = cs.bucket_list()
    objs = objs['Buckets']
    utils.print_list(objs, ['Name', 'CreationDate'])

    

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
