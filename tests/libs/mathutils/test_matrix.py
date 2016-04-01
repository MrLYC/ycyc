from unittest import TestCase

from ycyc.libs.mathutils.matrix import Matrix


class TestMatrix(TestCase):
    def assertMatrixEqualAs(self, matrix, table):
        for mr, tr, r in zip(matrix, table, range(matrix.row_n)):
            for mc, tc, c in zip(mr, tr, range(matrix.col_n)):
                self.assertEqual(mc, tc)
            else:
                self.assertEqual(c, matrix.col_n - 1)
        else:
            self.assertEqual(r, matrix.row_n - 1)

    def test_construction(self):
        m = Matrix(1, 1)
        self.assertEqual(m[0, 0], m[0][0])
        self.assertEqual(m[0, 0], 0)

        m = Matrix(3, 2, [[1], [2, 3]])
        self.assertMatrixEqualAs(m, [
            [1, 0],
            [2, 3],
            [0, 0]
        ])

        m = Matrix.from_table([
            [1, 2, 3],
            [4, 5, 6],
        ])
        self.assertIsInstance(m, Matrix)
        self.assertEqual(m.row_n, 2)
        self.assertEqual(m.col_n, 3)
        self.assertMatrixEqualAs(m, [
            [1, 2, 3],
            [4, 5, 6],
        ])

        m = Matrix.from_table([
            [1, 2],
            [4, 5, 6],
            [7],
        ], init_val=0)
        self.assertIsInstance(m, Matrix)
        self.assertEqual(m.row_n, 3)
        self.assertEqual(m.col_n, 3)
        self.assertMatrixEqualAs(m, [
            [1, 2, 0],
            [4, 5, 6],
            [7, 0, 0],
        ])

    def test_equal(self):
        m1 = Matrix.from_table([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
        ])
        m2 = Matrix.from_table([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
        ])
        self.assertEqual(m1, m2)

    def test_multiplication(self):
        m1 = Matrix.from_table([
            [1, 2, 3],
            [4, 5, 6],
        ])
        m2 = Matrix.from_table([
            [1, 4],
            [2, 5],
            [3, 6],
        ])
        self.assertMatrixEqualAs(m1 * m2, [
            [14, 32],
            [32, 77],
        ])

        m1 = Matrix.from_table([
            [2, 1],
            [4, 3],
        ])
        self.assertMatrixEqualAs(2 * m1, [
            [4, 2],
            [8, 6],
        ])

        m1 = Matrix.from_table([
            [20, 20, 18],
            [24, 16, 27],
            [21, 19, 22],
        ])
        m2 = Matrix.from_table([
            [12, 1.2],
            [14, 1.3],
            [16, 1.5],
        ])
        self.assertMatrixEqualAs(m1 * m2, [
            [808, 77],
            [944, 90.1],
            [870, 82.9],
        ])

        m1 = Matrix.from_table([
            [2, 4],
            [1, 2],
        ])
        m2 = Matrix.from_table([
            [2, -2],
            [-1, 1],
        ])
        self.assertMatrixEqualAs(m1 * m2, [
            [0, 0],
            [0, 0],
        ])
        self.assertMatrixEqualAs(m2 * m1, [
            [2, 4],
            [-1, -2],
        ])

    def test_addition(self):
        m1 = Matrix.from_table([
            [2, -4, 0],
            [3, -2, 2],
        ])
        m2 = Matrix.from_table([
            [1, 0, 3],
            [2, -1, 1],
        ])
        self.assertMatrixEqualAs(m1 + m2, [
            [3, -4, 3],
            [5, -3, 3],
        ])

    def test_subduction(self):
        m1 = Matrix.from_table([
            [2, -4, 0],
            [3, -2, 2],
        ])
        m2 = Matrix.from_table([
            [1, 0, 3],
            [2, -1, 1],
        ])
        self.assertMatrixEqualAs(m1 - m2, [
            [1, -4, -3],
            [1, -1, 1],
        ])

    def test_transpose_matrix(self):
        m = Matrix.from_table([
            [1, 2],
            [3, 4],
        ]).transpose_matrix()
        self.assertMatrixEqualAs(m, [
            [1, 3],
            [2, 4],
        ])

        m = Matrix.from_table([
            [1, 2],
            [3, 4],
            [5, 6],
        ]).transpose_matrix()
        self.assertMatrixEqualAs(m, [
            [1, 3, 5],
            [2, 4, 6],
        ])
