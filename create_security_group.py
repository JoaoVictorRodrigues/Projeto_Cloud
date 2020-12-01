import sys
import boto3
from botocore.exceptions import ClientError


client_Inst_NV = boto3.client('ec2', region_name='us-east-1')


def delete_security_group(client, sGroupName):
    response = client.describe_security_groups()
    for group in response['SecurityGroups']:
        if group['GroupName'] == sGroupName:
            client.delete_security_group(GroupName=sGroupName)


def create_security_group(client, sGroupName):

    response = client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = client.create_security_group(GroupName=sGroupName,
                                                Description='Security Group',
                                                VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' %
              (security_group_id, vpc_id))

        data = client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                 {'IpProtocol': 'tcp',
                 'FromPort': 8080,
                 'ToPort': 8080,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                 {'IpProtocol': 'tcp',
                 'FromPort': 5432,
                 'ToPort': 5432,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])

        return security_group_id
    except ClientError as e:
        print(e)
