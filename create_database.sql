-- Create a new SQLite database
CREATE TABLE IF NOT EXISTS SensorData (
    uptime INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    accel_x REAL,
    accel_y REAL,
    accel_z REAL,
    force REAL
);

-- Example of inserting a record
INSERT INTO SensorData (accel_x, accel_y, accel_z, force) VALUES (1.0, 0.5, -0.5, 10.0);

-- Example of querying the database
SELECT * FROM SensorData;
