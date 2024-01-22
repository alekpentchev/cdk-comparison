import json
import os

import boto3

def handler(event, context):
    # Specify your DynamoDB table name
    dynamodb_table_name = os.getenv('TABLE_NAME')

    # Create a DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table_name)

    try:
        # Scan the table to get all items (medicines)
        response = table.scan()

        # Extract the items from the response
        medicines = response.get('Items', [])

        # Convert the items to a JSON-formatted string
        medicines_json = json.dumps(medicines)

        # Return the JSON response
        return {
            'statusCode': 200,
            'body': medicines_json
        }

    except Exception as e:
        # Handle any exceptions and return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
