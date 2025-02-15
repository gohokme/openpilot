import jwt
import os
import requests
from datetime import datetime, timedelta
from common.basedir import PERSIST
from selfdrive.version import get_version
from common.params import Params

if Params().get("OPKRServer", encoding="utf8") == "0":
  API_HOST = os.getenv('API_HOST', 'http://opkr.o-r.kr:3000')
elif Params().get("OPKRServer", encoding="utf8") == "1":
  API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')
elif Params().get("OPKRServer", encoding="utf8") == "2":
  API_HOST = os.getenv('API_HOST', 'http://' + Params().get("OPKRServerAPI", encoding="utf8"))
else:
  API_HOST = os.getenv('API_HOST', 'http://opkr.tk:3000')

class Api():
  def __init__(self, dongle_id):
    self.dongle_id = dongle_id
    with open(PERSIST+'/comma/id_rsa') as f:
      self.private_key = f.read()

  def get(self, *args, **kwargs):
    return self.request('GET', *args, **kwargs)

  def post(self, *args, **kwargs):
    return self.request('POST', *args, **kwargs)

  def request(self, method, endpoint, timeout=None, access_token=None, **params):
    return api_get(endpoint, method=method, timeout=timeout, access_token=access_token, **params)

  def get_token(self):
    now = datetime.utcnow()
    payload = {
      'identity': self.dongle_id,
      'nbf': now,
      'iat': now,
      'exp': now + timedelta(hours=1)
    }
    token = jwt.encode(payload, self.private_key, algorithm='RS256')
    if isinstance(token, bytes):
      token = token.decode('utf8')
    return token


def api_get(endpoint, method='GET', timeout=None, access_token=None, **params):
  headers = {}
  if access_token is not None:
    headers['Authorization'] = "JWT " + access_token

  headers['User-Agent'] = "openpilot-" + get_version()

  return requests.request(method, API_HOST + "/" + endpoint, timeout=timeout, headers=headers, params=params)
