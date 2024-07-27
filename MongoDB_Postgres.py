from flask import Flask, request, jsonify
from pymongo import MongoClient
import psycopg2
import random

app = Flask(_name_)

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["flight_status_db"]
mongo_collection = mongo_db["flight_status"]

# PostgreSQL configuration
POSTGRES_URI = "dbname='flightdb' user='user' password='password' host='localhost'"
postgres_conn = psycopg2.connect(POSTGRES_URI)
postgres_cursor = postgres_conn.cursor()

# Mock flight data
mock_flights = [
    {"id": 1, "airline": "Airline Indigo", "flight_number": "6E 203", "status": "On Time", "gate": "T1"},
    {"id": 2, "airline": "Airline Vistara", "flight_number": "UK 944", "status": "Delayed", "gate": "T2"},
    {"id": 3, "airline": "Airline Akasa Air", "flight_number": "QP 1101", "status": "Cancelled", "gate": "T3"}
]

# Endpoint to get flight status
@app.route('/api/flights', methods=['GET'])
def get_flight_status():
    # Simulate pulling data from MongoDB
    mongo_flights = list(mongo_collection.find({}, {'_id': 0}))

    # Simulate pulling data from PostgreSQL
    postgres_cursor.execute("SELECT * FROM flights")
    postgres_flights = postgres_cursor.fetchall()
    postgres_flights = [
        {"id": row[0], "airline": row[1], "flight_number": row[2], "status": row[3], "gate": row[4]}
        for row in postgres_flights
    ]

    # Combine data from both sources (for demonstration purposes)
    all_flights = mongo_flights + postgres_flights
    return jsonify(all_flights)

# Endpoint to populate mock data
@app.route('/api/populate', methods=['POST'])
def populate_data():
    # Populate MongoDB with mock data
    mongo_collection.drop()  # Clear existing data
    mongo_collection.insert_many(mock_flights)

    # Populate PostgreSQL with mock data
    postgres_cursor.execute("DROP TABLE IF EXISTS flights")
    postgres_cursor.execute("""
        CREATE TABLE flights (
            id SERIAL PRIMARY KEY,
            airline VARCHAR(255),
            flight_number VARCHAR(255),
            status VARCHAR(255),
            gate VARCHAR(255)
        )
    """)
    for flight in mock_flights:
        postgres_cursor.execute(
            "INSERT INTO flights (airline, flight_number, status, gate) VALUES (%s, %s, %s, %s)",
            (flight['airline'], flight['flight_number'], flight['status'], flight['gate'])
        )
    postgres_conn.commit()

    return jsonify({"message": "Mock data populated"}), 200

# Simulate updating flight status randomly
@app.route('/api/update', methods=['POST'])
def update_flight_status():
    statuses = ["On Time", "Delayed", "Cancelled", "Boarding"]
    mongo_flights = list(mongo_collection.find({}, {'_id': 0}))
    for flight in mongo_flights:
        flight['status'] = random.choice(statuses)
        mongo_collection.update_one({'id': flight['id']}, {'$set': {'status': flight['status']}})

    postgres_cursor.execute("SELECT id FROM flights")
    postgres_flights = postgres_cursor.fetchall()
    for flight in postgres_flights:
        new_status = random.choice(statuses)
        postgres_cursor.execute(
            "UPDATE flights SET status = %s WHERE id = %s",
            (new_status, flight[0])
        )
    postgres_conn.commit()

    return jsonify({"message": "Flight status updated"}), 200

if _name_ == '_main_':
    app.run(debug=True)