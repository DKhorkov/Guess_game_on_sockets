class Game:

    def __init__(self):
        self.number = None
        self.attempts = None

    def reset_attributes(self, number: int) -> None:
        """The function updates the basic attributes necessary for the functioning of the game."""

        self.attempts = 5
        self.number = number

    def check_range(self, number: int, guessed_num: int) -> str:
        """Game method that accepts a guessed number and a number entered by a second user as an attempt to guess
        hidden number. The method compares how far the number is from the guessed one and returns a text annotation."""

        annotation = None
        if guessed_num > number + 50:
            annotation = f'Noooo, too much :) Number of attempts left: {self.attempts}'
        elif guessed_num > number + 10:
            annotation = f"No, it's too much :) Number of attempts left: {self.attempts}"
        elif guessed_num >= number + 1:
            annotation = f'Almost, but still a lot :) Number of attempts left: {self.attempts}'
        elif guessed_num < number - 50:
            annotation = f'Nooo, too few :) Number of attempts left: {self.attempts}'
        elif guessed_num < number - 10:
            annotation = f'No, not enough :) Number of attempts left: {self.attempts}'
        elif guessed_num <= number - 1:
            annotation = f'Almost, but still not enough :) Number of attempts left: {self.attempts}'
        return annotation

    def guess(self, guessed_num: int) -> tuple[str, int, str, int]:
        """The main function of the game, which checks whether the attempt of the second user to guess the number
        guessed is correct the first user. Depending on this, the function returns 'True' or 'False' as the first
        argument, as well as always returns the number of attempts left, an annotation of how close the user is to the
        desired number, and a number entered as an attempt to guess."""

        self.attempts -= 1

        if guessed_num != self.number and self.attempts > 0:
            annotation = self.check_range(self.number, guessed_num)
            return 'False', self.attempts, annotation, guessed_num
        elif self.attempts <= 0:
            annotation = f'You lost because you used up all your attempts! The number was {self.number}!'
            return 'True', self.attempts, annotation, guessed_num
        else:
            annotation = f'Congratulations, you won in {5 - self.attempts} attempts by guessing the number ' \
                         f'{self.number}, conceived by the first player!'
            return 'True', self.attempts, annotation, guessed_num
