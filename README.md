# Orko's Todo Tool

Small, terminal-first todo list CLI with styled output.
Installation

Quick install (recommended):

```
pip install --user .
```

System-wide install (requires sudo):

```
sudo pip install .
```

Install from git:

```
pip install --user git+https://github.com/<yourname>/orkos-todo-tool.git
```

Running from source

If you prefer to run the project without installing, you can run the script directly from the project root:

```
python3 todo list
```

Making the `todo` command available

When installed via pip the `todo` console script is created for you. If you run from source and want a shortcut on your PATH, create a symlink to the project `todo` script:

```
# create a user-local symlink
ln -s $PWD/todo ~/.local/bin/todo

# or create a system symlink (requires sudo)
sudo ln -s $PWD/todo /usr/local/bin/todo
```

Notes about symlinks and PATH

- If you previously had a different `todo` wrapper in `~/.local/bin`, back it up first (for example `mv ~/.local/bin/todo ~/.local/bin/todo.orig`).
- When using `sudo` you may need to preserve your PATH to run the user-local command: `sudo env "PATH=$PATH" todo list`.
- The project `todo` script will fall back to loading the local `__init__.py` when run from the project directory. If you symlink to the script make sure the symlink resolves to the project script so it can locate the package files.

Usage examples

```
todo list
todo add "Buy groceries"
todo update 2 "Buy milk and eggs"
todo remove 2
```

Configuration

- Configure colors and personalization using `todo personalize`.

Troubleshooting

- If you see `ModuleNotFoundError: No module named 'orkos_todo_tool'` when running a symlinked `todo` command, ensure the symlink points to the project `todo` script (not an installed wrapper) or install the package with `pip` so Python can import it.

Credit

Small, terminal-first todo list CLI with styled output.
