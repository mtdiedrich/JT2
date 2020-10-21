from datetime import date

import botocore
import boto3
import os


RESOURCE_NAME = 'jtrain'
OBJECT_NAME = 'jtrainDW'


def to_rds(db_path):
    """
    Migrate local DB to RDS.

    Args:
        db_path: the /path/to/the/db
    Returns:
        RDS DB configuration
    """
    s3_path = to_s3(db_path)
    rds_config = restore_from_s3(s3_path)
    return rds_config


def to_s3(db_path):
    """
    Store local DB on S3.

    Args:
        db_path: the /path/to/the/db
    Returns:
        s3_path: the S3 path of the DB
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(RESOURCE_NAME)
    try: 
        s3.meta.client.head_bucket(Bucket=bucket.name)
    except botocore.client.ClientError:
        bucket = s3.create_bucket(Bucket=RESOURCE_NAME)
    db_name = '-'.join([str(date.today()), OBJECT_NAME])
    bucket.upload_file(db_path, db_name)
    s3_path = '/'.join([RESOURCE_NAME, OBJECT_NAME])
    return s3_path


def restore_from_s3(s3_path):
    """
    Restore RDS DB instance from S3.

    Args:
        s3_path: the S3 path of the DB
    Returns:
        Config dict for restored RDS instance
    """
    master_user = input('Enter master username: ')
    master_pwd = input('Enter master password: ')
    ARN = 'arn:aws:iam::{}:role/jtrain-role'.format(os.environ['OWNER'])
    ARN = 'arn:aws:iam::961181693216:role/jtrain-role'
    rds = boto3.client('rds', region_name='us-east-1')
    rds_config = rds.restore_db_instance_from_s3(
                        DBInstanceIdentifier=OBJECT_NAME,
                        DBInstanceClass='db.t3.micro',
                        MasterUsername='Mitchy',
                        MasterUserPassword='temppassword',
                        AllocatedStorage=20,
                        Engine='mysql',
                        SourceEngine='mysql',
                        SourceEngineVersion='5.6',
                        S3BucketName=RESOURCE_NAME,
                        S3IngestionRoleArn=ARN,
                        )
    return rds_config
