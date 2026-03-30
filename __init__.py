import argparse
import difflib
import json
import os
import sys
import tempfile

# ── Display / Styling ────────────────────────────────────

def print_box(title, lines, date=None, show_header=True, urgent_set=None, day_labels=None):
    PAD = 4
    plain_title = title or ''
    plain_lines = list(lines)
    urgent_set = urgent_set or set()
    day_labels = day_labels or [None] * len(plain_lines)
    min_content = 32
    display_lines = [s + (f" [{day_labels[i]}]" if day_labels and day_labels[i] else '') for i, s in enumerate(plain_lines)]
    width = max(min_content, len(plain_title), (len(date) if date else 0), *(len(s) for s in display_lines))
    inner_w = width + PAD * 2

    style = load_style()
    if isinstance(style, dict) and style.get('styled'):
        BG = style.get('BG', '')
        BFG = style.get('BFG', '')
        MAG = style.get('MAG', '')
        ART = style.get('ART', '')
        RST = style.get('RST', '\033[0m')
        YEL = '\033[93m'
        CYN = style.get('CYN', '\033[1;36m')

        tw = inner_w
        hbar = '─' * tw
        sp = ' ' * PAD

        print(f"{BFG}{BG}┌{hbar}┐{RST}")

        if show_header:
            empty_row = f"{BFG}{BG}│{RST}{BG}{' ' * tw}{RST}{BFG}{BG}│{RST}"
            print(empty_row)
            title_center = plain_title.center(tw)
            print(f"{BFG}{BG}│{RST}{BG}{MAG}{title_center}{RST}{BFG}{BG}│{RST}")
            if date:
                date_center = date.center(tw)
                print(f"{BFG}{BG}│{RST}{BG}{CYN}{date_center}{RST}{BFG}{BG}│{RST}")
            print(empty_row)
            print(f"{BFG}{BG}├{hbar}┤{RST}")
        else:
            print(f"{BFG}{BG}├{hbar}┤{RST}")

        RESET_BG = RST + BG
        RED = '\033[91m'
        for li, ln in enumerate(display_lines):
            orig = plain_lines[li]
            day_label = day_labels[li] if li < len(day_labels) else None
            is_urgent = li in urgent_set
            ln_safe = ln.replace(RST, RESET_BG)
            if is_urgent:
                colored = f"{RED}{ln_safe}{RST}{BG}"
            else:
                if day_label:
                    base_safe = plain_lines[li].replace(RST, RESET_BG)
                    day_part = f"{YEL}[{day_label}]{RST}{BG}"
                    colored = base_safe + ' ' + day_part
                else:
                    colored = ln_safe
            padded = sp + colored + (' ' * (width - len(ln))) + sp
            print(f"{BFG}{BG}│{RST}{BG}{padded}{RST}{BFG}{BG}│{RST}")

        print(f"{BFG}{BG}└{hbar}┘{RST}")
        return

    horiz = '+' + ('-' * inner_w) + '+'
    nf_title_color, nf_index_color, nf_bold = style
    RESET = '\033[0m'

    def nf_color(code, bold=False):
        mapping = {
            0: 30, 1:31, 2:32, 3:33, 4:34, 5:35, 6:36, 7:37,
            8:90,9:91,10:92,11:93,12:94,13:95,14:96,15:97
        }
        base = mapping.get(code, 37)
        if bold:
            return f"\033[1;{base}m"
        return f"\033[{base}m"

    TITLE_COLOR = nf_color(nf_title_color or 13, nf_bold)
    INDEX_COLOR = nf_color(nf_index_color or 11, False)
    CYN_ASC = '\033[1;36m'

    print(horiz)
    if show_header:
        left = (inner_w - len(plain_title)) // 2
        right = inner_w - len(plain_title) - left
        title_colored = TITLE_COLOR + plain_title + RESET
        print('|' + (' ' * left) + title_colored + (' ' * right) + '|')
        if date:
            date_center = date.center(inner_w)
            date_colored = CYN_ASC + date_center + RESET
            print('|' + date_colored + '|')
        print(horiz)

    RED_ASC = '\033[91m'
    for li, ln in enumerate(display_lines):
        is_urgent = li in urgent_set
        day_label = day_labels[li] if li < len(day_labels) else None
        if ': ' in ln:
            idx, rest = ln.split(': ', 1)
            if idx.isdigit():
                if is_urgent:
                    colored = RED_ASC + idx + RESET + ': ' + RED_ASC + rest + RESET
                else:
                    if day_label:
                        colored = INDEX_COLOR + idx + RESET + ': ' + rest
                        colored = colored + ' ' + '\033[93m' + f"[{day_label}]" + RESET
                    else:
                        colored = INDEX_COLOR + idx + RESET + ': ' + rest
            else:
                if is_urgent:
                    colored = RED_ASC + ln + RESET
                else:
                    if day_label:
                        colored = ln.replace(f" [{day_label}]", '') + ' ' + '\033[93m' + f"[{day_label}]" + RESET
                    else:
                        colored = ln
        else:
            if is_urgent:
                colored = RED_ASC + ln + RESET
            else:
                if day_label:
                    colored = '\033[93m' + ln + RESET
                else:
                    colored = ln
        visible_len = len(ln)
        padded = (' ' * PAD) + colored + (' ' * PAD)
        print('|' + padded.ljust(inner_w + (len(padded) - (visible_len + PAD*2))) + '|')
    print(horiz)


# ── Style / Defaults ─────────────────────────────────────────


def load_style():
    # Default style values
    defaults = {
        'BG': '\033[48;2;70;60;70m',
        'BFG': '\033[38;2;125;125;125m',
        'ART': '\033[1;37m',
        'MAG': '\033[1;35m',  # title1
        'RST': '\033[0m',
        'CYN': '\033[1;36m',  # title2 / date
        'YEL': '\033[93m',
        'RED': '\033[91m',
        'styled': True,
    }
    # Load any personalized overrides from config
    try:
        cfg = load_personalization()
        if cfg:
            defaults.update(cfg)
    except Exception:
        pass
    return defaults


# ── Personalization / Config ─────────────────────────────────

def config_path():
    return os.path.expanduser('~/.todos_config.json')


def load_personalization():
    path = config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def save_personalization(d):
    path = config_path()
    dname = os.path.dirname(path) or os.path.expanduser('~')
    try:
        os.makedirs(dname, exist_ok=True)
    except Exception:
        pass
    fd, tmp = tempfile.mkstemp(prefix='.todos_config.', dir=dname)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


# ── Color Parsing ─────────────────────────────────────────────
def _parse_color_value(val, is_bg=False):
    """Parse a color specification into an ANSI escape sequence.

    Supports:
    - named colors: red, green, yellow, blue, magenta, cyan, white, black
    - hex: #rrggbb
    - raw SGR numeric (e.g. 91)
    """
    if not val:
        return ''
    v = val.strip().lower()
    # named colors mapping (foreground)
    names = {
        'black':'30','red':'31','green':'32','yellow':'33','blue':'34','magenta':'35','cyan':'36','white':'37',
        'bright_black':'90','bright_red':'91','bright_green':'92','bright_yellow':'93','bright_blue':'94','bright_magenta':'95','bright_cyan':'96','bright_white':'97'
    }
    if v in ('reset','rst','0'):
        return '\033[0m'
    # helper: blend user rgb toward base background for low opacity
    def _blend_to_base(user_rgb, alpha=0.35, base_rgb=(70, 60, 70)):
        r = int(user_rgb[0] * alpha + base_rgb[0] * (1 - alpha))
        g = int(user_rgb[1] * alpha + base_rgb[1] * (1 - alpha))
        b = int(user_rgb[2] * alpha + base_rgb[2] * (1 - alpha))
        return (r, g, b)

    # map named SGR codes to approximate RGBs for blending
    name_to_rgb = {
        'black': (0,0,0),'red': (205,49,49),'green': (13,188,121),'yellow': (229,229,16),
        'blue': (36,114,200),'magenta': (188,63,188),'cyan': (17,168,205),'white': (229,229,229),
        'bright_black': (102,102,102),'bright_red': (255,85,85),'bright_green': (75,255,150),'bright_yellow': (255,255,85),
        'bright_blue': (85,153,255),'bright_magenta': (255,125,255),'bright_cyan': (85,255,255),'bright_white': (255,255,255)
    }

    if v in names:
        code = names[v]
        # for background, produce a blended truecolor escape
        if is_bg:
            rgb = name_to_rgb.get(v)
            if rgb:
                br, bgc, bb = _blend_to_base(rgb)
                return f"\033[48;2;{br};{bgc};{bb}m"
            try:
                base = int(code)
            except Exception:
                base = None
            if base is not None:
                bg_code = base + 10
                return f"\033[{bg_code}m"
        return f"\033[{code}m"
    # hex color
    # accept either '#rrggbb' or 'rrggbb'
    if (v.startswith('#') and len(v) == 7) or (len(v) == 6 and all(c in '0123456789abcdef' for c in v)):
        try:
            if v.startswith('#'):
                r = int(v[1:3], 16)
                g = int(v[3:5], 16)
                b = int(v[5:7], 16)
            else:
                r = int(v[0:2], 16)
                g = int(v[2:4], 16)
                b = int(v[4:6], 16)
            if is_bg:
                br, bgc, bb = _blend_to_base((r,g,b))
                return f"\033[48;2;{br};{bgc};{bb}m"
            return f"\033[38;2;{r};{g};{b}m"
        except Exception:
            pass
    # raw sgr numeric or 38;2/48;2 form
    if ';' in v:
        # handle truecolor specs like 38;2;r;g;b or 48;2;r;g;b
        parts = v.split(';')
        try:
            if len(parts) >= 5 and parts[0] in ('38', '48') and parts[1] == '2':
                r = int(parts[2]); g = int(parts[3]); b = int(parts[4])
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    return ''
                if is_bg:
                    br, bgc, bb = _blend_to_base((r, g, b))
                    return f"\033[48;2;{br};{bgc};{bb}m"
                return f"\033[38;2;{r};{g};{b}m"
            # handle 256-color form: 38;5;N or 48;5;N
            if len(parts) >= 3 and parts[0] in ('38', '48') and parts[1] == '5':
                n = int(parts[2])
                if 0 <= n <= 255:
                    # convert foreground->background when requested
                    if is_bg and parts[0] == '38':
                        return f"\033[48;5;{n}m"
                    return f"\033[{v}m"
        except Exception:
            return ''
        return ''
    if v.isdigit():
        try:
            num = int(v)
            # map numeric SGR to RGB when making background
            sgr_to_rgb = {
                30: (0,0,0),31:(205,49,49),32:(13,188,121),33:(229,229,16),34:(36,114,200),35:(188,63,188),36:(17,168,205),37:(229,229,229),
                90:(102,102,102),91:(255,85,85),92:(75,255,150),93:(255,255,85),94:(85,153,255),95:(255,125,255),96:(85,255,255),97:(255,255,255)
            }
            if is_bg and num in sgr_to_rgb:
                br, bgc, bb = _blend_to_base(sgr_to_rgb[num])
                return f"\033[48;2;{br};{bgc};{bb}m"
            if is_bg and (30 <= num <= 37 or 90 <= num <= 97):
                num = num + 10
            return f"\033[{num}m"
        except Exception:
            return f"\033[{v}m"
    # fallback: invalid color specification
    return ''


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
        print('Color missing. If using a hex value start with # and quote or escape it, e.g. "#1e90ff" or \'1e90ff\'.')
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


# ── Persistence ─────────────────────────────────────────────

def todos_path():
    return os.path.expanduser('~/.todos.json')


# ── Utilities ───────────────────────────────────────────────

def resolve_todo_identifier(identifier, todos, cutoff=0.6):
    if identifier is None:
        return None
    try:
        i = int(identifier)
        return i - 1
    except Exception:
        pass

    texts = [t.get('text', '') if isinstance(t, dict) else str(t) for t in todos]
    if not texts:
        return None

    subs = [i for i, txt in enumerate(texts) if identifier.lower() in txt.lower()]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        return subs[0]

    best_idx = None
    best_score = 0.0
    for i, txt in enumerate(texts):
        score = difflib.SequenceMatcher(None, identifier.lower(), txt.lower()).ratio()
        if score > best_score:
            best_score = score
            best_idx = i

    if best_score >= cutoff:
        return best_idx
    return None


def find_matching_indices(identifier, todos):
    if identifier is None:
        return []
    ident = identifier.strip().lower()
    res = [i for i, t in enumerate(todos) if ident in (t.get('text','').lower() if isinstance(t, dict) else str(t).lower())]
    return res


def _prefix_and_space(lines, day_labels, urgent_set):
    """Prefix each line with '- ' and insert an empty spacer line after each item.

    Returns (spaced_lines, spaced_day_labels, spaced_urgent_set)
    """
    spaced_lines = []
    spaced_day_labels = []
    spaced_urgent_set = set()
    for i, ln in enumerate(lines):
        # prefix
        pref = f"- {ln}"
        spaced_lines.append(pref)
        spaced_day_labels.append(day_labels[i] if day_labels and i < len(day_labels) else None)
        if urgent_set and i in urgent_set:
            spaced_urgent_set.add(len(spaced_lines) - 1)
        # spacer
        spaced_lines.append("")
        spaced_day_labels.append(None)
    return spaced_lines, spaced_day_labels, spaced_urgent_set


def parse_days_arg(s):
    if not s:
        return []
    mapping = {
        'mon': 'monday', 'monday': 'monday', 'tue': 'tuesday', 'tues': 'tuesday', 'tuesday': 'tuesday',
        'wed': 'wednesday', 'wednesday': 'wednesday', 'thu': 'thursday', 'thurs': 'thursday', 'thursday': 'thursday',
        'fri': 'friday', 'friday': 'friday', 'sat': 'saturday', 'saturday': 'saturday',
        'sun': 'sunday', 'sunday': 'sunday'
    }
    parts = [p.strip().lower() for p in s.split(',') if p.strip()]
    out = []
    for p in parts:
        if p in mapping:
            out.append(mapping[p])
    res = []
    for d in out:
        if d not in res:
            res.append(d)
    return res


def load_todos():
    path = todos_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                out = []
                for t in data:
                    if isinstance(t, dict):
                        txt = t.get('text', '')
                        urgent = bool(t.get('urgent', False))
                        days = t.get('days') or []
                        out.append({'text': txt, 'urgent': urgent, 'days': days})
                    else:
                        out.append({'text': t, 'urgent': False, 'days': []})
                return out
    except Exception:
        return []
    return []


def save_todos(todos):
    path = todos_path()
    dname = os.path.dirname(path) or os.path.expanduser('~')
    try:
        os.makedirs(dname, exist_ok=True)
    except Exception:
        pass
    fd, tmp = tempfile.mkstemp(prefix='.todos.', dir=dname)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


# ── Commands ───────────────────────────────────────────────

def list_cmd(args):
    todos = load_todos()
    date_str = __import__('datetime').datetime.now().strftime('%A, %B %d, %Y')
    title = 'To-Do List'
    import datetime as _dt
    today = _dt.datetime.now().strftime('%A').lower()

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


# ── CLI / Argument Parsing ──────────────────────────────────

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
