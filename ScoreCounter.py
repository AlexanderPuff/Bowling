from itertools import accumulate

NR_THROWS = 10
NR_PINS = 10


class Frame:

    def __init__(self):
        self.throws = []
        self.score = 0
        self.score_from_future = 0
        self.completed = False
        

    def score_ball(self, knocked_pins: int):
        """
        Score a ball which knocked down a number of pins.

        Also set completed to True if this ball completes a frame.
        """

        # strike
        if knocked_pins == NR_PINS and not self.throws:
            self.throws = [NR_PINS]
            self.score = NR_PINS
            self.score_from_future = 2
            self.completed = True
            return

        # first ball of this frame
        if len(self.throws) == 0:
            self.throws = [knocked_pins]
            self.score = knocked_pins
            return

        # second ball of this frame
        self.throws.append(knocked_pins)
        self.score += knocked_pins

        # spare
        if self.throws[0] + knocked_pins == NR_PINS:
            self.score_from_future = 1

        self.completed = True


    def to_symbols(self, is_last=False) -> list[str]:
        """Returns a list of three symbols used for displaying this frame. If this is the last frame of a game, set is_last = True."""
        if not is_last:
            # strike
            if self.throws[0] == NR_PINS:
                return ["", "X", ""]

            # spare
            if sum(self.throws) == NR_PINS:
                return [self.throws[0], "/", ""]

            # fill up partial frames
            return extend_to(self.throws, 2, ["-"]) + [""]

        # if this is the final frame:
        symbols = ["X" if t == NR_PINS else t for t in self.throws]
        symbols = extend_to(symbols, 3, ["-"])
        if (
            len(self.throws) >= 2
            and self.throws[0] + self.throws[1] == NR_PINS
            and self.throws[1]
        ):
            symbols[1] = "/"

        return symbols



class BowlingScore:

    def __init__(self, throws: list[int] = []):
        self.frames = []
        self.cur_frame = Frame()
        self.done = False
        for throw in throws:
            self.score_ball(throw)


    def reward_strikes_spares(self, new_throw):
        """
        Go through the last frames and increase their score if they were a strike or spare.
        """
        for frame in self.frames[-2:]:
            if frame.score_from_future:
                frame.score_from_future -= 1
                frame.score += new_throw


    def score_ball(self, knocked_pins: int):
        if knocked_pins < 0 or knocked_pins > NR_PINS:
            raise ValueError(f"Bowling only has {NR_PINS} pins.")

        # extra logic for the last frame
        if len(self.frames) == NR_THROWS:
            last_frame = self.frames[-1]
            if last_frame.score_from_future:
                last_frame.throws.append(knocked_pins)
                self.reward_strikes_spares(knocked_pins)
                if not last_frame.score_from_future:
                    self.done = True
                return

        if len(self.frames) >= NR_THROWS:
            raise ValueError("The game is already over.")

        if self.cur_frame.throws and knocked_pins + self.cur_frame.throws[0] > NR_PINS:
            raise ValueError(f"Bowling only has {NR_PINS} pins.")

        self.reward_strikes_spares(knocked_pins)
        self.cur_frame.score_ball(knocked_pins)

        if self.cur_frame.completed:
            self.frames.append(self.cur_frame)

            # if this is our tenth frame and if it doesn't need any extra balls for scoring, set done
            if len(self.frames) == NR_THROWS and not self.cur_frame.score_from_future:
                self.done = True

            self.cur_frame = Frame()


    def prefix_scores(self) -> list[int]:
        """
        Returns a list of scores, cumulatively adding them up; One entry for each frame.
        """
        if not self.frames:
            return []  # for empty games

        scores = [frame.score for frame in self.frames]
        # add score for partially completed frames
        if self.cur_frame and self.cur_frame.throws:
            scores.append(self.cur_frame.score)
        return list(accumulate(scores))



def extend_to(input: list | str, target_len: int, padding: list | str) -> list | str:
    """
    Extends input list or string to given length by appending padding. Note: if input is a string, padding should be exactly one character.
    """

    if type(input) == str and len(padding) > 1:
        raise ValueError("This function only appends single characters.")

    return input + padding * (target_len - len(input))
