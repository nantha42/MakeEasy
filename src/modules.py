import json
import time
from datetime import datetime
from pprint import pprint
from bson.json_util import dumps

import certifi
import pytz
from pymongo import MongoClient

collection_user = "customers"
collection_debits = "debits"
date_format = "%Y:%m:%d %H:%M:%S"
interest = 0.001


class App:

    def __init__(self, credential_file):
        access_obj = self.read_credentials(credential_file)
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
        try:
            self.client = MongoClient(uri, tlsCAFile=certifi.where())
            return self.client[db]
        except:
            print("Difficulty in Logging in, Check Internet Connection")
            exit()

    def get_user(self, customer_id, mode="production"):
        return self.db["customers"].find_one({"customer_id": customer_id, "mode": mode})

    def get_users_count(self, mode="production"):
        records = self.db.customers.count_documents({"mode": mode})
        return records

    def get_debits_count(self, mode="production"):
        return self.db.debits.count_documents({"mode":mode})

    def add_user(self, name, mobile, address: dict, mode="production"):
        id = self.get_users_count(mode) + 1
        result = self.db.customers.insert_one({
            "customer_id": id,
            "name": name,
            "mobile": mobile,
            "address": address,
            "mode": mode,
            "deleted":False
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

    def add_debit(self, customer_id, amount: int, reason="", mode="production",interest_enabled=True):
        if not self.exists_customer(customer_id, mode):
            print("No user exists, cannot add debit")
            return None

        debit_id = self.db.debits.find({"customer_id": customer_id,"mode":mode}).count() + 1
        result = self.db.debits.insert_one({"customer_id": customer_id,
                                            "debit_id": debit_id,
                                            "time": datetime.utcnow(),
                                            "principal": amount,
                                            "reason": reason,
                                            "pays": [],
                                            "mode": mode,
                                            "deleted":False,
                                            "interest_enabled":interest_enabled
                                            })
        return debit_id

    def add_debit_past(self, customer_id, time_str: str, amount, reason="", mode="production",interest_enabled=True):
        if not self.exists_customer(customer_id, mode):
            print("No user exists, cannot add debit past")
            return "Error"

        debit_id = self.db.debits.count_documents({"customer_id": customer_id, "mode": mode}) + 1
        time_str += " 05:30"
        time_obj = datetime.utcfromtimestamp(time.mktime(time.strptime(time_str, "%Y:%m:%d %H:%M")))
        result = self.db.debits.insert_one({"customer_id": customer_id,
                                            "debit_id": debit_id,
                                            "time": time_obj,
                                            "principal": amount,
                                            "reason": reason,
                                            "pays": [],
                                            "mode": mode,
                                            "interest_enabled":interest_enabled
                                            })
        return debit_id

    def add_past_pay(self, customer_id, debit_id, amount, time_str, mode="production"):
        if not self.exists_debit(customer_id, debit_id, mode):
            print("No such debit_id or customer_id exists, cannot add past pay")
            return "Error"

        debit = self.db.debits.find_one({"customer_id": customer_id, "debit_id": debit_id, "mode": mode})
        time_str += " 05:30"
        time_obj = datetime.utcfromtimestamp(time.mktime(time.strptime(time_str, "%Y:%m:%d %H:%M")))
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
        if not debit["interest_enabled"]:
            print("This is Interestless Debit")
            return


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

    def calculate_interest(self, amount, startdate, enddate):
        tz = pytz.timezone("Asia/Kolkata")
        d1 = datetime.date(startdate)
        d2 = datetime.date(enddate)
        diff = (d2 - d1).days
        I = diff * self.interest * amount
        return I

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
        return self.db.debits.update_many({"mode": mode},{"$set":{"deleted":True}})

    def delete_all_customers(self, mode="test"):
        return self.db.customers.update_many({"mode": mode},{"$set":{"deleted":True}})

    def hard_delete_all_debits(self,mode="test"):
        return self.db.debits.delete_many({"mode": mode})

    def hard_delete_all_customers(self, mode="test"):
        return self.db.customers.delete_many({"mode": mode})

    def read_credentials(self, filename=".password.json"):
        with open(filename, "r") as f:
            obj = json.load(f)
            user = obj["user"]
            password = obj["password"]
            project_name = obj["project_name"]
            db_name = obj["db_name"]
            object = self.get_access_object(user, password, project_name, db_name)
            return object

    def get_customer_debit_summary(self, customerid, mode="production"):
        if not self.exists_customer(customer_id=customerid, mode=mode):
            print(f"No such customer_id exists, cannot get for userid {customerid} debits")
            return "Error"
        debits = self.db.debits.find({"customer_id": customerid, "mode": mode})
        return_obj = []
        for debit in debits:
            time_bought = debit["time"]
            I=0
            if len(debit["pays"]) == 0:
                principal_balance = debit["principal"]
                if debit["interest_enabled"]:
                    I = self.calculate_interest(principal_balance, debit["time"], datetime.utcnow())
            else:
                principal_balance = debit["pays"][-1]["principal"]
                last_pay_obj = debit["pays"][-1]["time"]
                if debit["interest_enabled"]:
                    I = self.calculate_interest(principal_balance, last_pay_obj, datetime.utcnow())
            return_obj.append({"time": time_bought, "principal": principal_balance, "interest": I})

            # print(f"Customer: {customerid:2}   Principal Balance : {principal_balance:5} Interest : {I:5} Time Bought : {time_bought} ")
        # print(return_obj)
        return return_obj

    # def get_due_customers(self,mode="production"):
    #     customers = self.db.customers.find({"mode":mode})
    #     today = datetime.date(datetime.utcnow())
    #     for customer in customers:
    #         debits = self.db.debits.find({"customer_id":customer["customer_id"],"mode":mode})
    #         for debit in debits:
    #             pays = debit["pays"]
    #             if len(pays) > 0:
    #                 last_pay = pays[-1]
    #                 last_date = datetime.date(last_pay[-1])
    #                 if last_date.month != 2:
    #                     if last_date.day ==1:

    def export_data(self,mode="production"):
        customers_cursor = self.db.customers.find({"mode":mode})
        debits_cursor = self.db.debits.find({"mode":mode})

        with open('customers.json','w') as file:
            json.dump(json.loads(dumps(customers_cursor)),file)

        with open('debits.json','w') as file:
            json.dump(json.loads(dumps(debits_cursor)),file)

    def import_data(self,add_mode=""):
        with open("customers.json",'r') as file:
            customers = json.load(file)
            for c in customers:
                c["_id"] = c["_id"]["$oid"]
                if add_mode != "":
                    c["mode"] = add_mode
            self.db.customers.insert_many(customers)
            print(f"Inserted {len(customers)} customers records")

        with open("debits.json","r") as file:
            debits = json.load(file)
            for c in debits:
                c["_id"] = c["_id"]["$oid"]
                if add_mode != "":
                    c["mode"] = add_mode
            self.db.debits.insert_many(debits)
            print(f"Inserted {len(debits)} debit records")
        pass

    def update_columns(self):
        """
        Used to update documents when new keys has to be added to particular
        collections
        """
        documents = self.db.customers.find({"deleted":{"$exists":False}})
        self.db.customers.update_many(documents,{"$set":{"deleted":False}})
