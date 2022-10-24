class Game:

    def __init__(self):
        self.list1 = ['да', 'нет']
        self.number = None
        self.attempts = 5

    def reset_attributes(self, number):
        self.attempt = 5
        self.number = number

    def guess(self, guessed_num):
        if guessed_num != self.number:
            return False
        else:
            return True
