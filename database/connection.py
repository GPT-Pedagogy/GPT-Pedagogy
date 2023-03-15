# access_key = 'AKIA3XFQ37CTBNQM5LHH'
# secret_Access_key = 'offjM6eq4Vl2AuK/8JRR9s1vZ0Fe7clmaGKBwWLd'

import os
import boto3
from dotenv import load_dotenv

load_dotenv()



# Your AWS access key and secret access key
aws_access_key_id = os.getenv('ACCESS_KEY')
aws_secret_access_key = os.getenv('SECRET_ACCESS_KEY')
aws_region = os.getenv('REGION')


print(aws_access_key_id, aws_secret_access_key, aws_region)
# Create a custom session with your access key and secret access key
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Create a DynamoDB resource using the custom session
dynamodb = session.resource('dynamodb')

# Connect to a specific table
table_name = 'students_info'
table = dynamodb.Table(table_name)

# Scan the table
response = table.scan()

# Print the scanned items
for item in response['Items']:
    print(item['RCSid'])

    print(item)

# TODO: Query function
# TODO: Update function
# TODO: create new user -> add into dbs 
# TODO: upload the performance to DBS
