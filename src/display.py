# display.py - functions for displaying todo lists in the terminal

from colors import load_style


def print_box(title, lines, date=None, show_header=True, urgent_set=None, day_labels=None):
    PAD = 4
    plain_title = title or ''
    plain_lines = list(lines)
    urgent_set = urgent_set or set()
    day_labels = day_labels or [None] * len(plain_lines)
    min_content = 32
    display_lines = []
    check_sub = ' [✔]'
    for i, s in enumerate(plain_lines):
        day = day_labels[i] if day_labels and i < len(day_labels) else None
        has_check = check_sub in s
        base = s.replace(check_sub, '')
        base_with_day = base + (f" [{day}]" if day else '')
        final = base_with_day + (check_sub if has_check else '')
        display_lines.append(final)
    width = max(min_content, len(plain_title), (len(date) if date else 0), *(len(s) for s in display_lines))
    inner_w = width + PAD * 2

    # Two display modes:
    # - Modern: `style` is a dict with pre-built ANSI sequences (preferred).
    # - Legacy: `style` is a tuple with numeric codes (kept for backward compatibility).
    # Prefer the dict-based rendering when available for richer visuals.
    style = load_style()
    if isinstance(style, dict) and style.get('styled'):
        BG = style.get('BG', '')
        BFG = style.get('BFG', '')
        MAG = style.get('MAG', '')
        ART = style.get('ART', '')
        RST = style.get('RST', '\033[0m')
        YEL = style.get('YEL', '\033[93m')
        CYN = style.get('CYN', '\033[1;36m')
        GRN = style.get('GRN', '\033[92m')

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

        # `RESET_BG` is used to replace any embedded reset sequences in
        # item text so the background remains consistent for the full line.
        RESET_BG = RST + BG
        RED = '\033[91m'
        for li, ln in enumerate(display_lines):
            orig = plain_lines[li]
            day_label = day_labels[li] if li < len(day_labels) else None
            is_urgent = li in urgent_set
            is_checked = '✔' in (orig or '')
            ln_safe = ln.replace(RST, RESET_BG)
            check_sub = ' [✔]'
            base_safe = plain_lines[li].replace(check_sub, '').replace(RST, RESET_BG)
            day_part = (f" {YEL}[{day_label}]{RST}{BG}") if day_label else ''
            check_part = f" {GRN}[✔]{RST}{BG}" if is_checked else ''
            if is_urgent:
                colored = f"{RED}{base_safe}{RST}{BG}{day_part}{check_part}"
            else:
                colored = f"{base_safe}{day_part}{check_part}"
            padded = sp + colored + (' ' * (width - len(ln))) + sp
            print(f"{BFG}{BG}│{RST}{BG}{padded}{RST}{BFG}{BG}│{RST}")

        print(f"{BFG}{BG}└{hbar}┘{RST}")
        return

    horiz = '+' + ('-' * inner_w) + '+'
    nf_title_color, nf_index_color, nf_bold = style
    RESET = '\033[0m'

    # Legacy helper: map numeric indices to simple SGR color codes.
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
    GREEN_ASC = '\033[92m'
    for li, ln in enumerate(display_lines):
        is_urgent = li in urgent_set
        day_label = day_labels[li] if li < len(day_labels) else None
        if ': ' in ln:
            idx, rest = ln.split(': ', 1)
            if idx.isdigit():
                check_sub = ' [✔]'
                is_checked = check_sub in rest
                rest_base = rest.replace(check_sub, '')
                if is_urgent:
                    colored = RED_ASC + idx + RESET + ': ' + RED_ASC + rest_base + RESET
                    if day_label:
                        colored += ' ' + '\033[93m' + f"[{day_label}]" + RESET
                    if is_checked:
                        colored += ' ' + GREEN_ASC + '[✔]' + RESET
                else:
                    colored = INDEX_COLOR + idx + RESET + ': ' + rest_base
                    if day_label:
                        colored += ' ' + '\033[93m' + f"[{day_label}]" + RESET
                    if is_checked:
                        colored += ' ' + GREEN_ASC + '[✔]' + RESET
            else:
                is_checked = '✔' in ln
                check_sub = ' [✔]'
                base = ln.replace(check_sub, '')
                if day_label:
                    base = base.replace(f" [{day_label}]", '')
                if is_checked:
                    if is_urgent:
                        colored = RED_ASC + base + RESET
                        colored += ' ' + GREEN_ASC + '[✔]' + RESET
                        if day_label:
                            colored += ' ' + '\033[93m' + f"[{day_label}]" + RESET
                    else:
                        colored = base + ' ' + GREEN_ASC + '[✔]' + RESET
                        if day_label:
                            colored += ' ' + '\033[93m' + f"[{day_label}]" + RESET
                elif is_urgent:
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
        # `visible_len` reflects the printed text length (without ANSI codes)
        # and is used to compute padding so the surrounding box stays aligned.
        visible_len = len(ln)
        padded = (' ' * PAD) + colored + (' ' * PAD)
        print('|' + padded.ljust(inner_w + (len(padded) - (visible_len + PAD*2))) + '|')
    print(horiz)


def _prefix_and_space(lines, day_labels, urgent_set):
    """Prefix each line with '- ' and insert an empty spacer line after each item.

    Returns (spaced_lines, spaced_day_labels, spaced_urgent_set)
    """
    spaced_lines = []
    spaced_day_labels = []
    spaced_urgent_set = set()
    for i, ln in enumerate(lines):
        pref = f"- {ln}"
        spaced_lines.append(pref)
        spaced_day_labels.append(day_labels[i] if day_labels and i < len(day_labels) else None)
        if urgent_set and i in urgent_set:
            spaced_urgent_set.add(len(spaced_lines) - 1)
        spaced_lines.append("")
        spaced_day_labels.append(None)
    return spaced_lines, spaced_day_labels, spaced_urgent_set
