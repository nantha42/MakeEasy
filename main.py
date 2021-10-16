from src.modules import *
from flask import Flask



app = Flask(__name__,)
app.debug=True

fin = App(".password.json")

@app.route("/")
def home():
    users_count = fin.get_users_count(mode="production")
    print(users_count)
    res = f"<html><body>"
    res += f"<h1>Ganapathi Finance Portal</h1>"
    for i in range(1,users_count+1):
        debits = fin.get_user_debits(i,mode="production")
        print(debits)
        user = fin.get_user(i,mode="production")
        res += f"Customer: {user['name']} <br>".format()
        for debit in debits:
            res += "<li>Principal:{} Interest:{} </li>".format(debit["principal"],debit["interest"])
    res += f"</body></html>"
    return res


if __name__ == '__main__':
    # app = App(".password.json")
    # customerid = app.add_user("Kannima Husband","1234567890",{})
    fin = App(".password.json")
    customerid = 1
    debitid = fin.add_debit_past(customer_id=customerid, time_str="2021:10:10", amount=10000, reason="no interest",mode="production")
    fin.get_customer_debit_summary(1, mode="production")
    fin.import_data()
    #app.run()
    pass
