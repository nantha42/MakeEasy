import time
from datetime import datetime
from pprint import pprint

import certifi
from pymongo import MongoClient

collection_user = "customers"
collection_debits = "debits"
date_format = "%Y:%m:%d %H:%M:%S"
interest = 0.001


class App:

    def __init__(self, u, p, proj, db_name):
        access_obj = self.get_access_object(u, p, proj, db_name)
        self.client = None
        self.db = self.get_database(access_obj)
        self.interest = interest

    def get_access_object(self, user, password, project_name, db_name):
        object = {"user": user,
                  "password": password,
                  "project_name": project_name,
                  "db_name": db_name}
        return object

    def parse_access_object(self, obj):
        u, p, proj, db = obj["user"], obj["password"], obj["project_name"], obj["db_name"]
        return u, p, proj, db

    def get_database(self, access_object):
        u, p, proj, db = self.parse_access_object(access_object)
        uri = f"mongodb+srv://{u}:{p}@turiyam.9qfeb.mongodb.net/{proj}?retryWrites=true&w=majority"
        self.client = MongoClient(uri, tlsCAFile=certifi.where())
        return self.client[db]

    def get_user(self, customer_id):
        return self.db["customers"].find({"customer_id": customer_id})

    def get_users_count(self, mode="production"):
        records = self.db.customers.find({"mode": mode}).count()
        return records

    def add_user(self, name, mobile, address: dict, mode="production"):
        id = self.get_users_count(mode) + 1
        result = self.db.customers.insert_one({
            "customer_id": id,
            "name": name,
            "mobile": mobile,
            "address": address,
            "mode": mode
        })
        print("Inserted id:", result.inserted_id)
        return id

    def exists_customer(self, customer_id, mode="production"):
        res = self.db.customers.count_documents({"customer_id": customer_id, "mode": mode})
        if res == 1:
            return True
        else:
            return False

    def exists_debit(self, customer_id, debit_id, mode="production"):
        if self.exists_customer(customer_id, mode):
            res = self.db.debits.count_documents({"debit_id": debit_id, "customer_id": customer_id, "mode": mode})
            if res == 1:
                return True
            else:
                return False
        else:
            print("No customer in that id")
            return False

    def add_debit(self, customer_id, amount: int, reason="", mode="production"):
        if not self.exists_customer(customer_id, mode):
            print("No user exists, cannot add debit")
            return None

        debit_id = self.db.debits.find({"customer_id": customer_id}).count() + 1
        result = self.db.debits.insert_one({"customer_id": customer_id,
                                            "debit_id": debit_id,
                                            "time": datetime.utcnow(),
                                            "principal": amount,
                                            "reason": reason,
                                            "pays": [],
                                            "mode": mode
                                            })
        return debit_id

    def add_debit_past(self, customer_id, time_str: str, amount, reason="", mode="production"):
        if not self.exists_customer(customer_id, mode):
            print("No user exists, cannot add debit past")
            return "Error"

        debit_id = self.db.debits.find({"customer_id": customer_id, "mode": mode}).count() + 1
        time_obj = datetime.utcfromtimestamp(time.mktime(time.strptime(time_str, "%Y:%m:%d")))
        result = self.db.debits.insert_one({"customer_id": customer_id,
                                            "debit_id": debit_id,
                                            "time": time_obj,
                                            "principal": amount,
                                            "reason": reason,
                                            "pays": [],
                                            "mode": mode
                                            })
        return debit_id

    def add_past_pay(self, customer_id, debit_id, amount, time_str, mode="production"):
        if not self.exists_debit(customer_id, debit_id, mode):
            print("No such debit_id or customer_id exists, cannot add past pay")
            return "Error"

        debit = self.db.debits.find_one({"customer_id": customer_id, "debit_id": debit_id, "mode": mode})
        time_obj = datetime.utcfromtimestamp(time.mktime(time.strptime(time_str, "%Y:%m:%d")))
        pays = debit["pays"]

        if len(pays) > 0:
            pays.sort(key=lambda x: x["time"])
            last_pay = pays[-1]
            principal = last_pay["principal"]
            interest_balance = last_pay["interest_balance"]
            pay_date = datetime.date(last_pay["time"])
            current_date = datetime.date(time_obj)
            diff = (current_date - pay_date).days
            pay_obj = self.pay(amount, diff, principal, time_obj, interest_balance)
            pays.append(pay_obj)
            self.db.debits.update_one({"customer_id": customer_id,
                                       "debit_id": debit_id},
                                      {
                                          "$set": {"pays": pays}
                                      })

        else:
            principal = debit["principal"]
            debit_date = datetime.date(debit["time"])
            current_date = datetime.date(time_obj)
            diff = (current_date - debit_date).days
            print("Days: ", diff)
            pay_obj = self.pay(amount, diff, principal, time_obj)
            pays.append(pay_obj)
            self.db.debits.update_one({"customer_id": customer_id,
                                       "debit_id": debit_id},
                                      {
                                          "$set": {"pays": pays}

                                      })

    def add_pay(self, customer_id, debit_id, amount, mode="production"):
        if not self.exists_debit(customer_id, debit_id, mode):
            print("No such debit_id or customer_id exists, cannot add pay")
            return "Error"

        debit = self.db.debits.find_one({"customer_id": customer_id, "debit_id": debit_id, "mode": mode})
        pays = debit["pays"]

        if len(pays) > 0:
            last_pay = pays[-1]
            principal = last_pay["principal"]
            interest_balance = last_pay["interest_balance"]
            pay_date = datetime.date(last_pay["time"])
            time_obj = datetime.utcnow()
            current_date = datetime.date(time_obj)
            diff = (current_date - pay_date).days
            pay_obj = self.pay(amount, diff, principal, time_obj, interest_balance)
            pays.append(pay_obj)
            self.db.debits.update_one({"customer_id": customer_id,
                                       "debit_id": debit_id},
                                      {
                                          "$set": {"pays": pays}

                                      })
        else:
            principal = debit["principal"]
            debit_date = datetime.date(debit["time"])
            time_obj = datetime.utcnow()
            current_date = datetime.date(time_obj)
            diff = (current_date - debit_date).days
            pay_obj = self.pay(amount, diff, principal, time_obj)

            pays.append(pay_obj)
            pays.sort(key=lambda x: x["time"])

            self.db.debits.update_one({"customer_id": customer_id,
                                       "debit_id": debit_id},
                                      {
                                          "$set": {"pays": pays}

                                      })

    def pay(self, amount, diff, principal, time_obj, interest_balance=0):
        total_interest = diff * self.interest * principal + interest_balance
        print("Interest_Amoung: %s" % (total_interest))
        if total_interest <= amount:
            interest_paying = total_interest
            interest_balance = 0
        else:
            interest_paying = amount
            interest_balance = total_interest - amount
        remaining = amount - interest_paying
        print("Remaining amount: %s" % (remaining))
        principal_remaining = principal - remaining
        pay_obj = {
            "principal": principal_remaining,
            "interest_paying": interest_paying,
            "interest_balance": interest_balance,
            "time": time_obj
        }
        pprint(pay_obj)
        return pay_obj

    def get_debit_principal(self, customer_id, debit_id, mode="production"):
        if not self.exists_debit(customer_id, debit_id, mode=mode):
            print("No such debit_id or customer_id exists")
            return "Error"

        debit = self.db.debits.find_one({"customer_id": customer_id, "debit_id": debit_id, "mode": mode})
        pay = debit["pays"][-1]
        return pay["principal"]

    def get_customers_debits(self, customer_id, mode="production"):
        if not self.exists_customer(customer_id=customer_id, mode=mode):
            print("No such customer_id exists")
            return "Error"
        return self.db.debits.find({"customer_id": customer_id, "mode": mode})

    def delete_all_debits(self, mode="test"):
        return self.db.debits.delete_many({"mode": mode})

    def delete_all_users(self, mode="test"):
        return self.db.customers.delete_many({"mode": mode})
