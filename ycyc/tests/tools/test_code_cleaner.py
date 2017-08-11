#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from textwrap import dedent

from ycyc.tools import code_cleaner


class TestCodeCleaner(TestCase):

    def clean(self, code, **conf):
        cleaner = code_cleaner.CodeCleaner(code, config=conf)
        content = cleaner.clean(True)
        return content

    def test1(self):
        code = dedent('''
        #!/usr/bin/env python
        # encoding: utf-8

        import test

        # remove me

        def test_func(x):
            for i in range(x):
                t = "this is %s" % x
                return t

        with open(
            "/tmp/test", "rt"
        ) as fp:
            print(test_func(fp.read()))
        ''')
        content = self.clean(code)
        code_lines = code.splitlines()
        content_lines = content.splitlines()
        self.assertEqual(code_lines[:2], content_lines[:2])
        self.assertNotIn("remove me", content)

    def test2(self):
        code = dedent('''
        # &BEGIN NOTFOR env1
        def getval():
            return 2
        # &END

        # &BEGIN NOTFOR env2
        def getval():
            return 1
        # &END

        x = getval()
        ''')

        code1 = self.clean(code, name="env1")
        env1 = {}
        exec(code1, env1, env1)
        self.assertEqual(env1["x"], 1)

        code2 = self.clean(code, name="env2")
        env2 = {}
        exec(code2, env2, env2)
        self.assertEqual(env2["x"], 2)

    def test3(self):
        code = dedent('''
        # &BEGIN NOTFOR env1
        def getval():
            return 2

        x = getval()
        ''')
        code1 = self.clean(code, name="env1")
        env1 = {}
        exec(code1, env1, env1)
        with self.assertRaises(KeyError):
            env1["x"]

    def test4(self):
        code = dedent('''
        # &BEGIN ONLYFOR env1
        def getval():
            return 1
        # &END

        # &BEGIN ONLYFOR env2
        def getval():
            return 2
        # &END

        x = getval()
        ''')

        code1 = self.clean(code, name="env1")
        env1 = {}
        exec(code1, env1, env1)
        self.assertEqual(env1["x"], 1)

        code2 = self.clean(code, name="env2")
        env2 = {}
        exec(code2, env2, env2)
        self.assertEqual(env2["x"], 2)

    def test5(self):
        code = dedent('''
        x = "111222333" \\
          .strip()
        ''')
        code1 = self.clean(code)
        env = {}
        env1 = {}
        exec(code, env, env)
        exec(code1, env1, env1)
        self.assertEqual(env1["x"], env["x"])

    def test6(self):
        code = dedent('''
        x = 1 # comment1
        # comment2
        ''')
        code1 = self.clean(code)
        self.assertNotIn("comment1", code1)
        self.assertNotIn("comment2", code1)

    def test7(self):
        code = dedent('''
        def f():
            """docstring
            """
            pass
        ''')
        code1 = self.clean(code)
        self.assertEqual(code, code1)

    def test8(self):
        code = dedent('''
        message = f(u"""
            hello %s
            hi %s
        """ % (
            "world",
            "me",
        ))
        ''')
        code1 = self.clean(code)
        self.assertEqual(code, code1)

    def test9(self):
        code = '''u"""
        123
        456
        """'''
        self.assertEqual(code, self.clean(code))

    def test10(self):
        code = dedent('''
        def getval():
            return 2

        # &END

        x = getval()
        ''')
        code1 = self.clean(code, name="env1")
        env1 = {}
        exec(code1, env1, env1)
        self.assertEqual(env1["x"], 2)
