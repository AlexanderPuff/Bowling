from itertools import accumulate

class Frame:

    fst_ball = 0
    snd_ball = 0
    #only used for final frame:
    thrd_ball = 0
    ball_nr = 1
    score = 0
    score_from_future = 0

    def score_ball(self, knocked_pins: int):
        '''
        Score a ball which knocked down a number of pins.

        Returns True if this completes this frame, False otherwise.
        '''

        #strike
        if knocked_pins == 10:
            self.fst_ball = 10
            self.score = 10
            self.score_from_future = 2
            return True
        
        #first ball of this frame
        if self.ball_nr == 1:
            self.ball_nr += 1
            self.fst_ball = knocked_pins
            self.score = knocked_pins
            return False
        
        #second ball of this frame
        self.snd_ball = knocked_pins
        self.score += knocked_pins

        #spare
        if self.fst_ball + knocked_pins == 10:
            self.score_from_future = 1

        return True

    

class BowlingScore:
    frames = []
    cur_frame = Frame()
    
    def reward_strikes_spares(self, new_throw):
        '''
        Go through the last frames and increase their score if they were a strike or spare.
        '''
        for frame in self.frames[-2:]:
            if frame.score_from_future:
                frame.score_from_future -= 1
                frame.score += new_throw


    def score_ball(self, knocked_pins: int):
        self.reward_strikes_spares(knocked_pins)

        if knocked_pins + self.cur_frame.fst_ball > 10:
            raise ValueError('Knocked down more than 10 pins')
        
        if len(self.frames) > 10:
            raise ValueError('The game is already over.')

        if len(self.frames) == 10:
            lst_frame = self.frames[-1]
            if lst_frame.score_from_future:
                lst_frame.score_from_future -= 1
                lst_frame.score += knocked_pins

                if not lst_frame.snd_ball:
                    lst_frame.snd_ball = knocked_pins
                else:
                    lst_frame.thrd_ball = knocked_pins
                    self.frames.append(self.cur_frame)
            return


        if self.cur_frame.score_ball(knocked_pins):
            self.frames.append(self.cur_frame)
            self.cur_frame = Frame()


    
    def prefix_scores(self):
        return list(accumulate([frame.score for frame in self.frames]))

if __name__ == "__main__":
    testarray = [1,4,4,5,6,4,5,5,10,0,1,7,3,6,4,10,2,8,6]
    testarray2 = [10]*12
    testarray3 = [1,9]*10 + [10]
    scorer = BowlingScore()
    for ball in testarray3:
        scorer.score_ball(ball)
    
    print(scorer.prefix_scores())