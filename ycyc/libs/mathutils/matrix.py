from collections import deque
from itertools import repeat
import os


class Matrix(object):

    @classmethod
    def from_table(cls, table, init_val=0):
        data = []
        row_n = 0
        col_n = 0

        for rn, r in enumerate(table):
            row = []
            for cn, c in enumerate(r):
                row.append(c)

                if col_n <= cn:
                    col_n = cn + 1
            data.append(row)
            if row_n <= rn:
                row_n = rn + 1

        return cls(row_n=row_n, col_n=col_n, matrix=data, init_val=init_val)

    @classmethod
    def check_size(
        cls, matrix, row_checker=lambda x: True, col_checker=lambda x: True
    ):
        if not row_checker(matrix.row_n) or not col_checker(matrix.col_n):
            raise ValueError("matrix size error: [%d, %d]" % (
                matrix.row_n, matrix.col_n,
            ))

    def __init__(self, row_n, col_n, matrix=None, init_val=0):
        self.init_val = init_val
        self.row_n = int(row_n)
        self.col_n = int(col_n)

        matrix = matrix or (
            repeat(init_val, col_n)
            for r in range(row_n)
        )
        self.data = deque((
            deque((c for c in r), maxlen=col_n)
            for r in matrix
        ), maxlen=row_n)

        self.make_sure_matrix_size()

    def make_sure_matrix_size(self):
        row_n = self.row_n
        col_n = self.col_n
        init_val = self.init_val
        data = self.data

        self.check_size(
            self,
            lambda x: x > 0,
            lambda x: x > 0,
        )

        for r in range(row_n):
            try:
                col = data[r]
                col_len = len(col)
                if col_len < col_n:
                    col.extend(repeat(init_val, col_n - col_len))
            except IndexError:
                data.append(deque(repeat(init_val, col_n)))

    def visit_with(self, callback):
        for i in range(self.row_n):
            for j in range(self.col_n):
                callback(i, j, self[i, j])

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, idx):
        if isinstance(idx, (tuple, list)):
            row_n, col_n = idx
            return self.data[row_n][col_n]
        return self.data[idx]

    def __setitem__(self, idx, val):
        if not isinstance(idx, (tuple, list)):
            raise ValueError("index type error: %s" % idx)

        row_n, col_n = idx
        if row_n >= self.row_n or col_n >= self.col_n:
            raise IndexError("index error: [%s, %s]" % (row_n, col_n))

        self.data[row_n][col_n] = val

    def __str__(self):
        output = []
        max_width = 0

        for r in self:
            line = []
            for c in r:
                element_str = str(c)
                line.append(element_str)

                element_str_len = len(element_str)
                if element_str_len > max_width:
                    max_width = element_str_len

            else:
                output.append(line)

        template = "%%%ds" % (max_width + 1)
        return os.linesep.join(
            ",".join(template % c for c in r)
            for r in output
        )

    def __eq__(self, other):
        if self.row_n != other.row_n or self.col_n != other.col_n:
            return False

        for mr, tr, r in zip(self, other, range(self.row_n)):
            for mc, tc, c in zip(mr, tr, range(self.col_n)):
                if mc != tc:
                    return False
            else:
                if c != self.col_n - 1:
                    return False
        else:
            if r != self.row_n - 1:
                return False
        return True

    def __add__(self, other):
        self.check_size(
            other,
            lambda x: self.row_n == x,
            lambda x: self.col_n == x,
        )

        matrix = Matrix(self.row_n, self.col_n)

        def add(i, j, val):
            matrix[i, j] = val + other[i, j]

        self.visit_with(add)
        return matrix

    def __sub__(self, other):
        self.check_size(
            other,
            lambda x: self.row_n == x,
            lambda x: self.col_n == x,
        )

        matrix = Matrix(self.row_n, self.col_n)

        def sub(i, j, val):
            matrix[i, j] = val - other[i, j]

        self.visit_with(sub)
        return matrix

    def __repr__(self):
        return str(self)

    def __mul__(self, other):
        self.check_size(
            other,
            lambda x: self.col_n == x,
        )

        matrix = Matrix(self.row_n, other.col_n)
        for i in range(self.row_n):
            for j in range(other.col_n):
                elememt = 0

                for k in range(self.col_n):
                    elememt += self[i, k] * other[k, j]
                else:
                    matrix[i, j] = elememt

        return matrix

    def __rmul__(self, other):
        matrix = Matrix(self.row_n, self.col_n, self)
        for i in range(self.row_n):
            for j in range(self.col_n):
                matrix[i, j] *= other
        return matrix

    def transpose_matrix(self):
        matrix = Matrix(self.col_n, self.row_n)
        for i in range(self.row_n):
            for j in range(self.col_n):
                matrix[j, i] = self[i, j]
        return matrix
