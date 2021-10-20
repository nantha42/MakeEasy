from src.modules import *


class CMode:
    def __init__(self):
        password = ".password.json"
        self.options = ["create user","create debit","delete user","delete debit","quit"]
        # self.app = App(password)
        self.quit = False

    def print_options(self):
        opt_indexes = {}
        for i,opt in enumerate(self.options):
            print(f"{i}: {opt}")
            opt_indexes[i] = opt
        return opt_indexes

    def run(self):
        while not self.quit:
            opt_indexes = self.print_options()
            try:
                inp = int(input())
                choosen_opt = opt_indexes[inp]
                if choosen_opt == "quit":
                    self.quit = True

            except KeyError:
                print("Not a valid option,")
                pass

if __name__ == '__main__':
    cm = CMode()
    cm.run()
