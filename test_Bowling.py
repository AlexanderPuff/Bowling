from ScoreCounter import *
import pytest


@pytest.mark.parametrize(
    "throws, result",
    [
        ([1, 4, 4, 5, 6, 4, 5, 5, 10, 0, 1, 7, 3, 6, 4, 10, 2, 8, 6], 133),
        ([10] * 12, 300),
        ([1, 9] * 10 + [10], 119),
        ([0] * 20, 0),
        ([8, 2] * 10 + [10], 182),
        ([0, 10] * 9 + [0, 10, 10], 110),
        ([0] * 19 + [10] * 2, 20),
        ([0] * 18 + [10] * 3, 30),
        ([10, 10, 10] + [0] * 14, 60),
    ],
)
def test_bowling_scorer(throws, result):
    scorer = BowlingScore(throws)
    assert scorer.prefix_scores()[-1] == result


@pytest.mark.parametrize(
    "throws, exception, message",
    [
        ([11], ValueError, "Bowling only has 10 pins."),
        ([9, 9], ValueError, "Bowling only has 10 pins."),
        ([0] * 21, ValueError, "The game is already over."),
        ([0] * 19 + [10] * 3, ValueError, "The game is already over."),
        ([-4], ValueError, "Bowling only has 10 pins."),
    ],
)
def test_bowling_errors(throws, exception, message):
    with pytest.raises(exception, match=message):
        scorer = BowlingScore(throws)


# only need to test "legal" states here because all others were caught beforehand
@pytest.mark.parametrize(
    "throws, isFinal, symbols",
    [
        ([10, 0], False, ["", "X", ""]),
        ([1, 1], False, [1, 1, ""]),
        ([0, 10], False, [0, "/", ""]),
        ([5, 5], False, [5, "/", ""]),
        
        ([0, 0], True, [0, 0, "-"]),
        ([5, 5, 5], True, [5, "/", 5]),
        ([4, 6, 10], True, [4, "/", "X"]),
        ([10, 10, 10], True, ["X"] * 3),
        ([10, 0, 10], True, ["X", 0, "X"]),
        ([10, 6, 4], True, ["X", 6, 4]),
    ],
)
def test_to_symbols(throws, isFinal, symbols):
    frame = Frame()
    frame.throws = throws
    assert frame.to_symbols(isFinal) == symbols
