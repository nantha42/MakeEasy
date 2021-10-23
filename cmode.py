from src.modules import *
import os
from colorama import Fore, Back, Style

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')
class CMode:
    def __init__(self, mode):
        password = ".password.json"
        self.options = ["create customer", "show customers", "show debits", "create pay", "create debit","create debit interestless",
                        "delete customer", "delete debit", "quit"]
        self.app = App(password)
        self.quit = False
        self.mode = mode

    def print_options(self):
        opt_indexes = {}
        clear_screen()
        for i, opt in enumerate(self.options):
            print(f"{i}: {opt}")
            opt_indexes[i] = opt
        return opt_indexes

    def act(self, opt):
        clear_screen()
        if opt == "create customer":
            name = input("Customer Name: ")
            mobile = input("Customer mobile: ")
            doorno = input("Customer doorno: ")
            street = input("Customer street: ")
            self.app.add_user(name,
                              mobile,
                              {"doorno": doorno,
                               "street": street},
                              self.mode)
        if opt == "create debit":
            id = int(input("Enter Customer id: "))
            enter_date = input("yyy:mm:dd Date: ")
            amount = int(input("Enter amount"))
            reason = input("Debit reason")
            print(f"Debit id: {self.app.add_debit_past(id, enter_date, amount, reason, self.mode)}")
            pass

        elif opt == "show customers":
            count = self.app.get_users_count()
            for id in range(1, count + 1):
                cus = self.app.get_user(id, self.mode)
                print(f"{id:<3} : {(Fore.GREEN + cus['name']):20s} {Fore.BLACK}")
            print()

        elif opt == "show debits":
            print("enter customer id or -1 for all debits")
            id = int(input("customer id: "))
            if id != -1:
                obj = self.app.get_customer_debit_summary(id, self.mode)
                for rec in obj:
                    print(f"{Fore.GREEN}Date{Fore.BLACK}: {str(rec['time']):10} {Fore.GREEN}Principal{Fore.BLACK} :  {rec['principal']:5} {Fore.GREEN}Interest{Fore.BLACK}: {rec['interest']:5}")
            else:
                count = self.app.get_users_count(self.mode)
                for id in range(1, count + 1):
                    obj = self.app.get_customer_debit_summary(id, self.mode)
                    for rec in obj:
                        print(rec["time"])
                        print(f"{Fore.GREEN}Date{Fore.BLACK}: {str(rec['time'])} {Fore.GREEN}Principal{Fore.BLACK} :  {rec['principal']:5} {Fore.GREEN}Interest{Fore.BLACK}: {rec['interest']:5}")

        elif opt == "delete customer":
            id = int(input("Enter customer id: "))
            print(self.app.db.customers.delete({"customer_id": id, "mode": self.mode}))

        elif opt == "delete debit":
            id = int(input("Enter customer id: "))
            d_id = int(input("Enter debit id: "))
            print(self.app.db.debits.delete({"customer_id": id, "debit_id": d_id, "mode": self.mode}))

        elif opt == "create debit interestless":
            id = int(input("Enter customer id:"))
            enter_date = input("yyy:mm:dd Date: ")
            amount = int(input("Enter amount"))
            reason = input("Debit reason")
            print(f"Debit id: {self.app.add_debit_past(id, enter_date, amount, reason, self.mode, False)}")
        input(Fore.GREEN + "Press Enter")
        clear_screen()
        print(Fore.BLACK)


    def run(self):
        while not self.quit:
            opt_indexes = self.print_options()
            try:
                inp = int(input("Enter option: "))
                choosen_opt = opt_indexes[inp]
                if choosen_opt == "quit":
                    self.quit = True
                self.act(choosen_opt)

            except KeyError:
                print("Not a valid option,")
                pass


if __name__ == '__main__':
    mode = "test"
    cm = CMode(mode)
    cm.run()
