import sys
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')


# Deleta uma instancia caso exista e cria uma nova

def create_instance():

    instance_id = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['Teste']
            }
        ]
    )

    ids = []
    for reservation in (instance_id["Reservations"]):
        for instance in reservation["Instances"]:
            ids.append(instance["InstanceId"])

    try:
        ec2.terminate_instances(InstanceIds=ids)
        print('Instancia:', ids, ' terminadas')
    except ClientError as e:
        print(e)


    userdata_oregon = """#!/bin/sh
    cd home/ubuntu
    sudo apt update
    git clone https://github.com/JoaoVictorRodrigues/Projeto_Cloud.git
    ./config_db.sh
    """
    # create a new EC2 instance
    try:
        instances = ec2.run_instances(
            ImageId='ami-0885b1f6bd170450c',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            SecurityGroupIds=['sg-066bdfd38838f1d12'],
            KeyName='Pub-JoaoR',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'Teste',
                        },
                    ],
                },
            ],
            UserData=userdata_oregon
        )
    except ClientError as e:
        print(e)


create_instance()
