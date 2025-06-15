from .dynamo_client import db_client

def create_initial_tables():
    """Create initial tables for the application."""
    tables = [
        {
            'table_name': 'TestTable1',
            'key_schema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'attribute_definitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            'provisioned_throughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
        # Add more table definitions here as needed
    ]
    
    for table_config in tables:
        try:
            print(f"Creating table {table_config['table_name']}...")
            response = db_client.create_table(**table_config)
            print(f"Table {table_config['table_name']} created successfully!")
            print(f"Table ARN: {response['TableDescription']['TableArn']}")
        except Exception as e:
            print(f"Error creating table {table_config['table_name']}: {str(e)}")

if __name__ == '__main__':
    create_initial_tables() 