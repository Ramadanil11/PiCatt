package main

import (
	"PiCat/database"
	"PiCat/handler"

	"github.com/gin-gonic/gin"
)

func main() {
	database.ConnectDB()
	database.RunMigrations()

	r := gin.Default()
	r.POST("/api/sensor", handler.PostSensorData)
	r.Run(":8080")
}
