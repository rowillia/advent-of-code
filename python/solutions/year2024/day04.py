"""
--- Day 4: Ceres Search ---
"Looks like the Chief's not here. Next!" One of The Historians pulls out a
device and pushes the only button on it. After a brief flash, you recognize the
interior of the Ceres monitoring station!

As the search for the Chief continues, a small Elf who lives on the station tugs
on your shirt; she'd like to know if you could help her with her word search
(your puzzle input). She only has to find one word: XMAS.

This word search allows words to be horizontal, vertical, diagonal, written
backwards, or even overlapping other words. It's a little unusual, though, as
you don't merely need to find one instance of XMAS - you need to find all of
them. Here are a few ways XMAS might appear, where irrelevant characters have
been replaced with .:
..X...
.SAMX.
.A..A.
XMAS.S
.X....

The actual word search will be full of letters instead. For example:

MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX

In this word search, XMAS occurs a total of 18 times; here's the same word
search again, but where letters not involved in any XMAS have been replaced with
.:

....XXMAS.
.SAMXMS...
...S..A...
..A.A.MS.X
XMASAMX.MM
X.....XA.A
S.S.S.S.SS
.A.A.A.A.A
..M.M.M.MM
.X.X.XMASX

Take a look at the little Elf's word search. How many times does XMAS appear?



--- Part Two ---
The Elf looks quizzically at you. Did you misunderstand the assignment?

Looking for the instructions, you flip over the word search to find that this
isn't actually an XMAS puzzle; it's an X-MAS puzzle in which you're supposed to
find two MAS in the shape of an X. One way to achieve that is like this:

M.S
.A.
M.S

Irrelevant characters have again been replaced with . in the above diagram.
Within the X, each MAS can be written forwards or backwards.

Here's the same example from before, but this time all of the X-MASes have been
kept instead:

.M.S......
..A..MSMS.
.M.S.MAA..
..A.ASMSM.
.M.S.M....
..........
S.S.S.S.S.
.A.A.A.A..
M.M.M.M.M.
..........

In this example, an X-MAS appears 9 times.

Flip the word search from the instructions back over to the word search side and
try again. How many times does an X-MAS appear?
"""

from python.common.point import Point

TARGET = "XMAS"


def safe_get(grid: list[str], loc: Point) -> str | None:
    if not (0 <= loc.x < len(grid[0]) and 0 <= loc.y < len(grid)):
        return None
    return grid[loc.y][loc.x]


def search(grid: list[str], loc: Point, step: Point) -> bool:
    for char in TARGET:
        if safe_get(grid, loc) == char:
            loc += step
        else:
            return False
    return True


def is_xmas(grid: list[str], loc: Point) -> bool:
    diags = ((Point(x=-1, y=-1), Point(x=1, y=1)), (Point(x=-1, y=1), Point(x=1, y=-1)))
    if safe_get(grid, loc) == "A":
        for diag in diags:
            if {safe_get(grid, loc + p) for p in diag} != set("MS"):
                return False
        return True
    return False


def part1(text: str) -> int | None:
    grid = text.splitlines()
    count = 0
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            count += sum(
                int(search(grid, Point(x, y), adj))
                for adj in Point(0, 0).adjacent_points(allow_negative=True)
            )
    return count


def part2(text: str) -> int | None:
    grid = text.splitlines()
    count = 0

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            loc = Point(x, y)
            count += int(is_xmas(grid, loc))
    return count
