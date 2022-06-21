import boto3

def publish(msg):
    client = boto3.client('sns')
    response = client.publish(
        TopicArn = 'topic_arn',
        Message = msg,
        Subject = 'Wäscheupdate')
