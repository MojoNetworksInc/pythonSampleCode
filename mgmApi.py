"""
This file runs API calls on an MGM service
"""

# Import requests for making API requests
import requests
# NOTE: Use a valid certificate.
# this sample will disable warning "InsecureRequestWarning: Unverified HTTPS request is being made"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Import for building urls
#  -- for python 3+
import urllib.parse as urlparse 

#  -- for python 2.7
#import urlparse


# Import for loading json into python dictionary
import json

REQUEST_TIMEOUT = 300  # 5 minutes

HTTPS = "https"
PATH_BASE = "{hostname}/api/"
PATH_LOGIN = "/site/keyLogin"
PATH_LOGOUT = "/site/logout"
PATH_API_VERSION = "/site/version"
PATH_FOOTFALL_BY_DURATION = "/analytics/graphs/visitor/days"
PATH_BRAND_LOYALTY = "/analytics/graphs/brandloyalty/location"
PATH_DATA_TRANSFER_DAYS = "/analytics/graphs/datatransfer/days"

QUERYPARAMS_LOGIN = "key_id={keyId}&key_value={keyValue}"
QUERYPARAMS_FOOTFALL = "duration={duration}&ssid={ssid}&node_type={node_type}&server_id={server_id}&location_id={location_id}"
QUERYPARAMS_BRAND_LOYALTY = "duration={duration}&ssid={ssid}&node_type={node_type}&server_id={server_id}&location_id={location_id}"
QUERYPARAMS_DATA_TRANSFER = "duration={duration}&ssid={ssid}&node_type={node_type}&server_id={server_id}&location_id={location_id}"

QUERYPARAMS_APPEND_CUSTOM_DATE = "&custom_end_date={custom_end_date}"

HEADER_JSON_CONTENT = {"Content-Type": "application/json"}

"""

# Login using KVS
#
# Example APIs:
#   Get MGM api version
#   Get Footfall by Duration/Days
#   Get Brand Loyalty
#   Get Data Transfer by Duration/Days
#
# Logout

"""

class MgmApi:

    def __init__(self, hostname):
        """
        :param hostname: server hostname (Example: "training.mojonetworks.com")
        :return:
        """
        self.hostname = hostname
        self.cookie_jar = None
        self.api_version = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        self.hostname = None
        self.cookie_jar = None
        self.api_version = ""

    def request(self, relative_path='', query_parameters='', method="GET", body=None, url=None, headers=HEADER_JSON_CONTENT):
        """ Common function for making API calls and returning content

        :param relative_path: resource path to be queried ("analytics/graphs/visitor/days")
        :param query_parameters: ampersand(&) separated query parameters ("server_id=null&location_id=1")
        :param method: request method ("GET", "PUT", "POST", "DELETE")
        :param body: request body as string (used for methods like POST, PUT)
        :param url: used to specify custom url (https://www.mojo.com/new/webservice/V4/devices/clients?locationid=1")
        :param headers: request headers
        :return: response object
        """
        if url is None:
            url = urlparse.urlunparse((
                HTTPS,                                                                  # "https"
                PATH_BASE.format(hostname=self.hostname) + self.api_version,            # "training.mojonetworks.com/api/v1.14"
                relative_path,                                                          # "analytics/graphs/visitor/days"
                '',
                query_parameters,                                                       # "server_id=null&location_id=1"
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
            print('Exception : mgm request [%s].', e)


    def login(self, kvs_service_data):
        """ Login to MGM service
        :param kvs_service_data: kvs credentials (keyId, keyValue)
        :return:
        """
        try:
            response = self.request(
                relative_path=PATH_LOGIN,
                method = "GET",
                query_parameters = QUERYPARAMS_LOGIN.format(keyId = kvs_service_data["keyId"], keyValue = kvs_service_data["keyValue"])
            )
            if response.status_code == requests.codes.ok:
                self.cookie_jar = response.cookies
                print("MGM login")
                print(response.json())
                return response.json()
            else:
                response_dict = response.json()                
                print("mgm login error; response (%s)" % response_dict)
                raise
        except Exception as e:
            print('Exception : mgm login [%s].', e)            


    def logout(self):
        """ Logout from service """

        try:
            response = self.request(
                relative_path=PATH_LOGOUT,
                method="GET"
            )

            if response.status_code == requests.codes.ok:
                print("MGM logout")
                print(response.json())
                return
            else:
                response_dict = response.json()                
                print("mgm logout error; response (%s)" % response_dict)
                raise
        except Exception as e:
            print('Exception : mgm logout [%s].', e)


    def getAPIVersion(self):
        """
        Get MGM API version
        Access Privilieges: Everyone
        """
        try:
            response = self.request(
                #url = urlparse.urlunparse(HTTPS, self.hostname, PATH_API_VERSION),
                relative_path=PATH_API_VERSION,
                method = "GET")

            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                response_dict = response.json()                
                print("mgm getAPIVersion Error " + str(response_dict["status"]))
                for error in response_dict["data"]:
                    print(error["errorCode"] + " => " + error["message"])
                raise
        except Exception as e:
            print('Exception : mgm getAPIVersion [%s].', e)


    # Presence Charts - Footfall by Duration
    def getFootfallByDuration(self, query_data):
        """
        Fetch analytics data of visitors by days.
        Access Privilieges: Users with Administrator role or Analyst role 
        """
        try:
            query_parameters = QUERYPARAMS_FOOTFALL.format(
                duration = query_data["duration"], 
                ssid = query_data["ssid"],
                node_type = query_data["node_type"],
                server_id = query_data["server_id"],
                location_id = query_data["location_id"])
            
            if "custom_end_date" in query_data:
                query_parameters += QUERYPARAMS_APPEND_CUSTOM_DATE.format(custom_end_date = query_data["custom_end_date"])
                
            response = self.request(
                relative_path=PATH_FOOTFALL_BY_DURATION,
                method = "GET",
                query_parameters = query_parameters)

            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                response_dict = response.json()                
                print("mgm getFootfallByDuration Error " + str(response_dict["status"]))
                for error in response_dict["data"]:
                    print(error["errorCode"] + " => " + error["message"])
                raise
        except Exception as e:
            print('Exception : mgm getFootfallByDuration [%s].', e)


    # Conversion Charts - Brand Loyalty
    def getBrandLoyalty(self, query_data):
        """
        Fetch the brand loyalty data based on their frequency of visits.
        Access Privileges: Users with Administrator role or Analyst role
        """
        try:
            query_parameters = QUERYPARAMS_BRAND_LOYALTY.format(
                duration = query_data["duration"], 
                ssid = query_data["ssid"],
                node_type = query_data["node_type"],
                server_id = query_data["server_id"],
                location_id = query_data["location_id"])
            
            if "custom_end_date" in query_data:
                query_parameters += QUERYPARAMS_APPEND_CUSTOM_DATE.format(custom_end_date = query_data["custom_end_date"])

            response = self.request(
                relative_path=PATH_BRAND_LOYALTY,
                method = "GET",
                query_parameters = query_parameters)

            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                response_dict = response.json()                
                print("mgm getBrandLoyalty Error " + str(response_dict["status"]))
                for error in response_dict["data"]:
                    print(error["errorCode"] + " => " + error["message"])
                raise
        except Exception as e:
            print('Exception : mgm getBrandLoyalty [%s].', e)



    # WiFi Usage Charts - Data Transfer by Duration
    def getWiFiDataTransfer(self, query_data):
        """
        Fetch  the total upload and total download of data in bytes between client and the server by days for the specified duration.
        Access Privileges: Users with Administrator role or Analyst role
        """
        try:
            query_parameters = QUERYPARAMS_DATA_TRANSFER.format(
                duration = query_data["duration"], 
                ssid = query_data["ssid"],
                node_type = query_data["node_type"],
                server_id = query_data["server_id"],
                location_id = query_data["location_id"])
            
            if "custom_end_date" in query_data:
                query_parameters += QUERYPARAMS_APPEND_CUSTOM_DATE.format(custom_end_date = query_data["custom_end_date"])

            response = self.request(
                relative_path=PATH_DATA_TRANSFER_DAYS,
                method = "GET",
                query_parameters = query_parameters)

            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                response_dict = response.json()                
                print("mgm getWiFiDataTransfer Error " + str(response_dict["status"]))
                for error in response_dict["data"]:
                    print(error["errorCode"] + " => " + error["message"])
                raise
        except Exception as e:
            print('Exception : mgm getWiFiDataTransfer [%s].', e)



            
if __name__ == '__main__':
    # MGM Server API hostname
    host = "training.mojonetworks.com"
    mgm_api = MgmApi(host)

    # Login to MGM using KVS
    kvs_auth_data = {
        "keyId": "KEY-ATN59618-1",
        "keyValue": "42ff84734541cbd98f674b02555330ef",
    }
    print(mgm_api.login(kvs_auth_data))
    
    # Fetch the Footfall by Duration data
    footfall_data = {
        "duration": 30,          # units: days; Allowed values are 7, 14, 30, 60, 90, 180, 365
        "ssid": "null",          # if null then all applicable SSIDs will be considered, else specific SSID name.
        "node_type": "root",     # Type of the node in the location tree; Allowed values are root, server, location.
        "server_id": "null",     # Specify the server id of the MWM server that this MGM syncs with; Should be null when node_type = root.
        "location_id": "1"       # the location id in the location tree.
    }

    # API 1: Presence: Get the Footfall by duration
    print(mgm_api.getFootfallByDuration(footfall_data))

    # Logout from the service
    mgm_api.logout()
