import json

from src.modules import *



def test_add_pays():
    app = App(".password.json")
    app.db.debits.delete_many({})
    app.delete_all_debits(mode="test")
    app.delete_all_users(mode="test")
    userid = app.add_user("Rajinikanth", "123434567", {"door": "12", "street": "boyes garden"}, mode="test")
    debitid = app.add_debit_past(userid, "2021:4:1", 1000, mode="test")
    app.add_past_pay(customer_id=userid, debit_id=debitid, amount=200, time_str="2021:6:1", mode="test")
    app.add_past_pay(customer_id=userid, debit_id=debitid, amount=200, time_str="2021:7:1", mode="test")
    app.add_past_pay(customer_id=userid, debit_id=debitid, amount=500, time_str="2021:10:8", mode="test")
    principal = str(app.get_debit_principal(userid, debitid, mode="test"))[:7]
    assert principal == "254.826"


def test_create_debit_for_non_exist_customer():
    app = App(".password.json")
    app.delete_all_debits(mode="test")
    assert app.add_debit_past(5, "2021:4:1", 1000, mode="test") == "Error"


def test_get_customers_debits():
    app = App(".password.json")
    userid = app.add_user("Rajinikanth", "123434567", {"door": "12", "street": "boyes garden"}, mode="test")
    app.add_debit_past(userid, "2021:4:1", 1000, mode="test")
    app.delete_all_debits(mode="test")
    app.add_debit_past(userid, "2021:4:1", 1000, mode="test")
    app.add_past_pay(customer_id=userid, debit_id=1, amount=200, time_str="2021:6:1", mode="test")
    app.add_debit_past(userid, "2021:5:1", 5000, mode="test")
    app.add_past_pay(customer_id=userid, debit_id=2, amount=400, time_str="2021:6:1", mode="test")
    obj = app.get_customers_debits(userid, mode="test")
    for ob in obj:
        pprint(ob)


if __name__ == '__main__':
    test_get_customers_debits()
