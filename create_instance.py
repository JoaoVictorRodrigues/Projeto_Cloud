import sys
import boto3
from botocore.exceptions import ClientError
from create_security_group import *

# ec2 = boto3.client('ec2')


client_Inst_NV = boto3.client('ec2', region_name='us-east-1')
resource_NV = boto3.resource('ec2', region_name='us-east-1')


lb_client_Inst_NV = boto3.client('elb', region_name='us-east-1')
aa_client_Inst_NV = boto3.client('autoscaling')

client_Inst_Oh = boto3.client('ec2', region_name='us-east-2')
resource_Oh = boto3.resource('ec2', region_name='us-east-2')


waiterInicialize_NV = client_Inst_NV.get_waiter('instance_status_ok')
waiterInicialize_Oh = client_Inst_Oh.get_waiter('instance_status_ok')


def getIp(client, nome):
    ip = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [nome]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ])
    inst_ip = ip['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return(inst_ip)

# Deleta uma instancia caso exista


def delete_instances(client, nome):
    instance_id = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [nome]
            }
        ]
    )

    ids = []
    for reservation in (instance_id["Reservations"]):
        for instance in reservation["Instances"]:
            ids.append(instance["InstanceId"])

    try:
        client.terminate_instances(InstanceIds=ids)
        client.get_waiter('instance_terminated').wait(InstanceIds=ids)
        print('Instancia:', nome, ' terminada')
    except ClientError as e:
        print(e)

# Cria a instancia de Ohio


def create_instance_Oh():
    userData_Oh = """#!/bin/sh
    cd home/ubuntu
    sudo apt update
    git clone https://github.com/JoaoVictorRodrigues/Projeto_Cloud.git
    cd Projeto_Cloud
    chmod +x config_db.sh
    ./config_db.sh
    """
    # create a new EC2 instance
    try:
        instance = resource_Oh.create_instances(
            ImageId='ami-0dd9f0e7df0f0a138',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            SecurityGroupIds=[Ohio],
            KeyName='Pub_JoaoR_2',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'Ohio_DB',
                        },
                    ],
                },
            ],
            UserData=userData_Oh
        )
        waiterInicialize_Oh.wait(InstanceIds=[instance[0].id])
        print("Fim do waiter")

    except ClientError as e:
        print(e)


# Cria a instancia de North Virginia
def create_instance_NV():

    userData_Nv = """#!/bin/sh
    cd home/ubuntu
    sudo apt update
    git clone https://github.com/raulikeda/tasks.git
    sudo sed -i 's/node1/{0}/' /home/ubuntu/tasks/portfolio/settings.py
    cd tasks
    ./install.sh
    cd ..
    sudo reboot
    """.format(inst_ip)
    try:
        instance_NV = client_Inst_NV.run_instances(
            ImageId='ami-0885b1f6bd170450c',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            SecurityGroupIds=[North],
            KeyName='Pub-JoaoR',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'NV',
                        },
                    ],
                },
            ],
            UserData=userData_Nv
        )
    except ClientError as e:
        print(e)


delete_instances(client_Inst_Oh, 'Ohio_DB')
delete_instances(client_Inst_NV, 'NV')

delete_security_group(client_Inst_Oh, "SgOhio")
delete_security_group(client_Inst_NV, "SgNorth")

Ohio = create_security_group(client_Inst_Oh, "SgOhio")
North = create_security_group(client_Inst_NV, "SgNorth")

create_instance_Oh()

inst_ip = getIp(client_Inst_Oh,'Ohio_DB')

create_instance_NV()
