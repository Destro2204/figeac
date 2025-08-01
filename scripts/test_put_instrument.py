import requests

# Change this to your server address if needed
SERVER = 'http://127.0.0.1:5050'

instrument_id = 2  # Change to 2 to test the second instrument
url = f'{SERVER}/api/instruments/{instrument_id}'

payload = {"status": "available"}
headers = {"Content-Type": "application/json"}

response = requests.put(url, json=payload, headers=headers)

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}') 