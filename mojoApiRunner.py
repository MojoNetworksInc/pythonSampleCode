"""
Compiled with python 3.5.2
This file runs various API calls for a cloud deployment
"""

from mgmApi import MgmApi
from mwmApi import MwmApi
from mlpApi import MlpApi
import time

if __name__ == '__main__':

    # MLP Server API instance
    mlp_host = "dashboard.mojonetworks.com"

    # KVS Credentials
    kvs_auth_data = {
        "keyId": "KEY-ATN563674-437",
        "keyValue": "2eeff76c6b9ac4c8942b60fd431b44dd",
        "cname": "ATN563674"
    }

    with MlpApi(mlp_host) as mlp_api:
        # Mojo Launchpad Login
        mlp_api.login(kvs_auth_data)
        mgm_service_hostname = mlp_api.get_mgm_service_url()
        mwm_service_hostname = mlp_api.get_mwm_service_url()
        
        # used by Mojo Wireless Manager(MWM)
        client = "api-client"       # Simple string parameter to identify your service to MWM
        login_timeout = str(5*60)  # seconds
        
    with MwmApi(mwm_service_hostname) as mwm_api:
        # Mojo Wireless Manager
        print("MWM: start")
        loginResponse = mwm_api.login(client, login_timeout, kvs_auth_data)
        print(loginResponse)

        # Get managed devices
        managedDeviceResponse = mwm_api.get_managed_devices()
        print(managedDeviceResponse)

        # Fetch Location tree
        locationTreeResponse = mwm_api.get_location_tree()
        print(locationTreeResponse)

        # Download Association Analytics File
        start = time.time()-(24*60*60*1000)
        analytics_start_time = int(round(start))
        analytics_end_time = int(round(time.time()))
        mwm_api.download_association_analytics_file("assocAnalytics_%s" % analytics_end_time, analytics_start_time, analytics_end_time, 'JSON', True)

        # Download Visibility Analytics File
        start = time.time()-(24*60*60*1000)
        analytics_start_time = int(round(start))
        analytics_end_time = int(round(time.time()))
        mwm_api.download_visibility_analytics_file("visibAnalytics_%s" % analytics_end_time, analytics_start_time, analytics_end_time, 'CSV', True)

        # Get Clients
        clientResponse = mwm_api.get_clients()
        print(clientResponse)

        #Get Virtual Access Points
        vapResponse = mwm_api.get_virtual_aps()
        print(vapResponse)

        # Get SSID Profiles
        ssidResponse = mwm_api.get_ssid_profiles()
        print(ssidResponse)
        print("MWM: end")


        
    with MgmApi(mgm_service_hostname) as mgm_api:
        # Mojo Guest Manager
        print("MGM: start")
        # Get API Version
        version_data = mgm_api.getAPIVersion()
        print ("MGM API Version: " + version_data['data']['version']['api_version'])
        mgm_api.api_version = version_data['data']['version']['api_version']

        # MGM Login
        loginResponse = mgm_api.login(kvs_auth_data)

        # API 1: Presence: Get the Footfall by duration
        # Parameters to fetch data for 30 days prior to custom_end_date
        footfall_data = {
            "duration": 30,          # units: days; Allowed values are 7, 14, 30, 60, 90, 180, 365
            "ssid": "null",          # if null then all applicable SSIDs will be considered, else specific SSID name.
            "node_type": "root",     # Type of the node in the location tree; Allowed values are root, server, location.
            "server_id": "null",     # Specify the server id of the MWM server that this MGM syncs with; Should be null when node_type = root.
            "location_id": "1",      # the location id in the location tree.
            "custom_end_date": "2017-11-26"     # format: yyyy-mm-dd; data will be fetched for "duration" days before the given custom-end-date.
        }
        footfall = mgm_api.getFootfallByDuration(footfall_data)

        # Result 1: Printing unique vistors for the day:
        print ("Unique Visitors per day:")
        for day in footfall["data"]["graphData"]["categories"]:
            # for python 2.x: printing on same line
            # print(day[0] + ","),
            # for python 3.x: printing on same line
            print(day[0] + ",", end=" ")
        # a newline after printing the dates above.
        print ("")
        for n in footfall["data"]["graphData"]["total"]:
            # # for python 2.x: printing on same line
            # print(str(n) + ","),
            # for python 3.x: printing on same line
            print(str(n) + ",", end=" ")
        print ("")

        # API 2: Conversion: Brand Loyalty
        brand_loyalty_data = {
            "duration": 30,          # units: days; Allowed values are 7, 14, 30, 60, 90, 180, 365
            "ssid": "null",          # if null then all applicable SSIDs will be considered, else specific SSID name.
            "node_type": "root",     # Type of the node in the location tree; Allowed values are root, server, location.
            "server_id": "null",     # Specify the server id of the MWM server that this MGM syncs with; Should be null when node_type = root.
            "location_id": "1"       # the location id in the location tree.
        }
        brand_loyalty = mgm_api.getBrandLoyalty(brand_loyalty_data)
        print ("MGM Brand Loyalty Response: ")
        print (brand_loyalty)

        # API 3: WiFi Usage: Data Transfer by Duration
        wifi_usage_data = {
            "duration": 30,          # units: days; Allowed values are 7, 14, 30, 60, 90, 180, 365
            "ssid": "null",          # if null then all applicable SSIDs will be considered, else specific SSID name.
            "node_type": "root",     # Type of the node in the location tree; Allowed values are root, server, location.
            "server_id": "null",     # Specify the server id of the MWM server that this MGM syncs with; Should be null when node_type = root.
            "location_id": "1"       # the location id in the location tree.
        }
        wifi_usage = mgm_api.getWiFiDataTransfer(wifi_usage_data)
        print ("MGM WiFi Usage Response: ")
        print (wifi_usage)
        print("MGM: end")


