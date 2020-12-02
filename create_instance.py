import sys
import boto3
from botocore.exceptions import ClientError
from create_security_group import *


client_Inst_NV = boto3.client('ec2', region_name='us-east-1')
resource_NV = boto3.resource('ec2', region_name='us-east-1')

client_Inst_Oh = boto3.client('ec2', region_name='us-east-2')
resource_Oh = boto3.resource('ec2', region_name='us-east-2')


waiterInicialize_NV = client_Inst_NV.get_waiter('instance_status_ok')
waiterInicialize_Oh = client_Inst_Oh.get_waiter('instance_status_ok')


def get_ip(client, nome):
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


def get_instance_id(client, nome):
    instance_id = client.describe_instances(
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
    inst_id = instance_id['Reservations'][0]['Instances'][0]['InstanceId']
    print(inst_id)
    return(inst_id)


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


def create_instance_Oh(security_id):
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
            SecurityGroupIds=[security_id],
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
        client_Inst_Oh.get_waiter('instance_status_ok').wait(
            InstanceIds=[instance[0].id])
        print("Ohio_DB criado e rodando")

    except ClientError as e:
        print(e)


# Cria a instancia de North Virginia
def create_instance_NV(security_id, inst_ip):

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
        instance = resource_NV.create_instances(
            ImageId='ami-0885b1f6bd170450c',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            SecurityGroupIds=[security_id],
            KeyName='Pub-JoaoR',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'NorthV_ORM',
                        },
                    ],
                },
            ],
            UserData=userData_Nv
        )
        client_Inst_NV.get_waiter('instance_status_ok').wait(
            InstanceIds=[instance[0].id])
        print("NorthV_ORM criado e rodando")
    except ClientError as e:
        print(e)


def delete_image(nome):
    try:
        image_id = client_Inst_NV.describe_images(
            Filters=[
                {
                    'Name': 'name',
                    'Values': [nome]
                }
            ]
        )
        if len(image_id['Images']) > 0:
            inst_id = image_id['Images'][0]['ImageId']
            print(inst_id)
            client_Inst_NV.deregister_image(ImageId=inst_id)
    except ClientError as e:
        print(e)


def create_AMI_ORM(instance_id, nome):

    ami = client_Inst_NV.create_image(
        InstanceId=instance_id, NoReboot=True, Name=nome)
    client_Inst_NV.get_waiter('image_available').wait(
        ImageIds=[ami["ImageId"]])
    print("Imagem criada")
    return ami['ImageId']
    #delete_instances(client_Inst_NV, 'NorthV_ORM')
