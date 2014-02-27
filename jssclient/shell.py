import sys
import argparse
import jssclient
import traceback
from jssclient import utils
from jssclient import exceptions as exc
from jssclient import actions
from jssclient import client

"""
Command-line interface to the Jindong Storage Service (JSS) API.
"""

class JSSClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(JSSClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})


class JSSClientShell(object):

    def get_base_parser(self):
        parser = JSSClientArgumentParser(
            prog='jss',
            description="Command-line interface to the Jindong Storage Service (JSS) API.",
            epilog='See "jss help COMMAND" '\
                   'for help on a specific command.',
            add_help=False,
            formatter_class=JSSHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,
        )

        parser.add_argument('--version',
                            action='version',
                            version=jssclient.__version__)

        parser.add_argument('--jss-access-key',
            # metavar='<auth-access-key>',
            default=utils.env('JSS_ACCESS_KEY', default=False),
            action='store_true',
            help='Defaults to env[JSS_ACCESS_KEY].')
        parser.add_argument('--jss_access_key',
            help=argparse.SUPPRESS)

        parser.add_argument('--jss-secret-key',
            # metavar='<auth-secret-key>',
            default=utils.env('JSS_SECRET_KEY', default=False),
            action='store_true',
            help='Defaults to env[JSS_SECRET_KEY].')
        parser.add_argument('--jss_secret_key',
            help=argparse.SUPPRESS)

        parser.add_argument('--jss-url',
            # metavar='<jss-service-url>',
            default=utils.env('JSS_URL', 'JSS_URL'),
            help='Defaults to env[JSS_URL].')
        parser.add_argument('--jss_url',
            help=argparse.SUPPRESS)

        return parser

    def get_subcommand_parser(self):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        self._find_actions(subparsers, actions)
        self._find_actions(subparsers, self)

        return parser


    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                help=action_help,
                description=desc,
                add_help=False,
                formatter_class=JSSHelpFormatter
            )
            subparser.add_argument('-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)


    @utils.arg('command',
            metavar='<subcommand>', nargs='?',
            help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()



    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        # self.setup_debugging(options.debug)
        if not options.jss_url:
            raise exc.CommandError('JSS_URL can not be none.')
        if not options.jss_access_key:
            raise exc.CommandError('JSS_ACCESS_KEY can not be none.')
        if not options.jss_secret_key:
            raise exc.CommandError('JSS_SECRET_KEY can not be none.')

        subcommand_parser = self.get_subcommand_parser()
        self.parser = subcommand_parser

        if options.help and len(args) == 0:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        if args.func == self.do_help:
            self.do_help(args)
            return 0

        self.cs = client.Client(options.jss_url,
                                options.jss_access_key,
                                options.jss_secret_key)

        args.func(self.cs, args)


class JSSHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(JSSHelpFormatter, self).start_section(heading)

def main():
    try:
        JSSClientShell().main(sys.argv[1:])
    except Exception, e:
        traceback.print_exc()
        print >> sys.stderr, "ERROR: %s" % unicode(e)
        sys.exit(1)

if __name__ == '__main__':
    main()

