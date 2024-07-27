from flask import Flask, request, jsonify
from kafka import KafkaConsumer
import pika
from pyfcm import FCMNotification
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import json

app = Flask(_name_)

# Firebase Cloud Messaging configuration
FCM_API_KEY = "YOUR_FCM_SERVER_KEY"
push_service = FCMNotification(api_key=FCM_API_KEY)

# Twilio SMS configuration
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'your-email@example.com'
SMTP_PASSWORD = 'your-email-password'

# Kafka Consumer setup
KAFKA_TOPIC = "flight_status"
KAFKA_SERVERS = ['localhost:9092']
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVERS)

# RabbitMQ setup
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_HOST = 'localhost'

def send_push_notification(user_token, message_title, message_body):
    result = push_service.notify_single_device(registration_id=user_token, message_title=message_title, message_body=message_body)
    return result

def send_sms(to, body):
    message = twilio_client.messages.create(
        body=body,
        from_='+1234567890',
        to=to
    )
    return message.sid

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to], msg.as_string())

def callback(ch, method, properties, body):
    data = json.loads(body)
    user_token = data.get('user_token')
    user_email = data.get('user_email')
    user_phone = data.get('user_phone')
    flight_status = data.get('flight_status')

    message_title = "Flight Status Update"
    message_body = f"Your flight status has changed: {flight_status}"

    if user_token:
        send_push_notification(user_token, message_title, message_body)
    if user_email:
        send_email(user_email, message_title, message_body)
    if user_phone:
        send_sms(user_phone, message_body)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    user_token = data.get('user_token')
    user_email = data.get('user_email')
    user_phone = data.get('user_phone')
    flight_status = data.get('flight_status')

    message_title = "Flight Status Update"
    message_body = f"Your flight status has changed: {flight_status}"

    if user_token:
        send_push_notification(user_token, message_title, message_body)
    if user_email:
        send_email(user_email, message_title, message_body)
    if user_phone:
        send_sms(user_phone, message_body)

    return jsonify({"message": "Notifications sent"}), 200

def consume_kafka_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    for message in consumer:
        flight_status_update = message.value.decode('utf-8')
        data = {
            "user_token": "user_device_token",
            "user_email": "user@example.com",
            "user_phone": "+1234567890",
            "flight_status": flight_status_update
        }
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=json.dumps(data))

    connection.close()

def consume_rabbitmq_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if _name_ == '_main_':
    from threading import Thread
    kafka_thread = Thread(target=consume_kafka_messages)
    rabbitmq_thread = Thread(target=consume_rabbitmq_messages)

    kafka_thread.start()
    rabbitmq_thread.start()

    app.run(debug=True)