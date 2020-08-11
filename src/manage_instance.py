import boto3
import click
import os


def run_create_process():
    try:
        create_key_pair()
        return create_instances()
    except:
        return create_instances()


def create_key_pair():
    # Creates key pair necessary for creating instances
    # Returns key pair as string
    ec2 = boto3.resource('ec2')
    outfile = open('jtrain.pem','w')
    key_pair = ec2.create_key_pair(KeyName='jtrain')
    KeyPairOut = str(key_pair.key_material)
    outfile.write(KeyPairOut)
    return KeyPairOut


def create_instances(count=1):
    # Creates specified number of instances, default is 1
    # Returns instances
    ec2 = boto3.resource('ec2')
    instances = []
    for i in range(count):
        inst = ec2.create_instances(
                ImageId = 'ami-0b59bfac6be064b78',
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.nano',
                KeyName='jtrain'
                )
        instances.append(inst)
    return instances


def get_active_instance_ids():
    # Returns list of ids for active instances
    active_ids = [i['InstanceId'] for i in get_active_instances()]
    return active_ids


def get_active_instances():
    # Returns list of active instances
    ec2client = boto3.client('ec2')
    response = ec2client.describe_instances()
    instances_2d = [r['Instances'] for r in response['Reservations']]
    instances = [i for j in instances_2d for i in j]
    active_instances = [i for i in instances if i['State']['Code']==16]
    return active_instances


def get_active_instance_ids():
    # Returns list of ids for active instances
    active_ids = [i['InstanceId'] for i in get_active_instances()]
    return active_ids


def terminate_instance(instance_id):
    # Terminates instance w/ given id
    # Returns terminated instance
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    terminated = instance.terminate()
    return terminated


def terminate_all_active_instances():
    # Terminates all active instances
    # Returns terminated instances
    active = get_active_instance_ids()
    terminations = [terminate_instance(a) for a in active]
    return terminations




if __name__ == "__main__":
    main()
