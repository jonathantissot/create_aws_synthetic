import uuid
import json
import datetime
import zipfile
import boto3
import time
from os.path import basename
from io import BytesIO

UID = uuid.uuid4().hex
TODAY = datetime.datetime.today().strftime('%Y-%m-%d')

TRUST_POLICY={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}


MANAGED_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "CloudWatchPutMetrics",
            "Action": "cloudwatch:PutMetricData",
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "LogsWrite",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "CustomAdd",
            "Action": [],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}

def read_yaml(filename=None):
    import yaml

    stream = open(filename, 'r')
    try:
        file_details = yaml.safe_load(stream)
    except yaml.YAMLError:
        print("Not yaml file...")
        return None
    return file_details


def create_synthetics(
    session: boto3.Session,
    configuration: {},
    role_arn: str,
    name: str = ''):
    # Use a breakpoint in the code line below to debug your script.
    client = session.client(
        'synthetics'
    )

    if not name:
        name = UID

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zip_path = configuration['zip_path']
        zip_info = zipfile.ZipInfo(zip_path)
        zip_info.external_attr = 0o0755 << 16  # Ensure the file is readable
        zf.write(zip_path, basename(zip_path))
    zip_buffer.seek(0)

    response = client.create_canary(
        Name=name,
        Code={
            'ZipFile': bytearray(zip_buffer.read()),
            'Handler': configuration['handler']
        },
        ArtifactS3Location=configuration['artifact_location'],
        ExecutionRoleArn=role_arn,
        Schedule={
            'Expression': configuration['expression'],
            'DurationInSeconds': configuration['duration_in_seconds']
        },
        RunConfig={
            'TimeoutInSeconds': configuration['timeout'],
            'MemoryInMB': configuration['memory_in_mb'],
            'ActiveTracing': False,
            'EnvironmentVariables': configuration['environment_variables']
        },
        SuccessRetentionPeriodInDays=30,
        FailureRetentionPeriodInDays=30,
        RuntimeVersion=configuration['runtime_version']
    )


def create_role(session: boto3.Session, name: str = '', configuration: {} = None):
    client = session.client(
        'iam'
    )

    role_name=f"canary-synth-{UID}"
    role = client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(TRUST_POLICY),
        Description=f"Canary Synthetic role created for {name}"
    )
    if 'actions' in configuration and configuration['actions']:
        for policy in MANAGED_POLICY['Statement']:
            if policy['Sid'] == 'CustomAdd':
                policy['Action'] = configuration['actions']

    policy_name=f'Policy-{name}-{UID}'
    policy = client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(MANAGED_POLICY)
    )

    client.attach_role_policy(
        PolicyArn=policy['Policy']['Arn'],
        RoleName=role_name
    )
    print(role['Role']['Arn'])
    return role['Role']['Arn']


def main():
    import sys
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Provide file name and keyfile, such as:\npython3 automation.py playbook.yml\n")
        print("Check also playbook.yml file for details\n")
        return
    data = read_yaml(filename=filename)
    try:
        name = data['name']
        credentials = data['credentials']
        configuration = data['configuration']
    except KeyError:
        print("Not all data has been filled. Name, credentials, and configuration is required")

    if 'session_token' in credentials and credentials['session_token']:
        session = boto3.Session(
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
            aws_session_token=credentials['session_token'],
            region_name='us-east-1'
        )
    elif 'profile_name' in credentials and credentials['profile_name']:
        session = boto3.Session(
            profile_name=credentials['profile_name'],
            region_name='us-east-1'
        )
    else:
        session = boto3.Session(
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key'],
            region_name='us-east-1'
        )
    role_arn = create_role(session=session, name=name, configuration=configuration)
    time.sleep(15)
    create_synthetics(
        session=session,
        configuration=configuration,
        role_arn=role_arn,
        name=name
    )

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
