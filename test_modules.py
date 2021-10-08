from src.modules import *


def test_add_pays():
    app = App(user, password, project_name, db_name)
    app.db.debits.delete_many({})
    app.add_debit_past(2, "2021:4:1", 1000)
    app.add_past_pay(customer_id=2,debit_id=1,amount=200,time_str="2021:6:1")
    app.add_past_pay(customer_id=2,debit_id=1,amount=200,time_str="2021:7:1")
    app.add_pay(customer_id=2, debit_id=1, amount=500)
    principal = app.get_debit_principal(2,1 )

if __name__ == '__main__':
    test_add_pays()
