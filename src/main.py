#!/usr/bin/env python3
import argparse
import os
import sys

from display import print_box, _prefix_and_space
from config import config_path, load_personalization, save_personalization
from colors import _parse_color_value
from storage import (
    todos_path, load_todos, save_todos, resolve_todo_identifier, find_matching_indices, parse_days_arg,
)


# ── Commands ───────────────────────────────────────────────

def list_cmd(args):
    from datetime import datetime as _dt
    date_str = _dt.now().strftime('%A, %B %d, %Y')
    title = 'To-Do List'
    todos = load_todos()
    today = _dt.now().strftime('%A').lower()

    # Visible todos are those with no schedule or scheduled for today.
    visible = []
    for t in todos:
        days = t.get('days') or []
        if days and today not in [d.lower() for d in days]:
            continue
        visible.append(t)

    if not visible:
        lines = ['Jobs done, nothing to-do right now!']
        urgent_set = set()
        day_labels = []
        print_box(title, lines, date=date_str, show_header=True, urgent_set=urgent_set, day_labels=day_labels)
        return

    abbrev = {'monday':'Mon','tuesday':'Tue','wednesday':'Wed','thursday':'Thu','friday':'Fri','saturday':'Sat','sunday':'Sun'}
    urgent_daily = []
    urgent_daily_labels = []
    urgent_regular = []
    urgent_regular_labels = []
    daily = []
    daily_labels = []
    regular = []
    regular_labels = []

    for t in visible:
        days = t.get('days') or []
        marker = ' [!]' if t.get('urgent') else ''
        if days:
            labels = [abbrev.get(d.lower(), d[:3].title()) for d in days]
            label = '/'.join(labels)
        else:
            label = None
        if t.get('urgent') and days:
            urgent_daily.append(f"{t['text']}{marker}")
            urgent_daily_labels.append(label)
        elif t.get('urgent'):
            urgent_regular.append(f"{t['text']}{marker}")
            urgent_regular_labels.append(label)
        elif days:
            daily.append(f"{t['text']}{marker}")
            daily_labels.append(label)
        else:
            regular.append(f"{t['text']}{marker}")
            regular_labels.append(label)

    lines = urgent_daily + urgent_regular + daily + regular
    day_labels = urgent_daily_labels + urgent_regular_labels + daily_labels + regular_labels
    urgent_set = set(range(len(urgent_daily) + len(urgent_regular)))
    spaced_lines, spaced_day_labels, spaced_urgent_set = _prefix_and_space(lines, day_labels, urgent_set)
    print_box(title, spaced_lines, date=date_str, show_header=True, urgent_set=spaced_urgent_set, day_labels=spaced_day_labels)


def add_cmd(args):
    todos = load_todos()
    text = args.text
    urgent = getattr(args, 'urgent', False)
    days = parse_days_arg(getattr(args, 'days', None))
    todos.append({'text': text, 'urgent': urgent, 'days': days})
    save_todos(todos)
    label = ' [urgent]' if urgent else ''
    if days:
        print(f"Added{label} ({', '.join(days)}): {text}")
    else:
        print(f'Added{label}: {text}')


def update_cmd(args):
    todos = load_todos()
    ident = args.id
    try:
        test_i = int(ident)
        idx = resolve_todo_identifier(ident, todos)
    except Exception:
        matches = find_matching_indices(ident, todos)
        if len(matches) > 1:
            print('Multiple matches found:')
            for n, mi in enumerate(matches, start=1):
                t = todos[mi]
                flags = []
                if t.get('urgent'):
                    flags.append('urgent')
                if t.get('days'):
                    flags.append('days=' + ','.join(t.get('days', [])))
                flag_str = (f" [{', '.join(flags)}]" if flags else '')
                print(f"  {n}) {t.get('text','')}{flag_str}")
            try:
                choice = input('Choose number to update (or C to cancel): ').strip()
            except Exception:
                print('Aborted.')
                return
            if not choice or choice.lower().startswith('c'):
                print('Aborted.')
                return
            try:
                sel = int(choice)
                if sel < 1 or sel > len(matches):
                    print('Invalid selection. Aborted.')
                    return
            except Exception:
                print('Invalid selection. Aborted.')
                return
            idx = matches[sel-1]
        elif len(matches) == 1:
            idx = matches[0]
        else:
            idx = resolve_todo_identifier(ident, todos)

    if idx is None or idx < 0 or idx >= len(todos):
        print(f"No matching todo for: {args.id}")
        return
    todos[idx]['text'] = args.text
    if getattr(args, 'days', None) is not None:
        todos[idx]['days'] = parse_days_arg(args.days)
    save_todos(todos)
    print(f'Updated {args.id}: {args.text}!')


def remove_cmd(args):
    todos = load_todos()
    ident = args.id
    try:
        test_i = int(ident)
        idx = resolve_todo_identifier(ident, todos)
    except Exception:
        matches = find_matching_indices(ident, todos)
        if len(matches) > 1:
            print('Multiple matches found:')
            for n, mi in enumerate(matches, start=1):
                t = todos[mi]
                flags = []
                if t.get('urgent'):
                    flags.append('urgent')
                if t.get('days'):
                    flags.append('days=' + ','.join(t.get('days',[])))
                flag_str = (f" [{', '.join(flags)}]" if flags else '')
                print(f"  {n}) {t.get('text','')}{flag_str}")
            try:
                choice = input('Choose number to remove (or C to cancel): ').strip()
            except Exception:
                print('Aborted.')
                return
            if not choice or choice.lower().startswith('c'):
                print('Aborted.')
                return
            try:
                sel = int(choice)
                if sel < 1 or sel > len(matches):
                    print('Invalid selection. Aborted.')
                    return
            except Exception:
                print('Invalid selection. Aborted.')
                return
            idx = matches[sel-1]
        elif len(matches) == 1:
            idx = matches[0]
        else:
            idx = resolve_todo_identifier(ident, todos)

    if idx is None or idx < 0 or idx >= len(todos):
        print(f"No matching todo for: {args.id}")
        return
    removed = todos.pop(idx)
    save_todos(todos)
    print(f"Removed: {removed.get('text','')}")


def urgent_cmd(args):
    todos = load_todos()
    idx = resolve_todo_identifier(args.id, todos)
    if idx is None or idx < 0 or idx >= len(todos):
        print(f"No matching todo for: {args.id}")
        return
    todos[idx]['urgent'] = not todos[idx].get('urgent', False)
    save_todos(todos)
    state = 'urgent' if todos[idx]['urgent'] else 'normal'
    print(f"Todo {args.id} marked as {state}")


def clear_cmd(args):
    path = todos_path()
    if not os.path.exists(path):
        print('No todos to clear.')
        return
    todos = load_todos()

    def ask(prompt):
        try:
            return input(prompt).strip().lower() in ('y', 'yes')
        except Exception:
            return False

    def clear_unflagged():
        cur = load_todos()
        unflagged = [t for t in cur if not t.get('urgent') and not (t.get('days'))]
        if not unflagged:
            print('No unflagged todos to clear.')
            return
        if ask(f"Clear {len(unflagged)} unflagged todos? (y/N): "):
            cur = [t for t in cur if t not in unflagged]
            save_todos(cur)
            print(f"Removed {len(unflagged)} unflagged todos.")
        else:
            print('Skipped unflagged todos.')

    def clear_urgent():
        cur = load_todos()
        urgent_list = [t for t in cur if t.get('urgent')]
        if not urgent_list:
            print('No urgent todos to clear.')
            return
        if ask(f"Clear {len(urgent_list)} urgent todos? (y/N): "):
            cur = [t for t in cur if not t.get('urgent')]
            save_todos(cur)
            print(f"Removed {len(urgent_list)} urgent todos.")
        else:
            print('Skipped urgent todos.')

    def clear_scheduled():
        cur = load_todos()
        scheduled = [t for t in cur if t.get('days')]
        if not scheduled:
            print('No scheduled todos to clear.')
            return
        if ask(f"Clear {len(scheduled)} scheduled todos? (y/N): "):
            cur = [t for t in cur if not t.get('days')]
            save_todos(cur)
            print(f"Removed {len(scheduled)} scheduled todos.")
        else:
            print('Skipped scheduled todos.')

    scope = getattr(args, 'scope', None)
    if scope == 'unflagged':
        clear_unflagged()
        return
    if scope == 'urgent':
        clear_urgent()
        return
    if scope == 'scheduled':
        clear_scheduled()
        return

    clear_unflagged()
    clear_urgent()
    clear_scheduled()


def scheduled_cmd(args):
    todos = load_todos()
    day_filter = None
    if getattr(args, 'day', None):
        days = parse_days_arg(args.day)
        if days:
            day_filter = days[0]
    scheduled = [t for t in todos if t.get('days')]
    if day_filter:
        scheduled = [t for t in scheduled if day_filter in [d.lower() for d in t.get('days', [])]]

    # Secondary title for scheduled view (Monday - Sunday) shown in cyan
    date_str = 'Monday - Sunday'

    if not scheduled:
        # Show styled UI even when there are no scheduled todos
        lines = ['Jobs done, nothing scheduled right now!']
        print_box('Scheduled To-Do List', lines, date=date_str, show_header=True, urgent_set=set(), day_labels=[])
        return

    lines = []
    day_labels = []
    for t in scheduled:
        marker = ' [!]' if t.get('urgent') else ''
        labels = [d[:3].title() for d in t.get('days', [])]
        label = '/'.join(labels) if labels else None
        lines.append(f"{t.get('text','')}{marker}")
        day_labels.append(label)

    urgent_set = set(i for i, t in enumerate(scheduled) if t.get('urgent'))
    spaced_lines, spaced_day_labels, spaced_urgent_set = _prefix_and_space(lines, day_labels, urgent_set)
    print_box('Scheduled Todos', spaced_lines, date=date_str, show_header=True, urgent_set=spaced_urgent_set, day_labels=spaced_day_labels)


def personalize_cmd(args):
    key = (args.key or '').strip().lower()
    color = args.color
    # Support resetting to defaults
    if key == 'default':
        pth = config_path()
        try:
            if os.path.exists(pth):
                os.remove(pth)
        except Exception:
            pass
        print('Personalization reset to defaults.')
        return
    # If the user typed an unquoted hex like #1e90ff the shell may drop it as a comment
    if color is None:
        print("Color missing. If using a hex value start with # and quote or escape it, e.g. \"#1e90ff\" or '1e90ff'.")
        return
    allowed = {
        'background': ('BG', True),
        'title1': ('MAG', False),
        'title2': ('CYN', False),
        'urgent': ('RED', False),
        'scheduled': ('YEL', False),
        'text': ('BFG', False),
    }
    if key not in allowed:
        print('Unknown key. Allowed:', ', '.join(allowed.keys()))
        return
    tgt, is_bg = allowed[key]
    seq = _parse_color_value(color, is_bg=is_bg)
    if not seq:
        print('Failed to parse color:', color, 'try named colors (red, bright_blue), hex (#1e90ff), or raw SGR (e.g. 91 or 38;2;R;G;B).')
        return
    cfg = load_personalization()
    cfg[tgt] = seq
    save_personalization(cfg)
    print(f"Saved {key} -> {color}")


def parse_args():
    p = argparse.ArgumentParser(prog='todo', usage='todo [arg] (i.e list | add | update | remove)', description='Simple todo CLI')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('list', aliases=['l', 'ls'], prog='todo list', help='List todos')

    pa = sub.add_parser('add', aliases=['a'], prog='todo add', help='Add a todo')
    pa.add_argument('text', nargs='+', help='Todo text')
    pa.add_argument('-u', '--urgent', action='store_true', help='Flag as urgent')
    pa.add_argument('-d', '--days', help='Comma-separated days (Mon,Tue or monday)')

    pu = sub.add_parser('update', aliases=['u'], prog='todo update', help='Update a todo by id or text')
    pu.add_argument('id', help='Todo id (from list) or text fragment')
    pu.add_argument('text', nargs='+', help='New todo text')
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
    # Normalize shorthand aliases to canonical command names so callers
    # can compare against the canonical names (e.g. 'list', 'add').
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


def main():
    args = parse_args()
    if args.cmd == 'list':
        list_cmd(args)
    elif args.cmd == 'add':
        args.text = ' '.join(args.text)
        add_cmd(args)
    elif args.cmd == 'update':
        args.text = ' '.join(args.text)
        update_cmd(args)
    elif args.cmd == 'remove':
        remove_cmd(args)
    elif args.cmd == 'urgent':
        urgent_cmd(args)
    elif args.cmd == 'clear':
        clear_cmd(args)
    elif args.cmd == 'scheduled':
        scheduled_cmd(args)
    elif args.cmd == 'personalize':
        personalize_cmd(args)
    else:
        print('Use: todo (list|scheduled|add|update|remove)')


__all__ = ['main']

# Package version
__version__ = '0.1.0'
