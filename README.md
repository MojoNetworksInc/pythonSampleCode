# About the Project
This project provides sample codes that leverage the Mojo REST APIs to demonstrate the following:
* A key-based login to:
- Mojo Launchpad (MLP)
- Mojo Wireless Manager (MWM)
- Mojo Guest Manager (MGM)
* Fetch list of services from Mojo Launchpad.
* For Mojo Wireless Manager service:
- Fetch, create, & modify SSID Profiles and Device Templates
* For Mojo Guest Manager service:
- Get Analytics data

# Purpose
This project has been primarily created for API end users to get a quick understanding of Mojo REST APIs for some of the most common use cases with Mojo products.

# Contents of the Project
This repository contains python based sample codes which can be imported and used for learning about the Mojo APIs

# Project Dependencies
* Python - 3.5.2

# How to use the Project
Anyone can clone/fork this repo to extend and execute the Python files and try out various Mojo API calls.

# Code Structure
* Use the `mojoApiRunner.py` to execute the sample code. Change the following fields in this file:
  - In main modify the value of the variable 'mlp_host' to the hostname of the MLP service. Also modify the KVS authentication information
* `mwmApi.py` contains the functions to access data from MWM service. To access the MWM service directly, modify the follign fields in this file:
  - In main modify the value of the variable 'host' to the hostname of the MWM srvice. Also modify the KVS authentication information
  - If you want to change the API version being used, modify the PATH_API_WEBSERVICE constant.
* `mlpApi.py` contains the functions to access data from MLP service. This file contains functions to log into MLP service, fetch the user's allowed MWM service and logout. To run this file:
  - In main modify the value of the 'host' variable to the hostname of the MLP service. Also modify the KVS authentication information.


# Reference Documentation
* [Mojo REST APIs - Getting Started Guide](https://support.mojonetworks.com/support/solutions/articles/9000124630-getting-started-with-mojo-rest-apis)
* [Mojo REST APIs - Reference Guide](http://prod.mojonetworks.com/WebAPI/source/)
