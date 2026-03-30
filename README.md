Orko's Todo Tool
=================

![Main view](docs/screenshots/Maintodo.png)

A small, terminal-first todo list CLI with styled, readable output. Designed for quick keyboard-driven workflows: add items, mark urgent, schedule tasks, update entries, and personalize the visual style to match your terminal.
Orko's Todo Tool
=================

Section 1 — Overview
---------------------

![Main view](docs/screenshots/Maintodo.png)

A small, terminal-first todo list CLI with styled, readable output. Designed for quick keyboard-driven workflows: add items, mark urgent, schedule tasks, update entries, and personalize the visual style to match your terminal.

Features
--------

- Fast CLI: `list`, `add`, `update`, `remove`, `urgent`, `scheduled`, and `personalize` commands.
- Styled terminal output with configurable colors and accenting for urgent/scheduled items.
- Simple persistence in a JSON file (`~/.todos.json`) with fuzzy-text lookup for quick updates.
- Small, single-file CLI wrapper for easy from-source use and packaging via setuptools.

![Scheduled view](docs/screenshots/Scheduledtodo.png)

Personalization
---------------

Customize colors and highlight behavior with `todo personalize`. You can set background, title, urgent, and scheduled colors using named colors, hex values, or SGR codes. Personalization is stored in `~/.todos_config.json` so your settings follow you between sessions.

![Personalize view](docs/screenshots/Personalizetodo.png)

Section 2 — Installation & Usage
--------------------------------

Installation
------------

Quick install (recommended):

```bash
pip install --user .
```

System-wide install (requires sudo):

```bash
sudo pip install .
```

Install from git:

```bash
pip install --user git+https://github.com/<yourname>/orkos-todo-tool.git
```

Running from source
-------------------

Run the CLI script directly from the project root when developing or trying changes:

```bash
python3 todo list
```

Make `todo` available on your PATH
---------------------------------

If you prefer a shortcut instead of installing, symlink the project script:

```bash
# user-local
ln -s $PWD/todo ~/.local/bin/todo

# system-wide (requires sudo)
sudo ln -s $PWD/todo /usr/local/bin/todo
```

If you previously had an installed wrapper at `~/.local/bin/todo`, back it up first:

```bash
mv ~/.local/bin/todo ~/.local/bin/todo.orig
```

Notes
-----

- `pyproject.toml` declares the build backend and `setup.cfg` contains package metadata and console entry points — both are part of the source and should be committed.
- `*.egg-info/` is generated at build/install time and is excluded via `.gitignore`.
- If you see `ModuleNotFoundError: No module named 'orkos_todo_tool'` when running a symlinked `todo`, ensure the symlink points to the project script or install the package with `pip` so Python can import it.

Usage examples
--------------

```bash
todo list
todo add "Buy groceries"
todo update 2 "Buy milk and eggs"
todo remove 2
todo urgent 1
todo scheduled
todo personalize background "#1e90ff"
```

Configuration
-------------

- Run `todo personalize` to edit color keys such as `background`, `title1`, `title2`, `urgent`, and `scheduled`.

Credit
------

Aeryn G (OrkoTheMage)
