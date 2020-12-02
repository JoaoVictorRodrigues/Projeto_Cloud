import sys
import boto3
from botocore.exceptions import ClientError
from create_security_group import *
from create_load_balancer import *
from create_auto_caling import *
from create_instance import *
import time

#Deleta antes de criar para não haver conflito
delete_instances(client_Inst_Oh, 'Ohio_DB')
delete_instances(client_Inst_NV, 'NorthV_ORM')
delete_load_balancer(client_LB_NV,'LoadBalancer')
delete_AS_launch(client_AS_NV,'LaunchAS')
delete_auto_scaling(client_AS_NV,'AutoScaling')

time.sleep(60)
delete_security_group(client_Inst_Oh, "SgOhio")
delete_security_group(client_Inst_NV, "SgNorth")

#Criação
Ohio = create_security_group(client_Inst_Oh, "SgOhio")
North = create_security_group(client_Inst_NV, "SgNorth")

create_instance_Oh(Ohio)

inst_ip = get_ip(client_Inst_Oh,'Ohio_DB')
create_instance_NV(North,inst_ip)
inst_id = get_instance_id(client_Inst_NV,'NorthV_ORM')

delete_image('ORM')

ami = create_AMI_ORM(inst_id,'ORM')

create_load_balancer(client_LB_NV,'LoadBalancer',North)

create_AS_launch(client_AS_NV,'LaunchAS',ami,North)



create_auto_scalling(client_AS_NV, 'AutoScaling','LaunchAS')