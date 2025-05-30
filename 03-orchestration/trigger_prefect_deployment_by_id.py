import requests

deployment_id = '5ec63a86-3a8b-4506-b004-77514df844d2'

payload = {
    "parameters": {
        'color': 'yellow',
        'year': 2023,
        'month': 3,
        'modeltype': 'XGB',
        'read_local': True
    }
}
response = requests.post(
    f'http://localhost:4200/api/deployments/{deployment_id}/create_flow_run',
    json=payload
)

if response.status_code==200:
    print(f'flow successfully triggered: {response.json()}')
else:
    print(f'error (status: {response.status_code}) triggering flow: {response.text}')