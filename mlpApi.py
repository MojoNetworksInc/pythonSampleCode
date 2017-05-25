"""
Compiled with python 3.5.2
This file runs API calls on Mojo Launch Pad
"""

# Import requests for making API requests
import requests

# Import for building urls
import urllib.parse as urlparse

# Import for loading json into python dictionary
import json

class MlpApi:

    REQUEST_TIMEOUT = 300  # 5 min

    PATH_BASE = "{hostname}/rest/api/v2"
    PATH_KVS_LOGIN = "kvs/login"
    PATH_KVS_LOGOUT = "kvs/logout"

    PATH_SERVICES = "services"

    HEADER_JSON_CONTENT = {"Content-Type": "application/json"}

    def __init__(self, hostname):
        """

        :param hostname: server hostname (Example: "training.mojonetworks.com")
        :return:
        """
        self.hostname = hostname
        self.cookie_jar = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        self.hostname = None
        self.cookie_jar = None

    def request(self, relative_path='', query_parameters=None, method="GET", body=None, url=None,
                headers=HEADER_JSON_CONTENT):
        """ Common function for making API calls and returning content

        :param relative_path: resource path to be queried ("rest/kvs")
        :param query_parameters: ampersand(&) separated query parameters ("key_id=KEY-101")
        :param method: request method ("GET", "PUT", "POST", "DELETE")
        :param body: request body as string (used for methods like POST, PUT)
        :param url: used to specify custom url (https://training.mojonetworks.com/kvs/login?key_id=KEY-101")
        :param headers: request headers
        :return: response object
        """

        if url is None:
            url = urlparse.urlunparse((
                "https",                                                      # "https"
                self.PATH_BASE.format(hostname=self.hostname),                # "training.mojonetworks.com/new/webservice/V4"
                relative_path,                                                # "login/kvs"
                '',
                '',                                            
                ''
            ))

        # Makes the request
        response = requests.request(
            method,                             # request method ("GET", "PUT", "POST", "DELETE")
            url,                                # constructed url
            params=query_parameters,
            timeout=self.REQUEST_TIMEOUT,       # timeout for request
            cookies=self.cookie_jar,            # session cookies to be passed after login
            data=body,                          # request body
            headers=headers,                    # headers to use ({"Content-Type": "application/json"})
            verify=False
        )

        try:
            # raise exception for error HTTP status (4xx, 5xx)
            response.raise_for_status()
            return response

        except Exception as e:
            # Handle for error HTTP codes
            print(response.status_code)
            print(response.content)

    def login(self, kvs_service_data):
        """ Login to service

        :param kvs_service_data: kvs credentials (cname, keyId, keyValue)
        :return:
        """

        response = self.request(
            self.PATH_KVS_LOGIN,
            method="GET",
            query_parameters={
                "key_id": kvs_service_data["keyId"],
                "key_value": kvs_service_data["keyValue"]
            }
        )

        if response.status_code == requests.codes.ok:
            self.cookie_jar = response.cookies
            print(response.json())
            return response.json()
        else:
            print("Unrecognised status for login" + response.status_code)
            raise

    def logout(self):
        """ Logout from service """

        response = self.request(
            self.PATH_KVS_LOGOUT,
            method="GET"
        )

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Unrecognised status for logout" + response.status_code)
            raise

    def get_mwm_service_url(self):
        """ Fetch service URL for MWM 

        :return: URL
        """
        response = self.request(self.PATH_SERVICES, query_parameters={"type": "amc"})

        if response.status_code == requests.codes.ok:
            response_json = response.json()
            for customer_service in response_json["data"]["customerServices"]:
                return urlparse.urlsplit(customer_service["service"]["service_url"])[1]

        else:
            print("Unrecognised status for fetching services available for customer" + response.status_code)


if __name__ == '__main__':

    # MLP Server API instance
    host = "training.mojonetworks.com"

    # KVS Credentials
    kvs_auth_data = {
        "keyId": "KEY-ATN59618-1",
        "keyValue": "42ff84734541cbd98f674b02555330ef"
        "cname": "ATN596",
    }

    with MlpApi(host) as mlp_api:
        print(mlp_api.login(kvs_auth_data))
        print(mlp_api.get_mwm_service_url())


