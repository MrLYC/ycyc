#!/usr/bin/env python
# encoding: utf-8

import sys
from HTMLParser import HTMLParser
import re
from collections import namedtuple
import argparse

from ycyc.base.iterutils import dict_merge
from ycyc.base.filetools import safe_open_for_read, safe_open_for_write
from ycyc.base.adapter import main_entry


class InlineStyleConvertor(HTMLParser):
    StyleAttribute = namedtuple("StyleAttribute", ["key", "value"])
    Style = namedtuple("Style", ["selector", "attributes"])
    StyleLevelOrders = map(re.compile, [
        r"#\w+$",
        r"\.\w+$",
        r"\b\w+$",
        r"\*$",
    ])

    def __init__(self, output, style_txt, ignore=False):
        self.output = output
        self.styles = self.format_style(style_txt)
        self.is_ignore = ignore
        self.is_in_body = None
        HTMLParser.__init__(self)

    @classmethod
    def level_of(cls, selector):
        for i, rex in enumerate(cls.StyleLevelOrders):
            if rex.match(selector):
                break
        return i

    @classmethod
    def cmp_style(cls, a, b):
        return cmp(cls.level_of(a.selector), cls.level_of(b.selector))

    def sort_styles(self, styles):
        styles.sort(self.cmp_style, reverse=True)
        return styles

    def format_style(self, style_txt):
        style_txt = re.sub(r"/\*(\s|.)*?\*/", "", style_txt, re.M)
        styles = [
            i.split("{")
            for i in style_txt.split("}")
            if i.strip()
        ]
        results = {}
        for selector, attrs in styles:
            selector = selector.strip()
            if not selector:
                continue
            attributes = []
            for attr in attrs.split(";"):
                attr = attr.strip()
                if not attr:
                    continue
                k, v = attr.split(":")
                attributes.append(self.StyleAttribute(k.strip(), v.strip()))
            results[selector] = self.Style(selector, attributes)
        return results

    def css_dict(self, selector):
        css = {}
        styles = self.styles.get(selector)
        if styles:
            for attr in styles.attributes:
                css[attr.key] = attr.value
        return css

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.is_in_body = True

        attrs = dict(attrs)

        if self.is_in_body:
            inline_style = attrs.pop("style", "")
            if self.is_ignore:
                styles_list = []
            else:
                styles_list = [dict(
                    i.strip().split(":")
                    for i in inline_style.split(";")
                    if i.strip()
                )]

            eid = attrs.get("id")
            if eid:
                styles_list.append(self.css_dict("#%s" % eid))

            for cls in attrs.get("class", "").split():
                styles_list.append(self.css_dict(".%s" % cls))

            styles_list.append(self.css_dict(tag))
            styles_list.append(self.css_dict("*"))

            if styles_list:
                styles = dict_merge(styles_list)
            if styles:
                styles_items = styles.items()
                styles_items.sort(lambda a, b: cmp(a[0], b[0]))
                attrs["style"] = "; ".join("%s:%s" % i for i in styles_items)

        attr_str = " ".join("%s=\"%s\"" % i for i in attrs.items())
        self.output.write(
            "<{tag}{attrs}>".format(
                tag=tag, attrs=" %s" % attr_str if attr_str else "",
            )
        )

    def handle_endtag(self, tag):
        if tag == "body":
            self.is_in_body = False

        self.output.write(
            "</{tag}>".format(tag=tag)
        )

    def handle_data(self, data):
        self.output.write(data)

    def feed(self, html):
        self.is_in_body = False
        return HTMLParser.feed(self, html)


@main_entry
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("base_file")
    arg_parser.add_argument(
        "-s", "--style",
        help="css file"
    )
    arg_parser.add_argument(
        "-o", "--output", default=None,
        help="output file",
    )
    arg_parser.add_argument(
        "-i", "--ignore", action="store_true", default=False,
        help="ignore inline style",
    )
    args = arg_parser.parse_args()

    with safe_open_for_read(args.base_file) as fp:
        html = fp.read()

    if args.style:
        with safe_open_for_read(args.style) as fp:
            style = fp.read()
    else:
        style = ""

    if args.output:
        fp = safe_open_for_write(args.output)
    else:
        fp = sys.stdout
    with fp:
        parser = InlineStyleConvertor(fp, style, args.ignore)
        parser.feed(html)
