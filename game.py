class Game:

    def __init__(self, max_number: int):
        self.list1 = ['да', 'нет']
        self.number = None
        self.attempts = None
        self.max_number = max_number

    def reset_attributes(self, number: int) -> None:
        self.attempts = 5
        self.number = number

    def check_range(self, number: int, guessed_num: int) -> str:
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

        self.attempts -= 1

        if guessed_num != self.number and self.attempts > 0:
            annotation = self.check_range(self.number, guessed_num)
            return 'False', self.attempts, annotation, guessed_num
        elif self.attempts <= 0:
            annotation = 'You lost because you used up all your attempts!'
            return 'True', self.attempts, annotation, guessed_num
        else:
            annotation = f'Congratulations, you won in {5 - self.attempts} attempts by guessing the number ' \
                         f'{self.number}, conceived by the first player'
            return 'True', self.attempts, annotation, guessed_num
