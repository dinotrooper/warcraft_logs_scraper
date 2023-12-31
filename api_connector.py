# https://github.com/sircinnamon/WCLBot
# Connector for the WCL API v2
import requests
from datetime import datetime, timedelta

class ApiConnector(object):
	def __init__(self, clientid, clientsecret, logging):
		# Init fields
		self.client_id=clientid
		self.client_secret=clientsecret
		self.baseURL = "https://classic.warcraftlogs.com:443/api/v2/client"

		self.oauth_auth_uri="https://www.warcraftlogs.com/oauth/authorize"
		self.oauth_token_uri="https://www.warcraftlogs.com/oauth/token"
		self.oauth_session=None
		self.current_oauth_token=None
		self.current_oauth_token_expiry=None
		self.logging = logging
		# Create session

		self.create_oauth_session()
		self.logging.info("API Connector initialized.")

	def create_oauth_session(self):
		data = {"grant_type":"client_credentials"}
		response = requests.post(self.oauth_token_uri, data=data, auth=(self.client_id, self.client_secret))
		# print(response.status_code)
		resp = response.json()
		# print(resp)
		# print(response.headers)
		self.current_oauth_token = resp["access_token"]
		self.current_oauth_token_expiry	= (datetime.now() + timedelta(seconds=resp["expires_in"]))

	def renew_token_if_needed(self):
		# Renew the token if it's near expiration
		if(self.current_oauth_token	== None): self.create_oauth_session()
		elif(self.current_oauth_token_expiry== None): self.create_oauth_session()
		elif((self.current_oauth_token_expiry - datetime.now()).total_seconds() < 86400):
			# Less than 1 day left, renew
			self.create_oauth_session()
		else: return

	def generic_request(self, query) -> dict:
		self.renew_token_if_needed()
		url = self.baseURL
		headers = {
			"authorization":"Bearer {}".format(self.current_oauth_token),
			"accept":"application/json"
		}
		response = requests.get(url, json={'query': query}, headers=headers)
		# print(response.url + " " + str(response.status_code))
		response.raise_for_status()
		return response.json()