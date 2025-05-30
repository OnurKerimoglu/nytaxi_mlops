import requests

def get_deployment_id(flow_name, deployment_name):
    print(f'trying to get the deployment_id for flow_name/deployment_name: {flow_name}/{deployment_name}')

    url = f'http://localhost:4200/api/deployments/name/{flow_name}/{deployment_name}'
    response = requests.get(url)

    if response.status_code == 200:
        deployment = response.json()
        deployment_id = deployment['id']
        print(f'deployment_id: {deployment_id}')
        return deployment_id
    else:
        raise Exception(f'Error: {response.status_code} - {response.text}')
    
flow_name = 'nyc-taxi-train-pipeline'
deployment_name = 'nyctaxi_train'
deployment_id = get_deployment_id(flow_name, deployment_name)
# deployment_id = '5ec63a86-3a8b-4506-b004-77514df844d2'

payload = {
    "parameters": {
        'color': 'yellow',
        'year': 2023,
        'month': 3,
        'modeltype': 'LR',
        'read_local': True
    }
}
# response = requests.post(
#     f'http://localhost:4200/api/deployments/{deployment_id}/create_flow_run',
#     json=payload
# )

# if response.status_code==200:
#     print(f'flow successfully triggered: {response.json()}')
# else:
#     print(f'error (status: {response.status_code}) triggering flow: {response.text}')