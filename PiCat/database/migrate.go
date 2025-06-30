// database/migrate.go
package database

import (
	"fmt"
	"log"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file" // required for file source
)

func RunMigrations() {
	sqlDB, err := DB.DB()
	if err != nil {
		log.Fatalf("Gagal mendapatkan koneksi DB: %v", err)
	}

	driver, err := postgres.WithInstance(sqlDB, &postgres.Config{})
	if err != nil {
		log.Fatalf("Gagal membuat DB driver untuk migrasi: %v", err)
	}

	m, err := migrate.NewWithDatabaseInstance(
		"file://migrations",
		"postgres", driver)
	if err != nil {
		log.Fatalf("Gagal membuat instance migrasi: %v", err)
	}

	if err := m.Up(); err != nil && err.Error() != "no change" {
		log.Fatalf("❌ Gagal menjalankan migrasi: %v", err)
	}

	fmt.Println("✅ Migrasi berhasil dijalankan")
}
