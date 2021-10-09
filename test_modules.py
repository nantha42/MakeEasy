import json
from src.modules import *

with open(".password.json", "r") as f:
    obj = json.load(f)
    user = obj["user"]
    password = obj["password"]
    project_name = obj["project_name"]
    db_name = obj["db_name"]


def test_add_pays():
    app = App(user, password, project_name, db_name)
    app.db.debits.delete_many({})
    app.add_debit_past(2, "2021:4:1", 1000)
    app.add_past_pay(customer_id=2, debit_id=1, amount=200, time_str="2021:6:1")
    app.add_past_pay(customer_id=2, debit_id=1, amount=200, time_str="2021:7:1")
    app.add_past_pay(customer_id=2, debit_id=1, amount=500, time_str="2021:10:8")
    principal = str(app.get_debit_principal(2, 1))[:7]
    assert principal == "254.826"


def test_create_debit_for_non_exist_customer():
    app = App(user, password, project_name, db_name)
    app.db.debits.delete_many({})
    assert app.add_debit_past(5, "2021:4:1", 1000) == "Error"

def test_get_customers_debits():
    app = App(user, password, project_name, db_name)
    app.db.debits.delete_many({})
    app.add_debit_past(2, "2021:4:1", 1000)
    app.add_past_pay(customer_id=2, debit_id=1, amount=200, time_str="2021:6:1")
    app.add_debit_past(2, "2021:5:1", 5000)
    app.add_past_pay(customer_id=2, debit_id=2, amount=400, time_str="2021:6:1")
    obj = app.get_customers_debits(2)
    for ob in obj:
        pprint(ob)



if __name__ == '__main__':
    test_get_customers_debits()
