class Game:

    def __init__(self, attempts):
        self.max_attempts = attempts
        self.number = None
        self.attempts = None

    def reset_attributes(self, number: int, attempts: int) -> None:
        """The function updates the basic attributes, necessary for the correct work of the game."""

        self.attempts = attempts
        self.number = number

    def check_range(self, conceived_number: int, guessed_num: int) -> str:
        """Game method, that accepts a conceived number and a number entered by a second user as an attempt to guess
        conceived number. The method compares how far the guessed number is from the conceived one and returns a text
        annotation."""

        annotation = None
        if guessed_num > conceived_number + 50:
            annotation = f'Noooo, too much :) Number of attempts left: {self.attempts}'
        elif guessed_num > conceived_number + 10:
            annotation = f"No, it's too much :) Number of attempts left: {self.attempts}"
        elif guessed_num >= conceived_number + 1:
            annotation = f'Almost, but still a lot :) Number of attempts left: {self.attempts}'
        elif guessed_num < conceived_number - 50:
            annotation = f'Noooo, too few :) Number of attempts left: {self.attempts}'
        elif guessed_num < conceived_number - 10:
            annotation = f'No, not enough :) Number of attempts left: {self.attempts}'
        elif guessed_num <= conceived_number - 1:
            annotation = f'Almost, but still not enough :) Number of attempts left: {self.attempts}'
        return annotation

    def guess(self, guessed_num: int) -> tuple[str, int, str, int, int]:
        """The main function of the game, which checks whether the attempt of the second user to guess the conceived
        number is correct. Depending on this, the function returns 'True' or 'False' as the first
        argument. Also function always returns the number of attempts left, an annotation of how close the user is to
        the conceived number, and a number entered as an attempt to guess."""

        self.attempts -= 1

        if guessed_num != self.number and self.attempts > 0:
            annotation = self.check_range(self.number, guessed_num)
            return 'False', self.attempts, annotation, guessed_num, self.max_attempts
        elif guessed_num == self.number and self.attempts >= 0:
            annotation = f'Congratulations, you won in {self.max_attempts - self.attempts} attempts by guessing the ' \
                         f'number {self.number}, conceived by the first player!'
            return 'True', self.attempts, annotation, guessed_num, self.max_attempts
        elif self.attempts <= 0:
            annotation = f'You lost because you used up all your attempts! The number was {self.number}!'
            return 'True', self.attempts, annotation, guessed_num, self.max_attempts
