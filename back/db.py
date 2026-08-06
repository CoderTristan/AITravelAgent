import os
from dotenv import load_dotenv

load_dotenv()
import boto3
import uuid
from datetime import datetime, timezone
from botocore.exceptions import ClientError

REGION_NAME = os.getenv("AWS_REGION", "us-east-2")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "chat_messages")

dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)

def init_table():
    """Creates the DynamoDB table if it does not exist."""
    try:
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'message_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'message_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMODB_TABLE_NAME)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            pass
        else:
            raise

def save_message(user_id: str, role: str, content: str):
    """Saves a single message to DynamoDB."""
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    message_id = f"{timestamp}#{uuid.uuid4().hex[:8]}"
    
    table.put_item(
        Item={
            'user_id': user_id,
            'message_id': message_id,
            'role': role,
            'content': content,
            'timestamp': timestamp
        }
    )

def get_chat_history(user_id: str) -> list[dict]:
    """Retrieves chronological chat history for a specific user."""
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    from boto3.dynamodb.conditions import Key
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    
    items = response.get('Items', [])
    return [{"role": item["role"], "content": item["content"]} for item in items]