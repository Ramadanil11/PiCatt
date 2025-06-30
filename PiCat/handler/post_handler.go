package handler

import (
	"PiCat/database"
	"PiCat/model"
	"net/http"

	"github.com/gin-gonic/gin"
)

func PostSensorData(c *gin.Context) {
	var data model.SensorData

	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Format JSON salah"})
		return
	}

	if data.Gas < 2000 {
		c.JSON(http.StatusOK, gin.H{"message": "✅ Gas aman, data tidak disimpan"})
		return
	}

	if err := database.DB.Create(&data).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "❌ Gagal simpan ke database"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "🔥 Gas tinggi, data disimpan",
		"data":    data,
	})
}
