#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define mq2Pin      35
#define flamePin    36
#define dhtPin      14
#define buzzerPin   27

#define DHTTYPE DHT22
DHT dht(dhtPin, DHTTYPE);

// WiFi
const char* ssid = "WikWek";
const char* password = "11334455";

// Server
const char* serverURL = "http://192.168.134.160:8080/api/sensor";

// Timer
unsigned long lastReadTime = 0;
const unsigned long readInterval = 5000;
unsigned long waktuMulai = 0;
const unsigned long tundaAwal = 10000;
bool siapBaca = false;

// Data
int gasValue = 0;
int flameState = HIGH;
float suhu = 0.0, kelembapan = 0.0;

// === Fuzzy Membership Functions ===
float gasRendah(int x) {
  if (x <= 1000) return 1.0;
  else if (x >= 1500) return 0.0;
  else return (1500.0 - x) / 500.0;
}

float gasSedang(int x) {
  if (x <= 1000 || x >= 2500) return 0.0;
  else if (x <= 1500) return (x - 1000.0) / 500.0;
  else if (x <= 2000) return 1.0;
  else return (2500.0 - x) / 500.0;
}

float gasTinggi(int x) {
  if (x <= 2000) return 0.0;
  else if (x >= 3000) return 1.0;
  else return (x - 2000.0) / 1000.0;
}

float suhuRendah(float x) {
  if (x <= 28.0) return 1.0;
  else if (x >= 32.0) return 0.0;
  else return (32.0 - x) / 4.0;
}

float suhuSedang(float x) {
  if (x <= 28.0 || x >= 38.0) return 0.0;
  else if (x <= 32.0) return (x - 28.0) / 4.0;
  else if (x <= 34.0) return 1.0;
  else return (38.0 - x) / 4.0;
}

float suhuTinggi(float x) {
  if (x <= 34.0) return 0.0;
  else if (x >= 40.0) return 1.0;
  else return (x - 34.0) / 6.0;
}

float apiAda(int flameDigital) {
  return (flameDigital == LOW) ? 1.0 : 0.0;
}

float apiTidakAda(int flameDigital) {
  return (flameDigital == HIGH) ? 1.0 : 0.0;
}

// === Fuzzy Inference System dengan Weighted Average ===
float fuzzyInference(float gasLow, float gasMed, float gasHigh, 
                    float suhuLow, float suhuMed, float suhuHigh, 
                    float apiYes, float apiNo) {
  
  // Definisi Rules dengan Weighted Average Method
  // Rule 1: IF Gas Rendah AND Suhu Rendah AND Api Tidak Ada THEN Bahaya Rendah (20)
  float rule1 = min(min(gasLow, suhuLow), apiNo);
  float output1 = 20.0;
  
  // Rule 2: IF Gas Sedang AND Suhu Rendah AND Api Tidak Ada THEN Bahaya Rendah (25)
  float rule2 = min(min(gasMed, suhuLow), apiNo);
  float output2 = 25.0;
  
  // Rule 3: IF Gas Rendah AND Suhu Sedang AND Api Tidak Ada THEN Bahaya Rendah (30)
  float rule3 = min(min(gasLow, suhuMed), apiNo);
  float output3 = 30.0;
  
  // Rule 4: IF Gas Sedang AND Suhu Sedang AND Api Tidak Ada THEN Bahaya Sedang (45)
  float rule4 = min(min(gasMed, suhuMed), apiNo);
  float output4 = 45.0;
  
  // Rule 5: IF Gas Tinggi AND Suhu Rendah AND Api Tidak Ada THEN Bahaya Sedang (55)
  float rule5 = min(min(gasHigh, suhuLow), apiNo);
  float output5 = 55.0;
  
  // Rule 6: IF Gas Rendah AND Suhu Tinggi AND Api Tidak Ada THEN Bahaya Sedang (50)
  float rule6 = min(min(gasLow, suhuHigh), apiNo);
  float output6 = 50.0;
  
  // Rule 7: IF Gas Sedang AND Suhu Tinggi AND Api Tidak Ada THEN Bahaya Tinggi (65)
  float rule7 = min(min(gasMed, suhuHigh), apiNo);
  float output7 = 65.0;
  
  // Rule 8: IF Gas Tinggi AND Suhu Sedang AND Api Tidak Ada THEN Bahaya Tinggi (70)
  float rule8 = min(min(gasHigh, suhuMed), apiNo);
  float output8 = 70.0;
  
  // Rule 9: IF Gas Tinggi AND Suhu Tinggi AND Api Tidak Ada THEN Bahaya Tinggi (75)
  float rule9 = min(min(gasHigh, suhuHigh), apiNo);
  float output9 = 75.0;
  
  // Rules dengan Api Terdeteksi - Prioritas Bahaya Tinggi
  // Rule 10: IF Api Ada THEN Bahaya Tinggi (85) - tidak peduli gas dan suhu
  float rule10 = apiYes;
  float output10 = 85.0;
  
  // Rule 11: IF Gas Tinggi AND Api Ada THEN Bahaya Sangat Tinggi (95)
  float rule11 = min(gasHigh, apiYes);
  float output11 = 95.0;
  
  // Rule 12: IF Suhu Tinggi AND Api Ada THEN Bahaya Sangat Tinggi (90)
  float rule12 = min(suhuHigh, apiYes);
  float output12 = 90.0;
  
  // Rule 13: IF Gas Tinggi AND Suhu Tinggi AND Api Ada THEN Bahaya Maksimal (100)
  float rule13 = min(min(gasHigh, suhuHigh), apiYes);
  float output13 = 100.0;
  
  // Weighted Average Defuzzification
  float numerator = (rule1 * output1) + (rule2 * output2) + (rule3 * output3) + 
                   (rule4 * output4) + (rule5 * output5) + (rule6 * output6) + 
                   (rule7 * output7) + (rule8 * output8) + (rule9 * output9) + 
                   (rule10 * output10) + (rule11 * output11) + (rule12 * output12) + 
                   (rule13 * output13);
                   
  float denominator = rule1 + rule2 + rule3 + rule4 + rule5 + rule6 + 
                     rule7 + rule8 + rule9 + rule10 + rule11 + rule12 + rule13;
  
  // Cegah pembagian dengan nol
  if (denominator == 0.0) {
    return 0.0;
  }
  
  return numerator / denominator;
}

void setup() {
  Serial.begin(115200);
  pinMode(flamePin, INPUT_PULLUP);
  pinMode(mq2Pin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  dht.begin();

  // Optional: Aktifkan WiFi jika ingin kirim ke server

  WiFi.begin(ssid, password);
  Serial.print("🔌 Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Terhubung ke WiFi!");

  waktuMulai = millis();
}

void loop() {
  if (millis() - lastReadTime >= readInterval) {
    lastReadTime = millis();

    if (!siapBaca && millis() - waktuMulai >= tundaAwal) {
      siapBaca = true;
      Serial.println("✅ Sensor sudah stabil. Mulai membaca dan mengirim data jika bahaya.");
    }

    if (!siapBaca) {
      // Saat belum siap baca, nilai dianggap nol
      gasValue = 0;
      flameState = HIGH;
      suhu = 0.0;
      kelembapan = 0.0;

      digitalWrite(buzzerPin, LOW); // buzzer tidak bunyi

      Serial.println("⏳ Menunggu stabil... Nilai sensor sementara diabaikan.");
      Serial.println("Gas: 0, Suhu: 0.0°C, Kelembapan: 0.0%, Api: Tidak Ada");
      Serial.println("=========================");
      return; // Keluar dari loop agar tidak lanjut fuzzy & kirim data
    }

    // Baca sensor setelah siap
    gasValue = analogRead(mq2Pin);
    flameState = digitalRead(flamePin);
    suhu = dht.readTemperature();
    kelembapan = dht.readHumidity();

    if (isnan(suhu) || isnan(kelembapan)) {
      Serial.println("❌ Gagal membaca DHT22!");
      return;
    }

    // Hitung membership functions
    float gasLow = gasRendah(gasValue);
    float gasMed = gasSedang(gasValue);
    float gasHigh = gasTinggi(gasValue);

    float suhuLow = suhuRendah(suhu);
    float suhuMed = suhuSedang(suhu);
    float suhuHigh = suhuTinggi(suhu);

    float apiYes = apiAda(flameState);
    float apiNo = apiTidakAda(flameState);

    // Jalankan Fuzzy Inference System
    float hasilFuzzy = fuzzyInference(gasLow, gasMed, gasHigh, 
                                     suhuLow, suhuMed, suhuHigh, 
                                     apiYes, apiNo);

    // Tentukan status bahaya berdasarkan hasil fuzzy
    String statusBahaya = "Aman";
    bool kondisiBahaya = false;

    if (hasilFuzzy >= 80.0) {
      statusBahaya = "Bahaya Sangat Tinggi";
      kondisiBahaya = true;
    } else if (hasilFuzzy >= 60.0) {
      statusBahaya = "Bahaya Tinggi";
      kondisiBahaya = true;
    } else if (hasilFuzzy >= 40.0) {
      statusBahaya = "Bahaya Sedang";
      kondisiBahaya = true;
    } else if (hasilFuzzy >= 25.0) {
      statusBahaya = "Waspada";
      kondisiBahaya = false;
    } else {
      statusBahaya = "Aman";
      kondisiBahaya = false;
    }

    // Aktifkan buzzer jika kondisi bahaya
    digitalWrite(buzzerPin, (kondisiBahaya) ? HIGH : LOW);

    // 🖨️ Tampilkan data ke Serial Monitor
    Serial.println("=== Sensor Update ===");
    Serial.print("Gas: "); Serial.println(gasValue);
    Serial.print("Suhu: "); Serial.print(suhu); Serial.println("°C");
    Serial.print("Kelembapan: "); Serial.print(kelembapan); Serial.println(" %");
    Serial.print("Api: "); Serial.println((apiYes == 1.0) ? "🔥 Terdeteksi" : "✅ Tidak Ada");
    Serial.print("Nilai Fuzzy: "); Serial.println(hasilFuzzy);
    Serial.print("Status: "); Serial.println(statusBahaya);
    Serial.println("=====================");

    // Debug fuzzy membership values
    Serial.println("--- Fuzzy Membership ---");
    Serial.printf("Gas - Rendah:%.2f, Sedang:%.2f, Tinggi:%.2f\n", gasLow, gasMed, gasHigh);
    Serial.printf("Suhu - Rendah:%.2f, Sedang:%.2f, Tinggi:%.2f\n", suhuLow, suhuMed, suhuHigh);
    Serial.printf("Api - Ada:%.2f, Tidak Ada:%.2f\n", apiYes, apiNo);
    Serial.println("------------------------");

    // 💾 Kirim ke server jika kondisi bahaya
    if (kondisiBahaya && WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverURL);
      http.addHeader("Content-Type", "application/json");

      String jsonData = "{\"gas\":";
      jsonData += gasValue;
      jsonData += ",\"suhu\":";
      jsonData += suhu;
      jsonData += ",\"kelembapan\":";
      jsonData += kelembapan;
      jsonData += ",\"api\":";
      jsonData += ((apiYes == 1.0) ? "true" : "false");
      jsonData += ",\"nilai_fuzzy\":";
      jsonData += hasilFuzzy;
      jsonData += ",\"status_bahaya\":\"";
      jsonData += statusBahaya;
      jsonData += "\"}";

      int code = http.POST(jsonData);
      if (code > 0) {
        Serial.print("📤 Data kondisi bahaya terkirim! Response code: ");
        Serial.println(code);
      } else {
        Serial.print("❌ Gagal kirim. Error: ");
        Serial.println(http.errorToString(code));
      }
      http.end();
    }
  }
}