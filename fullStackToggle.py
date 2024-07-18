# Script to bulk toggle hosts to full-stack monitoring
# Selection based on mgmt zone (must be configured prior)
# charles.rinaldi@dynatrace.com

import requests
import json

# Be sure to change these to match your env
# Token requires readEntinties and writeConfig
DYNATRACE_BASE_URL = "https://YOUR-DT-ENV.com/api"
DYNATRACE_API_TOKEN = "INSERT API TOKEN"
HEADERS = {
    "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}",
    "Content-Type": "application/json",
}

# Specify Mgmt zone to pull hosts from

mgmtZoneName = input("Management zone containing hosts to be toggled to full stack (case sensitive): ")

# GET request to retrieve relevant host entities
# ** THIS REQUEST CURRENTLY HAS A TIMEFRAME OF 1 YEAR - delete "&from=now-1y" from end of URL to remove this constraint

response = requests.get(
    f"{DYNATRACE_BASE_URL}/v2/entities?entitySelector=type%28%22HOST%22%29%2CmzName%28%22{mgmtZoneName}%22%29&from=now-1y",
    headers=HEADERS,
)

############################################

# Extract the host ID's from the previous request

zone_data = json.loads(response.text)
zone_entity_id = zone_data['entities']

# For loop iterates through each of the returned Host ID's and submits a PUT request with the new monitoring settings
# This only occurs after the payload for a host has been validated

for data_item in zone_data['entities']:
    tempHostId = (data_item['entityId'])
    validator = requests.post(f"{DYNATRACE_BASE_URL}/config/v1/hosts/{tempHostId}/monitoring/validator",
    headers=HEADERS,
    data='{"monitoringEnabled":"true","monitoringMode":"FULL_STACK"}'
)
    if validator.status_code == 204:
        print(f"\nSuccessfully validated payload for {tempHostId}, submitting PUT request...")
        response2 = requests.put(f"{DYNATRACE_BASE_URL}/config/v1/hosts/{tempHostId}/monitoring",
        headers=HEADERS,
        data='{"monitoringEnabled":"true","monitoringMode":"FULL_STACK"}'
    )
        if response2.status_code == 204:
            print(f"Done! Successfully enabled monitoring and toggled to full stack mode for {tempHostId}")
        else:
            print(f"Error enabling full stack mode for {tempHostId}, Reason: {response2.content}\nPlease consult the tenant for information")

    else:
        print(f"\nUnable to successfuly validate payload for host {tempHostId}, Reason: {validator.content}\nPlease review configuration in the Dynatrace Tenant")

############################################

input("\nDone! Press enter to exit")
