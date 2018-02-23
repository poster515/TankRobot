from enum import Enum


class Operation(Enum):
    """Operations"""

    DELETED = 1
    INSERTED = 2
    SUBSTITUTED = 3

    def __str__(self):
        return str(self.name.lower())


def distances(a, b):
    """Calculate edit distance from a to b"""

    # need to create matrix[][] where matrix[0][0] is the top-left corner
    # and matrix[len(a)][len(b)] is the bottom-right corner
    matrix = []

    for i in range(0, len(a) + 1):
        matrix.append([])
        for j in range(0, len(b) + 1):
            matrix[i].append((0, None))

    # each element of matrix[i][j] contains a tuple (cost, Operation), where:
    # cost = edit distance between first i chars of 'a' and first j chars of 'b'
    # Operation = last operation taken in an optimal sequence

    #  [0]   b[0]    b[1]    b[2]    b[3]
    # a[0]  ...
    # a[1]
    # a[2]
    # a[3]

    # matrix[0][0] = (0, None) # this 0th element doesn't cost anything

    # Now, finishing initializing the first column and row
    for i in range(1, len(a) + 1):
        matrix[i][0] = (i, Operation.DELETED)

    for j in range(1, len(b) + 1):
        matrix[0][j] = (j, Operation.INSERTED)

    for i in range(1, len(a) + 1):
        matrix.append([])
        for j in range(1, len(b) + 1):
            matrix[i][j] = (min(
                (matrix[i - 1][j][0] + 1, Operation.DELETED),
                (matrix[i][j - 1][0] + 1, Operation.INSERTED),
                ((matrix[i - 1][j - 1][0] + (0 if a[i - 1] == b[j - 1] else 1), Operation.SUBSTITUTED)),
                key = lambda x: x[0]))

    return matrix
