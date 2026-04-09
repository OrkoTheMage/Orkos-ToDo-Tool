# cli_args.py - functions for parsing command-line arguments

import argparse


def parse_args():
    p = argparse.ArgumentParser(prog='todo', usage='todo [arg] (i.e list | add | update | remove)', description='Simple todo CLI')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('list', aliases=['l', 'ls'], prog='todo list', help='List todos')
    sub.add_parser('id', prog='todo id', help='List todos with numeric ids')

    pa = sub.add_parser('add', aliases=['a'], prog='todo add', help='Add a todo')
    pa.add_argument('text', nargs='+', help='Todo text')
    pa.add_argument('-u', '--urgent', action='store_true', help='Flag as urgent')
    pa.add_argument('-d', '--days', help='Comma-separated days (Mon,Tue or monday)')

    pu = sub.add_parser('update', aliases=['u'], prog='todo update', help='Update a todo by id or text')
    pu.add_argument('id', help='Todo id (from list) or text fragment')
    pu.add_argument('text', nargs='*', help='New todo text')
    pu.add_argument('-check', action='store_true', dest='check', help='Mark as checked / toggle checked state')
    pu.add_argument('-uncheck', action='store_true', dest='uncheck', help='Mark as unchecked (explicit)')
    pu.add_argument('-d', '--days', help='Comma-separated days (Mon,Tue or monday)')

    pr = sub.add_parser('remove', aliases=['r'], prog='todo remove', help='Remove a todo by id or text')
    pr.add_argument('id', help='Todo id (from list) or text fragment')

    pur = sub.add_parser('urgent', prog='todo urgent', help='Toggle urgent flag on a todo')
    pur.add_argument('id', help='Todo id (from list) or text fragment')

    pc = sub.add_parser('clear', aliases=['c'], prog='todo clear', help='Clear todos')
    pc.add_argument('scope', nargs='?', choices=['unflagged', 'urgent', 'scheduled'],
                    help='Optional scope to clear: unflagged, urgent, or scheduled')

    ps = sub.add_parser('scheduled', aliases=['s'], prog='todo scheduled', help='Show scheduled todos')
    ps.add_argument('-d', '--day', help='Filter scheduled todos by day (Mon,Tue or monday)')

    pp = sub.add_parser('personalize', prog='todo personalize', help='Personalize colors')
    pp.add_argument('key', help='Which element to personalize (background,title1,title2,urgent,scheduled,text) or "default" to reset')
    pp.add_argument('color', nargs='?', help='Color value (name, #rrggbb, or SGR code)')

    args = p.parse_args()
    alias_map = {
        'l': 'list', 'ls': 'list',
        'a': 'add',
        'u': 'update',
        'r': 'remove',
        'c': 'clear',
        's': 'scheduled',
    }
    if getattr(args, 'cmd', None) in alias_map:
        args.cmd = alias_map[args.cmd]
    return args
