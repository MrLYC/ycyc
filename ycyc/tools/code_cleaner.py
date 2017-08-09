#!/usr/bin/env python
# encoding: utf-8

import tokenize
from token import tok_name
import StringIO
import os
import ast
from collections import deque, OrderedDict, namedtuple

TokenPoint = namedtuple("TokenPoint", ["row", "col"])
Token = namedtuple("Token", [
    "type", "token", "start_at", "end_at", "source_line",
])
Macro = namedtuple("Macro", [
    "mark", "name", "args",
])

class CleanConfig(object):

    def __init__(self, **kwargs):
        self.in_header = True
        self.name = ""
        self.begin_mark = "&BEGIN"
        self.end_mark = "&END"

        for k, v in kwargs.items():
            setattr(self, k, v)

    def macro_dropblock(self, cleaner, args):
        def func(token):
            if token.type == "COMMENT":
                macro = cleaner.parse_macro_by_token(
                    token, [cleaner.conf.begin_mark, cleaner.conf.end_mark],
                )
                if not macro:
                    return False
                if macro.mark == cleaner.conf.begin_mark:
                    cleaner.clean_error("macro recursive", token)
                else:
                    return True
            return False

        for t in cleaner.read_token_until(func):
            pass

    def macro_notfor(self, cleaner, args):
        assert len(args) == 1
        name = args[0].strip("\"\'")
        if name == self.name:
            self.macro_dropblock(cleaner, args)

    def macro_onlyfor(self, cleaner, args):
        assert len(args) == 1
        name = args[0].strip("\"\'")
        if name != self.name:
            self.macro_dropblock(cleaner, args)


class BColors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def split_by_token(code):
    tokens = tokenize.generate_tokens(StringIO.StringIO(code).readline)
    return [i[1] for i in tokens if i[1].strip()]


def parse_macro(macro, marks):
    for mark in marks:
        if macro.startswith(mark):
            macro_content = macro[len(mark):].lstrip()
            macro_name, _, macro_args = macro_content.partition(" ")
            return Macro(
                mark=mark, name=macro_name,
                args=split_by_token(macro_args),
            )
    return None


class CleanError(Exception):
    def __init__(self, message, token):
        message = (
            "{message}\n"
            "token: {token.token}\n"
            "line: {token.start_at.row}"
        ).format(message=message, token=token)
        super(CleanError, self).__init__(message)
        self.token = token


class CodeCleaner(object):

    def __init__(self, code, bufsize=10, config=()):
        self.lines = []
        self.line = None
        self.finished = False
        self.conf = (
            config if isinstance(config, CleanConfig)
            else CleanConfig(**dict(config))
        )
        self.token_buffer = deque(maxlen=bufsize)
        self.token_gen = tokenize.generate_tokens(
            StringIO.StringIO(code).readline,
        )

    @property
    def content(self):
        return "".join(self.lines)

    @property
    def current_token(self):
        if self.token_buffer:
            return self.token_buffer[-1]
        return None

    @property
    def last_token(self):
        if len(self.token_buffer) > 1:
            return self.token_buffer[-2]
        return None

    def read_token_until(self, func):
        while True:
            token = self.read_token()
            if not token:
                break
            yield token
            if func(token):
                break

    def read_token(self):
        if self.finished:
            return None
        try:
            type_, token, start_at, end_at, source_line = next(self.token_gen)
            start_at = TokenPoint(*start_at)
            end_at = TokenPoint(*end_at)
            type_ = tok_name[type_]
            token = Token(type_, token, start_at, end_at, source_line)
            self.token_buffer.append(token)
            return token
        except StopIteration:
            self.finished = True
            return None

    def line_start(self, flush=True):
        if flush and self.line is not None:
            self.lines.append(self.line)
        self.line = ""

    def write_line(self, line, flush=True):
        self.line_start(flush)
        self.line = line
        self.line_end(flush)

    def line_end(self, flush=True):
        if flush and self.line is not None:
            self.lines.append(self.line)
        self.line = None

    def clean_error(self, message, token=None):
        raise CleanError(message, token)

    def parse_macro_by_token(self, token, marks):
        cleaned_comment = token.token.lstrip("\t #")
        return parse_macro(cleaned_comment, marks)

    def handle_header(self, token):
        if token.type != "COMMENT":
            self.conf.in_header = False
            return False
        self.line = token.source_line
        return True

    def handle_comment(self, token):
        if self.conf.in_header:
            self.handle_header(token)
        else:
            cleaned_line = (
                token.source_line[:token.start_at.col]
                + token.source_line[token.end_at.col:]
            )
            self.line = cleaned_line
            if cleaned_line.strip():
                return
        macro = self.parse_macro_by_token(
            token, [self.conf.begin_mark, self.conf.end_mark],
        )
        if not macro:
            return
        self.line = None
        if macro.mark == self.conf.end_mark:
            return
        macro_handler = getattr(
            self.conf, "macro_%s" % macro.name.lower(), None,
        )
        if macro_handler:
            macro_handler(self, macro.args)
        else:
            self.clean_error(
                "unknown macro: %s" % macro.name, token,
            )

    def handle_token(self, token):
        if token.type in ["NL", "NEWLINE"]:
            if self.line:
                self.line_end()
            else:
                self.write_line(token.token)
            return
        if token.type != "COMMENT":
            self.conf.in_header = False
            self.line = token.source_line
        else:
            self.line = None
            self.handle_comment(token)

    def clean(self, validate=True):
        self.line_start()
        while not self.finished:
            token = self.read_token()
            if token is None:
                break
            self.handle_token(token)
        self.line_end()
        self.finished = True
        content = self.content
        if validate:
            ast.parse(content)
        return content


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="clean python code")
    parser.add_argument("path", help="file path to handle")
    parser.add_argument(
        "-w", "--write_back", action="store_true",
        help="write content back to file"
    )
    parser.add_argument("-o", "--output", help="file to write content")
    args = parser.parse_args()

    with open(args.path, "rt") as fp:
        code = fp.read()

    try:
        cleaner = CodeCleaner(code)
        content = cleaner.clean()
    except CleanError as error:
        print(error.message)
        token = error.token
        if token:
            print(
                token.source_line[:token.start_at.col]
                + BColors.WARNING
                + token.source_line[token.start_at.col:token.end_at.col]
                + BColors.ENDC
                + token.source_line[token.end_at.col:]
            )

    output = args.path if args.write_back else args.output
    if output:
        with open(output, "wt") as fp:
            fp.write(content)
    else:
        print(content)

if __name__ == '__main__':
    main()
