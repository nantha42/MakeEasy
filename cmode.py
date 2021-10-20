from src.modules import *
from pprint import pprint


class CMode:
    def __init__(self,mode):
        password = ".password.json"
        self.options = ["create customer","show customers","create debit","delete user","delete debit","quit"]
        self.app = App(password)
        self.quit = False
        self.mode =mode

    def print_options(self):
        opt_indexes = {}
        for i,opt in enumerate(self.options):
            print(f"{i}: {opt}")
            opt_indexes[i] = opt
        return opt_indexes

    def act(self,opt):
        if opt == "create customer":
            name = input("Customer Name: ")
            mobile = input("Customer mobile: ")
            doorno = input("Customer doorno: ")
            street = input("Customer street: ")
            self.app.add_user(name,
                              mobile,
                              {"doorno":doorno,
                               "street":street},
                              self.mode)
        if opt == "create debit":

            pass

        if opt == "show customers":
            count = self.app.get_users_count()
            for id in range(1,count+1):
                cus = self.app.get_user(id,self.mode)
                print(f"{id:<3} : {cus['name']:20s}")
            print()






    def run(self):
        while not self.quit:
            opt_indexes = self.print_options()
            try:
                inp = int(input())
                choosen_opt = opt_indexes[inp]
                if choosen_opt == "quit":
                    self.quit = True
                self.act(choosen_opt)

            except KeyError:
                print("Not a valid option,")
                pass

if __name__ == '__main__':
    mode = "production"
    cm = CMode(mode)
    cm.run()
