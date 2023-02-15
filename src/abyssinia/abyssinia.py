import collections
import hashlib
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json
import environ
from urllib.parse import urlencode


class Abyssinia:
    # Initialise environment variables
   

    def __init__(self, access_key, profile_id,transaction_uuid,signed_field_names,unsigned_field_names,
                 signed_date_time,locale,transaction_type,reference_number,amount,currency,
                 #api="https://testsecureacceptance.cybersource.com/pay"
                 api="https://testsecureacceptance.cybersource.com/billing"
                 ):

        self.api = api
        self.access_key = access_key
        self.profile_id = profile_id

        pay_load = {
            "access_key": access_key,
            "profile_id": profile_id,
            "transaction_uuid": transaction_uuid,
            "reference_number": reference_number,
            "signed_field_names": signed_field_names,
            "unsigned_field_names": unsigned_field_names,
            "signed_date_time": signed_date_time,
            "locale": locale,
            "transaction_type": transaction_type,
            "amount": amount,
            "currency": currency,
            
        }
        env = environ.Env()
        environ.Env.read_env(DEBUG=(bool, False))
        self.sign = self.__sign(
            pay_load=pay_load, app_key=env("Aby_Secret_Key"))

        self.final_body = {
            "access_key": access_key,
            "profile_id": profile_id,
            "transaction_uuid": transaction_uuid,
            "reference_number": reference_number,
            "signed_field_names": signed_field_names,
            "unsigned_field_names": unsigned_field_names,
            "signed_date_time": signed_date_time,
            "locale": locale,
            "transaction_type": transaction_type,
            "amount": amount,
            "currency": currency,
            "signature": self.sign

        }
    

    @staticmethod
    def __sign(pay_load, app_key):
            ussd_for_string_a = pay_load.copy()
            ussd_for_string_a["access_key"] = app_key

            ordered_items = collections.OrderedDict(
                sorted(ussd_for_string_a.items()))

            string_a = ''
            for key, value in ordered_items.items():
                if string_a == '':
                    string_a = key + '=' + value
                else:
                    string_a += '&' + key + '=' + value
            string_b = hashlib.sha256(str.encode(string_a)).hexdigest()
            print(string_b)
            return str(string_b).upper()
            
    def result(self):
        return self.final_body


    
    def request_params(self):
        return {"pay_load":urlencode(self.final_body)}
       

    def send_request(self):
        try:

            retry_strategy = Retry(
                total=5,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],

            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            response = http.post(url=self.api, json=self.request_params())
            response.raise_for_status()  # raises exception when not a 2xx response
            if (
                response.status_code != 204 and
                response.headers["content-type"].strip().startswith("application/json")
            ):
                return json.loads(response.text)


            # if response.status_code != 204:
            #     return response.json()
            # #return json.loads(response.text)
        except BaseException as e:
            return str(e)
