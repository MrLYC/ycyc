#!/usr/bin/env python
# encoding: utf-8

try:
    import readline
    import rlcompleter
except ImportError:
    print("auto complete failed to install")
else:
    readline.parse_and_bind("tab: complete")
    print("auto complete installed")
