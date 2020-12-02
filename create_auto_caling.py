import sys
import boto3
from botocore.exceptions import ClientError
import time

client_AS_NV = boto3.client('autoscaling')


def delete_AS_launch(client, nome):
    launch_name = client.describe_launch_configurations(
        LaunchConfigurationNames=[nome])
    try:
      if len(launch_name['LaunchConfigurations']):
          client.delete_launch_configuration(LaunchConfigurationName=nome)
          #client.get_waiter('launch_deleted').wait(LaunchConfigurationName=nome)
          print("Launch terminado")
    except ClientError as e:
      print(e)


def create_AS_launch(client, nome, image, security_id):

    client.create_launch_configuration(
        LaunchConfigurationName=nome,
        ImageId=image,
        KeyName='Pub-JoaoR',
        SecurityGroups=[security_id],
        InstanceType='t2.micro'
    )
    print("Launch Criado")


def delete_auto_scaling(client, nome):
    as_name = client.describe_auto_scaling_groups(AutoScalingGroupNames=[nome])
    for name in as_name["AutoScalingGroups"]:
        if name['AutoScalingGroupName'] == nome:
            client.delete_auto_scaling_group(
                AutoScalingGroupName=nome, ForceDelete=True)


def create_auto_scalling(client, nome, launch_name):

    client.create_auto_scaling_group(
        AutoScalingGroupName=nome,
        LaunchConfigurationName=launch_name,
        MinSize=2,
        MaxSize=5,
        DesiredCapacity=2,
        AvailabilityZones=[
            'us-east-1a',
            'us-east-1b',
            'us-east-1c',
            'us-east-1d',
            'us-east-1e',
            'us-east-1f',
        ],
        LoadBalancerNames=['LoadBalancer'],
        CapacityRebalance=True
    )
    print("AS Criado")
