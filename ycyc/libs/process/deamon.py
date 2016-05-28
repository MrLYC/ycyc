import os
import sys


class ChildForkFinished(Exception):
    pass


class DeamonProcess(object):

    def __init__(
        self, target=None, pidfile=None,
        stdin=None, stdout=None, stderr=None,
    ):
        self.target = target
        self._pid = None
        self.pidfile = pidfile or "/tmp/DeamonProcess.pid"
        self.stdin = stdin or "/dev/null"
        self.stdout = stdout or "/dev/null"
        self.stderr = stderr or self.stdout

    @property
    def pid(self):
        if self._pid is None:
            try:
                with open(self.pidfile, "rt") as fp:
                    self._pid = int(fp.readline())
            except (IOError, ValueError):
                pass
        return self._pid

    def run(self, *args, **kwargs):
        if not self.target:
            raise NotImplementedError()
        self.target(*args, **kwargs)

    def _fork_child_process(self):
        """
        Fork a child process which would not collected by the init.
        """
        try:
            pid = os.fork()
        except OSError as err:
            sys.stderr.write("fork #1 failed: %s" % err)

        if pid > 0:
            raise ChildForkFinished()

    def _wait_child_process(self):
        """
        Wait child process to exit to avoid a zombie process.
        """
        return os.wait()

    def _fork_deamon_process(self):
        """
        Grandchild process adopted by the init because child process
        has been exited.
        """
        try:
            pid = os.fork()
        except OSError as err:
            sys.stderr.write("fork #1 failed: %s" % err)
            sys.exit(1)

        if pid > 0:
            sys.exit(0)

    def _redirect_standard_file_descriptors(self):
        """
        Redirect stdin, stdout, stderr.
        """
        sys.stderr.flush()

        stdin = open(self.stdin, "r")
        os.dup2(stdin.fileno(), sys.stdin.fileno())

        stdout = open(self.stdout, "a+")
        sys.stdout.flush()
        os.dup2(stdout.fileno(), sys.stdout.fileno())

        stderr = open(self.stderr, "a+")
        sys.stderr.flush()
        os.dup2(stderr.fileno(), sys.stderr.fileno())

    def _daemonize(self):
        # move to background
        try:
            self._fork_child_process()
        except ChildForkFinished as err:
            self._wait_child_process()
            raise err

        # become session leader
        os.setsid()
        # change directory to root to avoid unmount error
        os.chdir("/")
        # reset the default umask file creation mask
        os.umask(0)

        # become process group leader
        self._fork_deamon_process()
        with open(self.pidfile, "w+") as fp:
            self._pid = os.getpid()
            fp.write("%s\n" % self._pid)

        # redirect standard file descriptors
        self._redirect_standard_file_descriptors()

    def start(self, args=(), kwargs=None):
        kwargs = kwargs or {}
        try:
            self._daemonize()
        except ChildForkFinished:
            return

        self.run(*args, **kwargs)
