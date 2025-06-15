import pytest
from moto import mock_dynamodb
from backend.app.db.dynamo_client import DynamoDBClient

@pytest.fixture
def dynamo_client():
    with mock_dynamodb():
        client = DynamoDBClient()
        # Create a test table
        client.create_table(
            table_name='TestTable1',
            key_schema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            attribute_definitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            provisioned_throughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        yield client

def test_create_table(dynamo_client):
    """Test table creation"""
    response = dynamo_client.create_table(
        table_name='TestTable2',
        key_schema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        attribute_definitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ]
    )
    assert 'TableDescription' in response
    assert response['TableDescription']['TableName'] == 'TestTable2'

def test_put_and_get_item(dynamo_client):
    """Test putting and getting an item"""
    # Put an item
    item = {
        'id': 'test123',
        'data': 'test data'
    }
    dynamo_client.put_item('TestTable1', item)
    
    # Get the item
    retrieved_item = dynamo_client.get_item('TestTable1', {'id': 'test123'})
    assert retrieved_item is not None
    assert retrieved_item['id'] == 'test123'
    assert retrieved_item['data'] == 'test data'

def test_scan_items(dynamo_client):
    """Test scanning items"""
    # Put multiple items
    items = [
        {'id': 'test1', 'data': 'data1'},
        {'id': 'test2', 'data': 'data2'}
    ]
    for item in items:
        dynamo_client.put_item('TestTable1', item)
    
    # Scan items
    scanned_items = dynamo_client.scan('TestTable1')
    assert len(scanned_items) == 2
    assert any(item['id'] == 'test1' for item in scanned_items)
    assert any(item['id'] == 'test2' for item in scanned_items)

def test_delete_item(dynamo_client):
    """Test deleting an item"""
    # Put an item
    item = {'id': 'test123', 'data': 'test data'}
    dynamo_client.put_item('TestTable1', item)
    
    # Delete the item
    dynamo_client.delete_item('TestTable1', {'id': 'test123'})
    
    # Verify item is deleted
    retrieved_item = dynamo_client.get_item('TestTable1', {'id': 'test123'})
    assert retrieved_item is None

def test_batch_write_items(dynamo_client):
    """Test batch writing items"""
    items = [
        {'id': 'batch1', 'data': 'data1'},
        {'id': 'batch2', 'data': 'data2'},
        {'id': 'batch3', 'data': 'data3'}
    ]
    
    response = dynamo_client.batch_write_items('TestTable1', items)
    assert 'message' in response
    
    # Verify all items were written
    scanned_items = dynamo_client.scan('TestTable1')
    assert len(scanned_items) == 3
    for item in items:
        assert any(scanned['id'] == item['id'] for scanned in scanned_items)

def test_query_items(dynamo_client):
    """Test querying items"""
    # Put items with different attributes
    items = [
        {'id': 'test1', 'type': 'A', 'data': 'data1'},
        {'id': 'test2', 'type': 'A', 'data': 'data2'},
        {'id': 'test3', 'type': 'B', 'data': 'data3'}
    ]
    for item in items:
        dynamo_client.put_item('TestTable1', item)
    
    # Query items with type 'A'
    queried_items = dynamo_client.query(
        'TestTable1',
        'type = :type',
        {':type': 'A'}
    )
    assert len(queried_items) == 2
    assert all(item['type'] == 'A' for item in queried_items) 