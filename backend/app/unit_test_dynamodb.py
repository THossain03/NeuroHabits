import boto3
from botocore.exceptions import ClientError

# Sample Initialization of DynamoDB (TODO: set up still in progress)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # TODO: Replace with dynamic region configuration later. Apply us-east-1 for now solely during in dev.
table_name = 'YourTableName'

# Create DynamoDB Table (Run this once)
def create_table():
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully!")
    except ClientError as e:
        print(f"Error creating table: {e}")