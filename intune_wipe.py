import requests
import json
import boto3

# Intune API endpoint for device wipe
intune_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"

# AWS Secrets Manager details
secret_name = "intune_credentials"
region_name = "us-east-1"

# Device ID and device name for the PC to be wiped
device_id = "YOUR_DEVICE_ID"
device_name = "YOUR_DEVICE_NAME"

# Retrieve the Intune username and password from Secrets Manager
secrets_client = boto3.client("secretsmanager", region_name=region_name)
secret_response = secrets_client.get_secret_value(SecretId=secret_name)
secret_data = json.loads(secret_response["SecretString"])
intune_username = secret_data["username"]
intune_password = secret_data["password"]

# Construct the authentication token
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
wipe_action_id = device_details['wipeActionId']

# Create the request body to initiate the device wipe
wipe_request_body = {
    'actionReason': 'Wipe requested by user',
    'actionType': 'wipe',
    'deviceActionResult': {
        '@odata.type': '#microsoft.graph.deviceActionResult',
        'actionName': 'wipe',
        'actionState': 'pending'
    }
}

# Initiate the device wipe
wipe_action_url = f"{intune_url}/{device_id}/deviceManagement/executeAction"
response = requests.post(wipe_action_url, headers=headers, json=wipe_request_body)

# Check the response status and display the result
if response.status_code == 202:
    print("Device wipe initiated successfully.")
else:
    print("Failed to initiate device wipe.")
    print("Response:", response.text)
