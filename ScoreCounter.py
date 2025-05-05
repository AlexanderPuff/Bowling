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

    

class BowlingScore:

    def __init__(self, throws: list[int] = []):
        self.frames = []
        self.cur_frame = Frame()
        for throw in throws:
            self.score_ball(throw)

        
    
    def reward_strikes_spares(self, new_throw):
        '''
        Go through the last frames and increase their score if they were a strike or spare.
        '''
        frames = self.frames[:9]
        for frame in frames[-2:]:
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
                last_frame.score_from_future -= 1
                last_frame.score += knocked_pins
                last_frame.throws.append(knocked_pins)
                self.reward_strikes_spares(knocked_pins)
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
        if not self.frames: return [0] # for empty games
        return list(accumulate([frame.score for frame in self.frames]))
