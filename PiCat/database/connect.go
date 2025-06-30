// database/connect.go
package database

import (
	"fmt"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func ConnectDB() {
	dsn := "host=localhost user=danil password=@danil123 dbname=esp32db port=2685 sslmode=disable"
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		panic("❌ Gagal koneksi ke database")
	}
	DB = db
	fmt.Println("✅ Terkoneksi ke PostgreSQL")
}
