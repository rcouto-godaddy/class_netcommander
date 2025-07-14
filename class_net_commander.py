# Python existing libraries
import requests
import json
import yaml
import sys


class class_net_commander:
  
  @property
  def fqdn(self):
    return self._fqdn


  def __init__(self, yaml_fname: str):

    self._fqdn = ""
    self._oauth_url = "https://sso.godaddy.com/v1/api/token" 
    self._netcomm_url = "https://ncm.int.godaddy.com/api/v1.0/netcommander/run/"
    
    # Return content of yaml file;
    # in this case this contains the service accounts
    with open(yaml_fname, 'r') as f:
      self._svc_acct = yaml.safe_load(f)
      

  def _get_sso_token(self):
    username = self._svc_acct["svc_acct"]["uname"]
    password = self._svc_acct["svc_acct"]["passwd"]
    realm = self._svc_acct["svc_acct"]["realm"]
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        "username": username,
        "password": password,
        "realm": realm
    })  

    response = requests.post(self._oauth_url, headers=headers, data=payload)
    sso_token = response.json()['data']

    return sso_token
    

  # The names of the functions will be a direct reflection of the API methods here:
  # https://ncm.int.godaddy.com/api/v1.0/docs/netcommander/
  # This function takes a list of commands and sends them to the device
  # A NEW TOKEN WILL ALWAYS BE GENERATED TO AVOID THE CASE OF THE TOKEN EXPIRING
  
  def run(self, dev_fqdn: str, commds: list):
    payload = [
        {
            "device": f"{dev_fqdn}",
            "config_mode": "false",
            "commands": commds
        }
    ]

    # Returns a List with each item a reslt for each command
    sso_token = self._get_sso_token() 
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'sso-jwt {sso_token}' 
    }

    try:
      response = requests.request("POST", self._netcomm_url, headers=headers, data=json.dumps(payload), timeout=15)
    except requests.exceptions.RequestException as err:
      print("An error occurred while attempting connection to the device")
      print(f"Details: {err}")
      sys.exit(1)

    self._fqdn = response.json()[0]['device'].strip()
    self._api_output = response.json()[0]['result']
        
    return self._api_output
  