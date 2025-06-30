CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    gas INTEGER,
    suhu FLOAT,
    kelembapan FLOAT,
    api BOOLEAN,
    status_bahaya VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
