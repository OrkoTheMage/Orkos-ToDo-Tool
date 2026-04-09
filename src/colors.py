# colors.py - functions for parsing color specifications and loading styles

from config import load_personalization


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
    names = {
        'black':'30','red':'31','green':'32','yellow':'33','blue':'34','magenta':'35','cyan':'36','white':'37',
        'bright_black':'90','bright_red':'91','bright_green':'92','bright_yellow':'93','bright_blue':'94','bright_magenta':'95','bright_cyan':'96','bright_white':'97'
    }
    if v in ('reset','rst','0'):
        return '\033[0m'

    def _blend_to_base(user_rgb, alpha=0.35, base_rgb=(70, 60, 70)):
        # Blend a user-specified RGB towards a darker base so background
        # colors remain readable when used as terminal backgrounds.
        r = int(user_rgb[0] * alpha + base_rgb[0] * (1 - alpha))
        g = int(user_rgb[1] * alpha + base_rgb[1] * (1 - alpha))
        b = int(user_rgb[2] * alpha + base_rgb[2] * (1 - alpha))
        return (r, g, b)

    name_to_rgb = {
        'black': (0,0,0),'red': (205,49,49),'green': (13,188,121),'yellow': (229,229,16),
        'blue': (36,114,200),'magenta': (188,63,188),'cyan': (17,168,205),'white': (229,229,229),
        'bright_black': (102,102,102),'bright_red': (255,85,85),'bright_green': (75,255,150),'bright_yellow': (255,255,85),
        'bright_blue': (85,153,255),'bright_magenta': (255,125,255),'bright_cyan': (85,255,255),'bright_white': (255,255,255)
    }

    if v in names:
        code = names[v]
        if is_bg:
            # For background colors prefer an RGB blend for nicer blocks
            # otherwise fall back to the simple SGR background code.
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

    # Accept both `#rrggbb` and bare `rrggbb` hex formats.
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
            # Hex colors: use 24-bit SGR sequences. For background, blend
            # the color slightly towards the base for improved contrast.
            if is_bg:
                br, bgc, bb = _blend_to_base((r,g,b))
                return f"\033[48;2;{br};{bgc};{bb}m"
            return f"\033[38;2;{r};{g};{b}m"
        except Exception:
            pass

    # Accept SGR-like raw specifications such as "38;2;R;G;B" or "38;5;n"
    # and also allow passing them directly.
    if ';' in v:
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
            if len(parts) >= 3 and parts[0] in ('38', '48') and parts[1] == '5':
                n = int(parts[2])
                if 0 <= n <= 255:
                    if is_bg and parts[0] == '38':
                        return f"\033[48;5;{n}m"
                    return f"\033[{v}m"
        except Exception:
            return ''
        return ''

    # Numeric SGR codes (e.g. 31, 91) are also supported and mapped to
    # either foreground or blended background sequences depending on context.
    if v.isdigit():
        try:
            num = int(v)
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
    return ''


def load_style():
    defaults = {
        'BG': '\033[48;2;70;60;70m',
        'BFG': '\033[38;2;125;125;125m',
        'ART': '\033[1;37m',
        'MAG': '\033[1;35m',
        'RST': '\033[0m',
        'CYN': '\033[1;36m',
        'YEL': '\033[93m',
        'GRN': '\033[92m',
        'RED': '\033[91m',
        'styled': True,
    }
    try:
        cfg = load_personalization()
        if cfg:
            defaults.update(cfg)
    except Exception:
        pass
    return defaults
