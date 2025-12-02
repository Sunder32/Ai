import requests

try:
    response = requests.get('http://localhost:8000/api/computers/cpu/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Found {len(data.get('results', []))} CPUs")
        print(f"Response keys: {data.keys()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
