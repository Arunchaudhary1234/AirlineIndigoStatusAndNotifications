import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FlightStatus.css';

const FlightStatus = () => {
  const [flights, setFlights] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFlightStatus = async () => {
      try {
        const response = await axios.get('/api/flights'); // Update with actual backend endpoint
        setFlights(response.data);
      } catch (err) {
        setError('Error fetching flight status');
      }
    };

    fetchFlightStatus();
    const intervalId = setInterval(fetchFlightStatus, 60000); // Poll every 60 seconds

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="flight-status-container">
      <h1>Flight Status</h1>
      <table className="flight-status-table">
        <thead>
          <tr>
            <th>Airline</th>
            <th>Flight Number</th>
            <th>Status</th>
            <th>Gate</th>
          </tr>
        </thead>
        <tbody>
          {flights.map((flight) => (
            <tr key={flight.id}>
              <td>{flight.airline}</td>
              <td>{flight.flight_number}</td>
              <td>{flight.status}</td>
              <td>{flight.gate}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FlightStatus;