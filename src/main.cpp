#include <Arduino.h>
#include <LiquidCrystal.h>

// Pin config
#define TRIG_PIN       5
#define ECHO_PIN       15
#define GREEN_LED_PIN  25
#define YELLOW_LED_PIN 26
#define RED_LED_PIN    32
#define BUTTON_PIN     4

// LCD: RS, EN, D4, D5, D6, D7
LiquidCrystal lcd(19, 23, 13, 12, 14, 27);

//Timing 
unsigned long previousMillis      = 0;
const unsigned long interval      = 500;
unsigned long lastDebounceTime    = 0;
const unsigned long debounceDelay = 50;
unsigned long lastLCDUpdate       = 0;
const unsigned long lcdInterval   = 2000;
unsigned long lastBatteryUpdate   = 0;
const unsigned long batteryInterval = 30000;

//  States
enum SystemState { SYSTEM_ON, SYSTEM_OFF };
SystemState systemState = SYSTEM_ON;
bool justToggled  = false;
bool screenToggle = false;

// Button 
int lastButtonState = HIGH;
int buttonPressed   = HIGH;

// Sensor data 
float lastDistance  = 0;
String lastZone     = "--";
int batteryLevel    = 100;

// Forward declarations 
void allLedsOff();
void toggleState();
void runState();
void displayOffScreen();
void displayScreen1();
void displayScreen2();
void printBattery();

void allLedsOff() {
  digitalWrite(GREEN_LED_PIN,  LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN,    LOW);
}


void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN,       OUTPUT);
  pinMode(ECHO_PIN,       INPUT);
  pinMode(GREEN_LED_PIN,  OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN,    OUTPUT);
  pinMode(BUTTON_PIN,     INPUT_PULLUP);

  lcd.begin(16, 2);
  displayScreen1();

  Serial.println(">> Smart Proximity Alert System START");
  lcd.setCursor(0, 0);
  lcd.print("Hello World!");
  lcd.setCursor(0, 1);
  lcd.print("LCD Test OK");
  
  delay(3000);  // hold for 3 seconds
  
}


void loop() {
  unsigned long currentMillis = millis();

  //Button debounce
  int reading = digitalRead(BUTTON_PIN);
  if (reading != lastButtonState) {
    lastDebounceTime = currentMillis;
  }
  if ((currentMillis - lastDebounceTime) > debounceDelay) {
    if (reading != buttonPressed) {
      buttonPressed = reading;
      if (buttonPressed == LOW) {
        Serial.println("Button ok!!");
        toggleState();
      }
    }
  }
  lastButtonState = reading;

  // Battery drain 
  if (currentMillis - lastBatteryUpdate >= batteryInterval) {
    lastBatteryUpdate = currentMillis;
    if (batteryLevel > 0) batteryLevel--;
  }

  
  runState();

  // LCD update
  if (systemState == SYSTEM_ON) {
    if (currentMillis - lastLCDUpdate >= lcdInterval) {
      lastLCDUpdate = currentMillis;
      screenToggle  = !screenToggle;
      if (screenToggle) {
        displayScreen1();
      } else {
        displayScreen2();
      }
    }
  }
}


void toggleState() {
  unsigned long t = millis();
  if (systemState == SYSTEM_OFF) {
    systemState  = SYSTEM_ON;
    justToggled  = true;
    screenToggle = false;
    Serial.print("[t="); Serial.print(t);
    Serial.println("ms] >> System toggled ON");
    displayScreen1();
  } else {
    systemState = SYSTEM_OFF;
    justToggled = true;
    Serial.print("[t="); Serial.print(t);
    Serial.println("ms] >> System toggled OFF");
    displayOffScreen();
  }
}


void runState() {
  switch (systemState) {

    case SYSTEM_OFF: {
      allLedsOff();
      if (justToggled) {
        Serial.println("[SYSTEM OFF]");
        justToggled = false;
      }
      break;
    }

    case SYSTEM_ON: {
      unsigned long currentMillis = millis();

      if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        // Trigger pulse 
        digitalWrite(TRIG_PIN, LOW);
        delayMicroseconds(2);
        digitalWrite(TRIG_PIN, HIGH);
        delayMicroseconds(10);
        digitalWrite(TRIG_PIN, LOW);

        long duration  = pulseIn(ECHO_PIN, HIGH);
        float distance = duration * 0.034 / 2;
        unsigned long t = millis();
        String zone;

        // Zone + LED logic
        if (distance < 2 || distance > 400) {
          allLedsOff();
          zone = "--";
          Serial.print("[t="); Serial.print(t);
          Serial.println("ms] Distance: OUT OF RANGE | Zone: --");

        } else if (distance > 100) {
          allLedsOff();
          digitalWrite(GREEN_LED_PIN, HIGH);
          zone = "SAFE";

        } else if (distance > 40) {
          allLedsOff();
          digitalWrite(YELLOW_LED_PIN, HIGH);
          zone = "WARNING";

        } else {
          allLedsOff();
          digitalWrite(RED_LED_PIN, HIGH);
          zone = "DANGER";
        }

        lastDistance = distance;
        lastZone     = zone;

        // Battery warning
        if (zone != "--") {
          Serial.print("[t="); Serial.print(t);
          Serial.print("ms] Distance: ");
          Serial.print(distance, 1);
          Serial.print("cm | Zone: ");
          Serial.print(zone);
          Serial.print(" | Bat: ");
          Serial.print(batteryLevel);
          Serial.println("%");
        }
      }

      if (justToggled) {
        Serial.println("[SYSTEM ON]");
        justToggled = false;
      }
      break;
    }
  }
}

//  LCD Screens 
void displayOffScreen() {
  lcd.setCursor(0, 0);
  lcd.print("== SYSTEM OFF ==");
  lcd.setCursor(0, 1);
  lcd.print("==============");
}

void displayScreen1() {
  lcd.setCursor(0, 0);
  if (lastZone == "--") {
    lcd.print("Dist: -------   ");
    lcd.setCursor(0, 1);
    lcd.print("Zone: NO SIGNAL ");
  } else {
    lcd.print("Dist:");
    lcd.print(lastDistance, 1);
    lcd.print("cm      ");
    lcd.setCursor(0, 1);
    lcd.print("Zone:");
    lcd.print(lastZone);
    lcd.print("          ");
  }
}

void displayScreen2() {
  lcd.setCursor(0, 0);
  lcd.print("State: ON       ");
  lcd.setCursor(0, 1);
  lcd.print("Bat: ");
  printBattery();
}

void printBattery() {
  lcd.print(batteryLevel);
  lcd.print("%");
  if (batteryLevel < 20) lcd.print("!");
  lcd.print("        ");
}