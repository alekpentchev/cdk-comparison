import boto3
import os

import cfnresponse

dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    table_name = os.environ['TABLE_NAME']
    
    try:
        table = dynamodb.Table(table_name)

        # Check if the table is empty
        response = table.scan()
        if response.get('Count', 0) == 0:
            # 10 most common medicines to the table
            medicines = [
                {'name': 'Paracetamol', 'description': 'Paracetamol is a painkiller used to treat aches and pains. It can also be used to reduce a high temperature. It\'s available combined with other painkillers and anti-sickness medicines.'},
                {'name': 'Ibuprofen', 'description': 'Ibuprofen is a painkiller available over the counter without a prescription. It\'s one of a group of painkillers called non-steroidal anti-inflammatory drugs (NSAIDs) and can be used to ease mild to moderate pain, inflammation and fever.'},
                {'name': 'Aspirin', 'description': 'Aspirin is a common painkiller for children and adults. It\'s often used to treat headaches, stomach ache, toothache, and sore throats.'},
                {'name': 'Lansoprazole', 'description': 'Lansoprazole reduces the amount of acid your stomach makes. It\'s used for indigestion, heartburn and acid reflux and gastroesophageal-reflux-disease (GORD).'},
                {'name': 'Omeprazole', 'description': 'Omeprazole reduces the amount of acid your stomach makes. It\'s a widely-used treatment for indigestion and acid reflux.'},
                {'name': 'Simvastatin', 'description': 'Simvastatin is a medicine used to lower cholesterol. If you have high cholesterol, taking simvastatin might help prevent heart disease and hardening of the arteries, strokes and heart attacks.'},
                {'name': 'Atorvastatin', 'description': 'Atorvastatin is a medicine used to lower cholesterol. If you have high cholesterol, taking atorvastatin might help prevent heart disease and hardening of the arteries, strokes and heart attacks.'},
                {'name': 'Ramipril', 'description': 'Ramipril is a medicine widely used to treat high blood pressure and heart failure. It\'s also prescribed after a heart attack.'},
                {'name': 'Amlodipine', 'description': 'Amlodipine is a medicine used to treat high blood pressure (hypertension). If you have high blood pressure, taking amlodipine helps prevent future heart disease, heart attacks and strokes.'},
                {'name': 'Bendroflumeth', 'description': 'Bendroflumethiazide is a type of medicine called a thiazide diuretic. Diuretics are sometimes called "water pills/tablets" because they make you pee more.'}
            ]
            
            # Insert data into the table
            for medicine in medicines:
                table.put_item(Item=medicine)
                
        response_data = {
            "Status": "SUCCESS",
            "RequestId": event.get("RequestId"),
            "LogicalResourceId": event.get("LogicalResourceId"),
            "PhysicalResourceId": "LambdaPrefillCustomResource",
        }

        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        return "SUCCESS"
    except Exception as e:
        response_data = {
            "Status": "FAILED",
            "Reason": str(e),
            "RequestId": event.get("RequestId"),
            "LogicalResourceId": event.get("LogicalResourceId"),
            "PhysicalResourceId": "LambdaPrefillCustomResource",
        }

        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)