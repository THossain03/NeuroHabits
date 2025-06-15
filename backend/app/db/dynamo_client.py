from typing import Dict, List, Any, Optional, Union
import boto3
from botocore.exceptions import ClientError
from ..config.db_config import get_db_config

class DynamoDBClient:
    """A client wrapper for DynamoDB operations with error handling and type hints."""
    
    def __init__(self):
        config = get_db_config()
        self.client = boto3.client(
            'dynamodb',
            region_name=config.region_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            endpoint_url=config.endpoint_url
        )
        self.resource = boto3.resource(
            'dynamodb',
            region_name=config.region_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            endpoint_url=config.endpoint_url
        )
    
    def create_table(self, table_name: str, key_schema: List[Dict[str, str]], 
                    attribute_definitions: List[Dict[str, str]], 
                    provisioned_throughput: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Create a new DynamoDB table."""
        try:
            params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
            }
            if provisioned_throughput:
                params['ProvisionedThroughput'] = provisioned_throughput
            
            response = self.client.create_table(**params)
            return response
        except ClientError as e:
            raise Exception(f"Failed to create table {table_name}: {str(e)}")
    
    def delete_table(self, table_name: str) -> Dict[str, Any]:
        """Delete a DynamoDB table."""
        try:
            response = self.client.delete_table(TableName=table_name)
            return response
        except ClientError as e:
            raise Exception(f"Failed to delete table {table_name}: {str(e)}")
    
    def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put a single item into a table."""
        try:
            table = self.resource.Table(table_name)
            response = table.put_item(Item=item)
            return response
        except ClientError as e:
            raise Exception(f"Failed to put item in table {table_name}: {str(e)}")
    
    def batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write multiple items to a table in batch."""
        try:
            table = self.resource.Table(table_name)
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            return {"message": f"Successfully wrote {len(items)} items to {table_name}"}
        except ClientError as e:
            raise Exception(f"Failed to batch write items to table {table_name}: {str(e)}")
    
    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single item from a table."""
        try:
            table = self.resource.Table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get item from table {table_name}: {str(e)}")
    
    def query(self, table_name: str, key_condition_expression: str, 
              expression_attribute_values: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query items from a table."""
        try:
            table = self.resource.Table(table_name)
            response = table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to query table {table_name}: {str(e)}")
    
    def scan(self, table_name: str, filter_expression: Optional[str] = None,
             expression_attribute_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Scan items from a table with optional filtering."""
        try:
            table = self.resource.Table(table_name)
            params = {}
            if filter_expression:
                params['FilterExpression'] = filter_expression
            if expression_attribute_values:
                params['ExpressionAttributeValues'] = expression_attribute_values
            
            response = table.scan(**params)
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to scan table {table_name}: {str(e)}")
    
    def update_item(self, table_name: str, key: Dict[str, Any], 
                   update_expression: str, expression_attribute_values: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item in a table."""
        try:
            table = self.resource.Table(table_name)
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to update item in table {table_name}: {str(e)}")
    
    def delete_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an item from a table."""
        try:
            table = self.resource.Table(table_name)
            response = table.delete_item(Key=key)
            return response
        except ClientError as e:
            raise Exception(f"Failed to delete item from table {table_name}: {str(e)}")

# Create a singleton instance
db_client = DynamoDBClient() 