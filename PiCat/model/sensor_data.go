package model

import "time"

type SensorData struct {
	ID           uint    `gorm:"primaryKey"`
	Gas          int     `json:"gas"`
	Suhu         float64 `json:"suhu"`
	Kelembapan   float64 `json:"kelembapan"`
	Api          bool    `json:"api"`
	StatusBahaya string  `json:"status_bahaya"`
	CreatedAt    time.Time
}
