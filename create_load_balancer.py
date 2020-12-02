import sys
import boto3
from botocore.exceptions import ClientError
import time

client_LB_NV = boto3.client('elb', region_name='us-east-1')


def delete_load_balancer(client, nome):
    client.delete_load_balancer(LoadBalancerName=nome)
    time.sleep(15)
    print("Load balancer terminado")


def create_load_balancer(client, nome, security_id):
    res = client.create_load_balancer(
        LoadBalancerName=nome,
        Listeners=[
            {
                'Protocol': 'HTTP',
                'LoadBalancerPort': 80,
                'InstancePort': 8080
            }
        ],
        AvailabilityZones=[
            'us-east-1a',
            'us-east-1b',
            'us-east-1c',
            'us-east-1d',
            'us-east-1e',
            'us-east-1f',
        ],
        SecurityGroups=[security_id],
        Tags=[
            {'Key': 'Name', 'Value': 'LoadBOrm'},
        ]
    )
    print("LoadBalancer Criado")
    with open("loadBalancer_DNS.txt", "w") as file:
        file.write(res['DNSName'])
