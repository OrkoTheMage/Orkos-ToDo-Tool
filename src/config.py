#!/usr/bin/env python3
import os
import json
import tempfile


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
