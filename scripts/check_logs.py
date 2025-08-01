import requests

logs = requests.get('http://localhost:5050/api/access-logs').json()
print("Recent Access Logs:")
print("=" * 50)
for log in logs[-10:]:
    print(f"{log['name']} ({log['status']}): {log['action']}") 