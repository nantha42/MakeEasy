from src.modules import *
from pprint import pprint


class CMode:
    def __init__(self,mode):
        password = ".password.json"
        self.options = ["create customer","show customers","show debits","create pay","create debit","delete customer","delete debit","quit"]
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
            id = int(input("Enter Customer id: "))
            enter_date = input("yyy:mm:dd Date: ")
            amount = int(input("Enter amount"))
            reason = input("Debit reason")
            print(f"Debit id: {self.app.add_debit_past(id,enter_date,amount,reason,self.mode)}")
            pass

        if opt == "show customers":
            count = self.app.get_users_count()
            for id in range(1,count+1):
                cus = self.app.get_user(id,self.mode)
                print(f"{id:<3} : {cus['name']:20s}")
            print()

        if opt == "show debits":
            print("enter customer id or -1 for all debits")
            id = int(input("customer id: "))
            if id != -1:
                self.app.get_customer_debit_summary(id,self.mode)
            else:
                count = self.app.get_users_count(self.mode)
                for id in range(1,count+1):
                    self.app.get_customer_debit_summary(id,self.mode)
                pass


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
