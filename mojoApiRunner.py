"""
Compiled with python 3.5.2
This file runs various API calls for a cloud deployment
"""

from mwmApi import MwmApi
from mlpApi import MlpApi
import time

if __name__ == '__main__':

    # MLP Server API instance
    mlp_host = "training.mojonetworks.com"

    # KVS Credentials
    kvs_auth_data = {
        "keyId": "KEY-ATN59618-1",
        "keyValue": "42ff84734541cbd98f674b02555330ef",
        "cname": "ATN596",
    }

    with MlpApi(mlp_host) as mlp_api:
        mlp_api.login(kvs_auth_data)
        mwm_service_hostname = mlp_api.get_mwm_service_url()
        
        client = "api-client"       # Simple string parameter to identify your service to MWM
        login_timeout = str(5*60)  # seconds
        
    with MwmApi(mwm_service_hostname) as mwm_api:
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

        # Get Clients
        clientResponse = mwm_api.get_clients()
        print(clientResponse)

        #Get Virtual Access Points
        vapResponse = mwm_api.get_virtual_aps()
        print(vapResponse)

        # Get SSID Profiles
        ssidResponse = mwm_api.get_ssid_profiles()
        print(ssidResponse)
