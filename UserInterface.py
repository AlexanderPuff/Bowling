import os
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from ScoreCounter import *

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.rule import Rule
from rich.markdown import Markdown

def _clear_terminal():
    """Reset and clear the current terminal."""
    os.system('cls' if os.name == 'nt' else 'printf "\033[2J\033[3J\033[H"')

bindings = KeyBindings()
@bindings.add('enter')
def _(event):
    event.current_buffer.validate_and_handle()

def _get_input(prompt_text: str = "Enter your scores: ", default: str = ""):
    """Get user input, a custom prompt and prefill can be provided.
    """
    user_input = prompt(prompt_text, key_bindings=bindings, default=default).lower()
    return user_input

class bowling_screen:

    def __init__(self):
        self.console = Console()
        self.history = []
        self.reset()
        self.to_screen()

    
    def reset(self):
        '''
        Reset the game (but keep the history around, allows for undo).
        '''
        self.done = False
        self.throws = []
        self.cur_game = BowlingScore()
        self.message = None


    def to_screen(self):
        '''
        Prints all relevant info after resetting the terminal.
        '''
        _clear_terminal()

        self.console.print(Rule("Bowling Scorer 3000"))

        table = self.create_score_table()
        self.console.print(Columns(table), justify="center")

        self.console.print(Rule())

        md = "Enter U to undo, R to reset, Q to quit."
        self.console.print(Panel(Markdown(md,justify="center")))

        self.console.print(Rule())

        if self.message:
            self.console.print(self.message, justify="center")
            self.message = None

    def stringify(self, symbols, score):
        '''
        Insert newlines between all our symbols and numbers.
        '''
        # there might be ints in here
        str_symbols = [str(s) for s in symbols]
        str_score = str(score)
        str_score += " " * (3-len(str_score)) # insert padding for better alignment

        lines = str_symbols + [str_score]

        return "\n".join(lines)
    

    def create_score_table(self):
        '''
        Put all game info in one table.
        '''
        frame_symbols = [frame.to_symbols() for frame in self.cur_game.frames[:NR_THROWS-1]]
        # finale needs special care
        if len(self.cur_game.frames) == NR_THROWS:
            frame_symbols.append(self.cur_game.frames[-1].to_symbols(is_last=True))

        # append partially completed frame
        if self.cur_game.cur_frame.throws:
            frame_symbols.append(self.cur_game.cur_frame.to_symbols())
        
        scores = self.cur_game.prefix_scores()

        # fill up so there are always 10 frames, taking special care of the longer last one
        frame_symbols += [["-", "-", ""]] * (NR_THROWS - 1 - len(frame_symbols))
        if len(frame_symbols) < NR_THROWS:
            frame_symbols.append(["-", "-", "-"])

        scores += ["---"]*(NR_THROWS-len(scores))

        cols = []
        cur_frame_number = len(self.cur_game.frames)
        if cur_frame_number == NR_THROWS and not self.cur_game.done:
            cur_frame_number -= 1
        
        for i in range(NR_THROWS):
            # color the current frame's border red
            if i == cur_frame_number: color = "red"
            else: color = "white"
            
            cols.append(Panel(self.stringify(frame_symbols[i], scores[i]), border_style=color))
        
        return cols



    def main_loop(self):
        '''
        Keep reading user input until the game is completed.
        '''
        while not self.done:
            user_input = _get_input()
            # quit
            if user_input == "q":
                self.done = True
            # undo
            elif user_input == "u":
                if self.history:
                    self.throws = self.history.pop()
                    self.cur_game = BowlingScore(self.throws)
            # reset
            elif user_input == "r":
                self.history.append(self.throws.copy())
                self.reset()
            # (hopefully) number entered
            else: self.int_input(user_input)
            self.to_screen()


    
    def int_input(self, input):
        '''
        Read user input, convert it into an integer, and update the game. Display an error message if input was invalid.
        '''
        try:
            pins_knocked = int(input)
            try:
                self.cur_game.score_ball(pins_knocked)
                self.history.append(self.throws.copy())
                self.throws.append(pins_knocked)
                if self.cur_game.done:
                    self.message = f"Congratulations! You scored {self.cur_game.prefix_scores()[-1]} points."
            except ValueError as e:
                    self.message = "Error: " + str(e)
        except ValueError:
            self.message = f"Error: Please enter a number between 0 and {NR_PINS}."