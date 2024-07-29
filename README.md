**Real-Time Indigo-Flight Status and Notification System**

Introduction:
Our project provides real-time Indigo-flight status updates and notifications to passengers.
This project includes the following features:
Real-time Updates: 
It displays current flight status (delays, cancellations, gate changes).
Push Notifications: 
It sends notifications to passengers for flight status changes via SMS, email, or app notifications using Kafka and RabbitMQ.
Integrated with Airport Systems: 
It pulls data from airport databases for accurate information (mock data provided for testing).

**Getting Started**

Prerequisites:
Node.js and npm
Python and pip
Kafka
RabbitMQ
MongoDB
PostgreSQL

**Configuration**

Backend Configuration:
Updated the notification_service.py with our Firebase, Twilio, and SMTP credentials.
Mock API :
Installed the json-server and created a db.json file for mock data.
npm install -g 
json-server
json-server --watch 
db.json --port 5000

**Running the Application**

Started the Frontend:
cd frontend
npm start

Started the Backend:
cd ../backend
python 
notification_service.py

Start Kafka and RabbitMQ:
Ensure Kafka and RabbitMQ are running on your local machine.

**Usage**

Opened our browser and navigated to http://localhost:3000 to see the flight status table.
The backend service will listen for flight status updates from Kafka, push updates to RabbitMQ, and send notifications using FCM, Twilio, and email.
