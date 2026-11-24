
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

// TFT
#define TFT_CS    5
#define TFT_DC    16
#define TFT_RST   17

// Joystick
#define JOY_SW    25

// Mikrofon
#define MIC_PIN   32

// Audio-Einstellungen
#define SAMPLE_RATE 4000
#define MAX_SECONDS 10
#define MAX_SAMPLES (SAMPLE_RATE * MAX_SECONDS)

// 8 Bit pro Sample
uint8_t audio[MAX_SAMPLES];

Adafruit_ST7735 tft(TFT_CS, TFT_DC, TFT_RST);

void showText(String text) {
  tft.fillScreen(ST77XX_BLACK);
  tft.setCursor(3, 5);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(1);
  tft.setTextWrap(true);
  tft.println(text);
}

void waitForRelease() {
  while (digitalRead(JOY_SW) == LOW) {
    delay(5);
  }
  delay(30);
}

uint32_t recordAudio() {
  showText("AUFNAHME...\n\nKlicken zum Beenden");

  uint32_t count = 0;
  const uint32_t interval = 1000000UL / SAMPLE_RATE;

  while (count < MAX_SAMPLES) {
    uint32_t start = micros();

    // ADC: 12 Bit auf 8 Bit reduzieren
    audio[count++] = analogRead(MIC_PIN) >> 4;

    while ((uint32_t)(micros() - start) < interval) {
    }

    if (count % 40 == 0 && digitalRead(JOY_SW) == LOW) {
      delay(30);

      if (digitalRead(JOY_SW) == LOW) {
        waitForRelease();
        break;
      }
    }
  }

  return count;
}

void sendAudio(uint32_t count) {
  showText("SENDE AUDIO...");

  Serial.write((const uint8_t*)"AUD1", 4);

  // Sample-Anzahl
  Serial.write((uint8_t*)&count, 4);

  // Audio übertragen
  Serial.write(audio, count);

  Serial.flush();
}

void receiveText() {
  showText("WARTE AUF PYTHON...");

  String response = Serial.readStringUntil('\n');
  response.trim();

  if (response.startsWith("TEXT:")) {
    showText("ERKANNT:\n\n" + response.substring(5));
  } else {
    showText("FEHLER:\n" + response);
  }
}

void setup() {
  Serial.begin(460800);
  Serial.setTimeout(30000);

  pinMode(JOY_SW, INPUT_PULLUP);

  analogReadResolution(12);
  analogSetPinAttenuation(MIC_PIN, ADC_11db);

  tft.initR(INITR_BLACKTAB);
  tft.setRotation(1);

  showText("SPRACHASSISTENT\n\nJoystick klicken");
}

void loop() {
  if (digitalRead(JOY_SW) == LOW) {
    delay(30);

    if (digitalRead(JOY_SW) == LOW) {
      waitForRelease();

      uint32_t count = recordAudio();

      sendAudio(count);

      receiveText();

      delay(2000);

      showText("BEREIT\n\nJoystick klicken");
    }
  }

  delay(5);
}
