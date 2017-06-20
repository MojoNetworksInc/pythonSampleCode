"""
Compiled with python 3.5.2
This file runs API calls on an MWM service
"""

# Import requests for making API requests
import requests

# Import for building urls
import urllib.parse as urlparse

# Import for loading json into python dictionary
import json

# Handling datetime and timestamps
from datetime import datetime, timedelta
from calendar import timegm

REQUEST_TIMEOUT = 300  # 5 min

HTTPS = "https"
PATH_BASE = "{hostname}/new/"
PATH_API_WEBSERVICE = "webservice/V4"
PATH_LOGIN = "/login/key/{client_identifier}/{session_timeout}"
PATH_LOGOUT = "/logout"
PATH_LOCATION_TREE = "locations/tree"
PATH_MANAGED_DEVICES = "devices/manageddevices"
PATH_CLIENTS = "devices/clients"
PATH_ASSOCIATION_ANALYTICS = "analytics/associationdata/{start_time}/{end_time}"    # Path parameters
PATH_SSID_PROFILES = "templates/SSID_PROFILE"

QUERY_FILTER = "filter=%s"
QUERY_LOCATION_ID = "locationid=%s"
QUERY_NODE_ID = "nodeid=%s"
QUERY_FILE_FORMAT = 'format="%s"'
QUERY_MAC_OBFUSCATE = 'tohashmac="%s"'

HEADER_JSON_CONTENT = {"Content-Type": "application/json"}

"""
#GET
#POST
PUT
DELETE


#Login using KVS
#Fetch Location Tree
#Fetch Managed Devices
Fetch Clients
Example API calls which cover the following,
    #Using filters - encoding the URL should be considerd
    #Using Query params
    #Arguments via Path params
    #Arguments via Body
    #Explaining Headers
    #File download
    #Error handling

"""


class MwmApi:

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

    def request(self, relative_path='', query_parameters='', method="GET", body=None, url=None,
                headers=HEADER_JSON_CONTENT):
        """ Common function for making API calls and returning content

        :param relative_path: resource path to be queried ("devices/clients")
        :param query_parameters: ampersand(&) separated query parameters ("locationid=1&nodeid=1")
        :param method: request method ("GET", "PUT", "POST", "DELETE")
        :param body: request body as string (used for methods like POST, PUT)
        :param url: used to specify custom url (https://www.mojo.com/new/webservice/V4/devices/clients?locationid=1")
        :param headers: request headers
        :return: response object
        """
        if url is None:
            url = urlparse.urlunparse((
                HTTPS,                                                                  # "https"
                PATH_BASE.format(hostname=self.hostname) + PATH_API_WEBSERVICE,         # "training.mojonetworks.com/new/webservice/V4"
                relative_path,                                                          # "devices/clients"
                '',
                query_parameters,                                                       # "locationid=1&nodeid=1"
                ''
            ))

        # Makes the request
        response = requests.request(
            method,                             # request method ("GET", "PUT", "POST", "DELETE")
            url,                                # constructed url
            timeout=REQUEST_TIMEOUT,            # timeout for request
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
            response_dict = response.json()
            print("HTTP Error " + str(response_dict["status"]))
            for error in response_dict["errors"]:
                print(error["errorCode"] + " => " + error["message"])
                print("DEBUG: " + error["moreInfo"])


    def login(self, client_identifier, session_timeout, kvs_service_data):
        """ Login to service

        :param client_identifier: string to identify caller
        :param session_timeout: session timeout in seconds
        :param kvs_service_data: kvs credentials (cname, keyId, keyValue)
        :return:
        """

        # POST request body
        auth_data = {
            "type": "apikeycredentials",
            "keyId": kvs_service_data["keyId"],
            "keyValue": kvs_service_data["keyValue"],
            "exposedCustomerId": kvs_service_data["cname"]
        }

        response = self.request(
            PATH_LOGIN.format(client_identifier=client_identifier, session_timeout=session_timeout),
            method="POST",
            body=json.dumps(auth_data)
        )
        if response.status_code == requests.codes.ok:
            self.cookie_jar = response.cookies
            return response.json()
        else:
            print("Unrecognised status for login" + str(response.status_code))
            raise

    def logout(self):
        """ Logout from service """

        response = self.request(
            PATH_LOGOUT,
            method="POST"
        )

        if response.status_code == requests.codes.ok:
            return
        else:
            print("Unrecognised status for logout" + response.status_code)
            raise

    def get_ssid_profiles(self):
        """
        Fetch all SSID profiles
        
        """
        response = self.request(PATH_SSID_PROFILES)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Unrecognised status for location tree fetch" + response.status_code)
		
    def get_location_tree(self):
        """ Fetch location tree

        :return: response object
        """
        response = self.request(PATH_LOCATION_TREE)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Unrecognised status for location tree fetch" + response.status_code)

    def get_managed_devices(self):
        """ Fetch managed device with specified filter

        :return: response object
        """

        # Device with (boxid = 1) OR (troubleshootingstatus = 0)
        filter_value = {
            "value": [
                {
                    "property": "boxid",
                    "value": [1],
                    "operator": "="
                },
                {
                    "property": "troubleshootingstatus",
                    "value": [0],
                    "operator": "="
                }
            ],
            "operator": "OR"
        }
        query = QUERY_FILTER % json.dumps(filter_value)

        response = self.request(PATH_MANAGED_DEVICES, query)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Unrecognised status for managed device fetch" + response.status_code)

    def download_association_analytics_file(
            self, filename, start_time, end_time, file_format='JSON', obfuscate_mac=True):
        """ Requests for generation of association analytics file and then download it.

        :param filename: name of file to write downloaded content to
        :param start_time: start time of analytics data
        :param end_time: end time of analytics data
        :param file_format: file format (JSON, CSV)
        :param obfuscate_mac: whether to obfuscate mac ids or not
        :return:
        """

        # construct query param string
        query = QUERY_FILE_FORMAT % file_format + '&' + QUERY_MAC_OBFUSCATE % "true" if obfuscate_mac else "false"

        # Set path params to relative path string formatter
        association_analytics_uri = PATH_ASSOCIATION_ANALYTICS.format(start_time=start_time, end_time=end_time)
        #print(association_analytics_uri)
        # will get uri for generated file download
        response = self.request(association_analytics_uri, query)
        
        if response.status_code != requests.codes.ok:
            print("Unrecognised status for association analytics file generation request" + response.status_code)
            return
        decodedContent = response.content.decode("utf-8")
        print(decodedContent)
        # construct url for file download using received uri
        url = urlparse.urlunparse((
            HTTPS,
            PATH_BASE.format(hostname=self.hostname),
            decodedContent,
            '',
            '',
            ''
        ))
        print(url)
        r = requests.get(url, stream=True, cookies=self.cookie_jar, timeout=REQUEST_TIMEOUT, verify=False)

        if response.status_code == requests.codes.ok:
            # save file
            with open(filename+"."+file_format.lower(), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            print("Unrecognised status while retrieving file" + response.status_code)


    def get_clients(self):
        """ Fetch managed device with specified filter

        :return: response object
        """

        # Device with (boxid = 1) OR (troubleshootingstatus = 0)
        filter_value = {
            "value": [
                {
                    "property": "boxid",
                    "value": [1],
                    "operator": "="
                },
                {
                    "property": "troubleshootingstatus",
                    "value": [0],
                    "operator": "="
                }
            ],
            "operator": "OR"
        }
        query = QUERY_FILTER % json.dumps(filter_value)

        response = self.request(PATH_CLIENTS, query)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Unrecognised status for managed device fetch" + response.status_code)

if __name__ == '__main__':

    # MWM Server API instance
    host = "training.mojonetworks.com"
    mwm_api = MwmApi(host)

    # Login to MWM using KVS
    client = "api-client"
    login_timeout = "3000"
    kvs_auth_data = {
        "keyId": "KEY-ATN59618-1",
        "keyValue": "42ff84734541cbd98f674b02555330ef",
        "cname": "ATN596",
    }
    print(mwm_api.login(client, login_timeout, kvs_auth_data))
    
    #Get clients
    print(mwm_api.get_clients())
    
    # Get all SSID profiles
    print(mwm_api.get_ssid_profiles())
    
    # Get managed devices
    print(mwm_api.get_managed_devices())

    # Fetch Location tree
    print(mwm_api.get_location_tree())

    # Logout from the service
    mwm_api.logout()
