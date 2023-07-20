import requests
import json
import os

# Intune API endpoint for device wipe
intune_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"

# Intune username and password fetched from GitHub Actions secrets
intune_username = os.environ.get('INTUNE_USERNAME_SECRET')
intune_password = os.environ.get('INTUNE_PASSWORD_SECRET')

# Device ID for the PC to be wiped
device_id = "ILDMC-BW4SQF3"

# Authenticate and get the access token for Intune
token_url = "https://login.microsoftonline.com/common/oauth2/token"
data = {
    'grant_type': 'password',
    'client_id': '1950a258-227b-4e31-a9cf-717495945fc2',
    'resource': 'https://graph.microsoft.com',
    'username': intune_username,
    'password': intune_password
}
response = requests.post(token_url, data=data)
access_token = json.loads(response.text)['access_token']

# Prepare the request headers with the authentication token
headers = {
    'Authorization': 'Bearer ' + access_token,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Find the device by ID and retrieve its wipe action ID
device_search_url = f"{intune_url}/{device_id}"
response = requests.get(device_search_url, headers=headers)
device_details = json.loads(response.text)
wipe_action_id = device_details['id']

# Create the request body to initiate the device wipe
wipe_request_body = {
    'keepUserData': False,
    'keepEnrollmentData': False,
    'deleteAlerts': False,
    'deviceNotContactedSince': None,
    'deviceState': 'wipePending'
}

# Initiate the device wipe
wipe_action_url = f"{intune_url}/{device_id}/wipe"
response = requests.post(wipe_action_url, headers=headers, json=wipe_request_body)

# Check the response status and display the result
if response.status_code == 202:
    print("Device wipe initiated successfully.")
else:
    print("Failed to initiate device wipe.")
    print("Response:", response.text)
