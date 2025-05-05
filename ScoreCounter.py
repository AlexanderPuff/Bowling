from itertools import accumulate

class Frame:

    def __init__(self):
        self.throws = []
        self.score = 0
        self.score_from_future = 0
        self.completed = False

    def score_ball(self, knocked_pins: int):
        '''
        Score a ball which knocked down a number of pins.

        Also set completed to True if this ball completes a frame.
        '''

        #strike
        if knocked_pins == 10 and not self.throws:
            self.throws = [10]
            self.score = 10
            self.score_from_future = 2
            self.completed = True
            return
        
        #first ball of this frame
        if len(self.throws) == 0:
            self.throws = [knocked_pins]
            self.score = knocked_pins
            return
        
        #second ball of this frame
        self.throws.append(knocked_pins)
        self.score += knocked_pins

        #spare
        if self.throws[0] + knocked_pins == 10:
            self.score_from_future = 1

        self.completed = True

    def to_symbols(self, is_last = False):
        '''Returns a list of symbols later used for displaying this frame.'''
        if not is_last:
            # strike
            if self.throws[0] == 10:
                return(["   ", "X  "])
            # spare
            if sum(self.throws)==10:
                return([self.throws[0], "/  "])
            
            # fill up partial frames
            return self.throws + (2-len(self.throws)) * ["-"]
        
        symbols = ["X  " if t == 10 else t for t in self.throws]
        if len(self.throws) >= 2 and self.throws[0] + self.throws[1] == 10:
            symbols[1] = "/  "

        # completed finales might have a late spare
        if len(self.throws) == 3 and self.throws[1] + self.throws[2] == 10:
                symbols[2] = "/  "
        return symbols
        


    

class BowlingScore:

    def __init__(self, throws: list[int] = []):
        self.frames = []
        self.cur_frame = Frame()
        self.done = False
        for throw in throws:
            self.score_ball(throw)

        
    
    def reward_strikes_spares(self, new_throw):
        '''
        Go through the last frames and increase their score if they were a strike or spare.
        '''
        for frame in self.frames[-2:]:
            if frame.score_from_future:
                frame.score_from_future -= 1
                frame.score += new_throw


    def score_ball(self, knocked_pins: int):
        if knocked_pins < 0 or knocked_pins > 10:
            raise ValueError('Bowling only has 10 pins.')
        

        # extra logic for the last frame
        if len(self.frames) == 10:
            last_frame = self.frames[-1]
            if last_frame.score_from_future:
                last_frame.throws.append(knocked_pins)
                self.reward_strikes_spares(knocked_pins)
                if not last_frame.score_from_future: self.done=True
                return

        if len(self.frames) >= 10:
            raise ValueError('The game is already over.')
        
        if self.cur_frame.throws and knocked_pins + self.cur_frame.throws[0] > 10:
            raise ValueError('Bowling only has 10 pins.')
        
        self.reward_strikes_spares(knocked_pins)

        self.cur_frame.score_ball(knocked_pins)
        if self.cur_frame.completed:
            self.frames.append(self.cur_frame)
            self.cur_frame = Frame()

    def prefix_scores(self):
        if not self.frames: return [] # for empty games

        scores = [frame.score for frame in self.frames]
        # add score for partially completed frames
        if self.cur_frame and self.cur_frame.throws:
            scores.append(self.cur_frame.score)
        return list(accumulate(scores))
