# Orko's Todo Tool

Small, terminal-first todo list CLI with styled output.

Installation

Install locally from this directory:

```
pip install .
```

Or install directly from a Git repository:

```
pip install git+https://github.com/<yourname>/orkos-todo-tool.git
```

Usage

After installation the `orkos-todo` and `todo` console scripts are available. Example:

```
todo list
todo add "Buy groceries"
todo urgent 1
```

Notes

- The executable `todo` in this package is a convenience wrapper for running the package locally.
- Configure colors via `todo personalize`.
