#!/usr/bin/env python
# encoding: utf-8

import tokenize
from token import tok_name
import ast
import sys
import logging
import logging.config
from collections import deque, namedtuple
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

logger = logging.getLogger("root")
TokenPoint = namedtuple("TokenPoint", ["row", "col"])
Token = namedtuple("Token", [
    "type", "token", "start_at", "end_at", "source_line",
])
Macro = namedtuple("Macro", [
    "mark", "name", "args",
])
TokenNames = dict(tok_name)
TokenNames[54] = "NEWLINE"
TokenNames[-1] = "SPACE"


class TokenReader(object):

    @classmethod
    def gen_split_lines(cls, code):
        base = 0
        for i, c in enumerate(code):
            if c == "\n":
                yield code[base: base + i + 1]
                base = i + 1
        line = code[base:]
        if line:
            yield line

    def __init__(self, code):
        self.tokens = deque()
        self.buffer_index = 0
        self.handle_tokens(code)

    def handle_tokens(self, code):
        self.tokens.clear()
        self.buffer_index = 0
        gen_tokens = tokenize.generate_tokens(
            lambda: next(self.gen_split_lines(code)),
        )
        row = 0
        col = 0
        for type_, token, start_at, end_at, source_line in gen_tokens:
            start_at = TokenPoint(*start_at)
            end_at = TokenPoint(*end_at)
            type_ = TokenNames[type_]
            token = Token(type_, token, start_at, end_at, source_line)
            self.tokens.append(token)


class CleanConfig(object):
    NAME = "default"
    BEGIN_MARK = "&BEGIN"
    END_MARK = "&END"

    def __init__(self, **kwargs):
        self.in_header = True
        self.name = self.NAME
        self.begin_mark = self.BEGIN_MARK
        self.end_mark = self.END_MARK
        self.debug = False

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
    tokens = tokenize.generate_tokens(StringIO(code).readline)
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
            StringIO(code).readline,
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
            type_ = TokenNames[type_]
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
            logger.debug("[-] cleaned: %s", self.line)

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

    def handle_newline(self, token):
        if self.line:
            self.line_end()
        else:
            self.write_line(token.token)

    def handle_comment(self, token):
        self.line = None
        if self.conf.in_header:
            self.handle_header(token)
        else:
            cleaned_line = token.source_line[:token.start_at.col] + \
                token.source_line[token.end_at.col:]

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

    def handle_default(self, token):
        self.conf.in_header = False
        if self.line and self.line != token.source_line:
            self.line_end()
            self.line_start()
        self.line = token.source_line

    def handle_string(self, token):
        source_lines = [i + "\n" for i in token.source_line.split("\n")]
        source_lines[-1] = source_lines[-1][:-1]
        start_row = token.start_at.row
        end_row = token.end_at.row - start_row + 1
        lines = source_lines[:end_row]
        if len(lines) == 1:
            return self.handle_default(token)
        line0 = lines[0]
        if not self.line or not self.line.endswith(line0):
            self.line = line0
        self.line_end()
        map(self.write_line, lines[1:-1])
        line_1 = lines[-1] + "".join(source_lines[end_row:])
        self.line = line_1

    def handle_token(self, token):
        handlers = {
            "NEWLINE": self.handle_newline,
            "COMMENT": self.handle_comment,
            "STRING": self.handle_string,
        }
        handler = handlers.get(token.type, self.handle_default)
        handler(token)

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
    parser.add_argument(
        "-b", "--begin_mark", default=CleanConfig.BEGIN_MARK,
        help="begin mark of macro block",
    )
    parser.add_argument(
        "-e", "--end_mark", default=CleanConfig.END_MARK,
        help="end mark of macro block",
    )
    parser.add_argument(
        "-n", "--name", default=CleanConfig.NAME,
        help="name of environment",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="debug mode",
    )
    parser.add_argument("-o", "--output", help="file to write content")
    args = parser.parse_args()
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'datefmt': '[%d/%b/%Y %H:%M:%S]',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            "root": {
                'handlers': ['console'],
                'level': 'DEBUG' if args.debug else "INFO",
            }
        },
    })

    if args.path == "-":
        code = sys.stdin.read()
    else:
        with open(args.path, "rt") as fp:
            code = fp.read()

    try:
        cleaner = CodeCleaner(code, config={
            "name": args.name,
            "begin_mark": args.begin_mark,
            "end_mark": args.end_mark,
        })
        content = cleaner.clean()
    except CleanError as error:
        print(str(error))
        token = error.token
        if token:
            print(
                token.source_line[:token.start_at.col] +
                BColors.WARNING +
                token.source_line[token.start_at.col:token.end_at.col] +
                BColors.ENDC +
                token.source_line[token.end_at.col:]
            )
        sys.exit(1)

    output = args.path if args.write_back else args.output
    if output:
        with open(output, "wt") as fp:
            fp.write(content)
    else:
        print(content)


if __name__ == '__main__':
    main()
