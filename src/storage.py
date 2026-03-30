# storage.py - functions for loading/saving todos and resolving identifiers

import os
import json
import tempfile
import difflib


def todos_path():
    return os.path.expanduser('~/.todos.json')


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

    # First, try simple substring matches (case-insensitive). If there is
    # exactly one match we return it; if multiple matches occur we return
    # the first one (caller may present choices in other flows).
    subs = [i for i, txt in enumerate(texts) if identifier.lower() in txt.lower()]
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        return subs[0]

    best_idx = None
    best_score = 0.0
    # Fall back to fuzzy matching (difflib). We compute similarity scores
    # against each todo text and accept the best match if it meets the
    # provided cutoff threshold.
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


def parse_days_arg(s):
    if not s:
        return []
    mapping = {
        'mon': 'monday', 'monday': 'monday', 'tue': 'tuesday', 'tues': 'tuesday', 'tuesday': 'tuesday',
        'wed': 'wednesday', 'wednesday': 'wednesday', 'thu': 'thursday', 'thurs': 'thursday', 'thursday': 'thursday',
        'fri': 'friday', 'friday': 'friday', 'sat': 'saturday', 'saturday': 'saturday',
        'sun': 'sunday', 'sunday': 'sunday'
    }
    # Normalize comma-separated parts and map common abbreviations to
    # full weekday names. Remove duplicates while preserving order.
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
    # Atomic write: write to temp file then replace the target path
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
