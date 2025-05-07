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


def clear_console():
    """Reset and clear the current console."""
    # These are special characters used by different operating systems
    os.system("cls" if os.name == "nt" else 'printf "\033[2J\033[3J\033[H"')


bindings = KeyBindings()


@bindings.add("enter")
def _(event):
    event.current_buffer.validate_and_handle()


def get_input(prompt_text: str = "Enter your scores: ", default: str = "") -> str:
    """Get user input, a custom prompt and prefill can be provided."""
    user_input = prompt(prompt_text, key_bindings=bindings, default=default).lower()
    return user_input


class bowling_screen:

    def __init__(self):
        self.console = Console()
        self.history = []
        self.reset()
        self.to_screen()

    def reset(self):
        """
        Reset the game (but keep the history around, allows for undo).
        """
        self.done = False
        self.throws = []
        self.cur_game = BowlingScore()
        self.message = None


    def to_screen(self):
        """
        Prints all relevant info after resetting the terminal.
        """
        clear_console()

        # after clearing the screen just go through each element top to bottom
        self.console.print(Rule("Bowling Scorer 3000"))

        table = self.create_score_table()
        self.console.print(Columns(table), justify="center")

        self.console.print(Rule())

        md = "Enter u to undo, r to reset, q to quit."
        self.console.print(Panel(Markdown(md, justify="center")))

        self.console.print(Rule())

        if self.message:
            self.console.print(self.message, justify="center")
            self.message = None
            

    def stringify(self, symbols, score) -> str:
        """
        Insert newlines between all our symbols and numbers.
        """
        # there might be ints in here
        str_symbols = [str(s) for s in symbols]
        str_score = extend_to(str(score), 3, " ")

        lines = str_symbols + [str_score]
        return "\n".join(lines)
    

    def create_score_table(self):
        """
        Put all game info in one table.
        """

        frame_symbols = [
            frame.to_symbols(is_last=i == 9)
            for (i, frame) in enumerate(self.cur_game.frames)
        ]

        # also needed for coloring the current frame's border red
        cur_frame_number = len(self.cur_game.frames)
        if cur_frame_number == NR_THROWS and not self.cur_game.done:
            cur_frame_number -= 1

        # append partially completed frame
        if self.cur_game.cur_frame.throws:
            frame_symbols.append(
                self.cur_game.cur_frame.to_symbols(is_last=cur_frame_number == 9)
            )

        scores = extend_to(self.cur_game.prefix_scores(), NR_THROWS, ["---"])

        # fill up so there are always 10 frames, taking special care of the longer last one
        frame_symbols = extend_to(frame_symbols, NR_THROWS - 1, [["-", "-", ""]])
        if len(frame_symbols) < NR_THROWS:
            frame_symbols.append(["-", "-", "-"])

        cols = []
        for i in range(NR_THROWS):
            if i == cur_frame_number:
                color = "red"
            else:
                color = "white"

            cols.append(
                Panel(self.stringify(frame_symbols[i], scores[i]), border_style=color)
            )

        return cols


    def main_loop(self):
        """
        Keep reading user input until the game is completed.
        """
        while not self.done:
            usr_input = get_input()
            match usr_input:
                case "q":  # quit
                    self.done = True
                case "u":  # undo
                    if self.history:
                        self.throws = self.history.pop()
                        self.cur_game = BowlingScore(self.throws)
                case "r":  # restart
                    self.history.append(self.throws.copy())
                    self.reset()
                case (
                    _
                ):  # something else entered, for example the score of a single ball
                    try:
                        pins_knocked = int(usr_input)
                        try:
                            self.cur_game.score_ball(pins_knocked)
                            self.history.append(
                                self.throws.copy()
                            )  # keep track of all states for undoing
                            self.throws.append(pins_knocked)
                            if self.cur_game.done:
                                self.message = f"Congratulations! You scored {self.cur_game.prefix_scores()[-1]} points."
                        except ValueError as e:
                            self.message = "Error: " + str(e)
                    except ValueError:
                        self.message = (
                            f"Error: Please enter a number between 0 and {NR_PINS}."
                        )

            self.to_screen()
