#!/usr/bin/env python3
import os
import sys

# Ensure src directory is on sys.path so imports work when running directly
here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if here not in sys.path:
    sys.path.insert(0, here)

from main import main


if __name__ == '__main__':
    main()
