# Pins
| ESP32 | Bauteil | Pin-Bezeichnung |
|---|---|---|
| GPIO 5 | TFT-Display | CS |
| GPIO 16 | TFT-Display | DC / A0 |
| GPIO 17 | TFT-Display | RST / RESET |
| GPIO 18 | TFT-Display | SCL / SCK |
| GPIO 23 | TFT-Display | SDA / MOSI |
| GPIO 25 | Joystick | SW |
| GPIO 34 | Joystick | VRy |
| GPIO 35 | Joystick | VRx |
| GPIO 32 | GY-MAX4466 Mikrofon | OUT |
| 3V3 | TFT-Display | VCC |
| 3V3 | Joystick | VCC |
| 3V3 | GY-MAX4466 Mikrofon | VCC |
| GND | TFT-Display | GND |
| GND | Joystick | GND |
| GND | GY-MAX4466 Mikrofon | GND |

# Arduino
```
// TFT Display ST7735
#define TFT_CS    5
#define TFT_DC    16
#define TFT_RST   17
#define TFT_SCLK  18
#define TFT_MOSI  23

// Joystick
#define JOY_SW    25
#define JOY_VRY   34
#define JOY_VRX   35

// Mikrofon GY-MAX4466
#define MIC_PIN   32
```