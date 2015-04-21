#!/usr/bin/env python
# encoding: utf-8


import re


def template_render(template, model):
    parts = []
    for part in re.split(r"{{([\.\w]+?)}}", template):
        parts.append(str(
            part if len(parts) % 2 == 0 else
            reduce(lambda m, k: m[k], part.split("."), model)))
    return "".join(parts)
