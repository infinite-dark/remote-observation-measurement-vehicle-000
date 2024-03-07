#define STEERING_PIN_IA1 PA9
#define STEERING_PIN_IA2 PA10

#define DRIVE_DIRECTION_PIN PB5
#define DRIVE_SPEED_PIN PA11

#define INTERRUPT_PIN PB5

#define STEERING_ANGLE_SENSOR_PIN PA5
#define BATTERY_VOLTAGE_LEVEL_PIN PA0

#define STEERING_DIRECTION_MASK 0b00001100
#define DRIVE_DIRECTION_MASK 0b00000011

#define RX_CMD PA3
#define TX_CMD PA2

#define MINIMUM_BATTERY_ADC_VOLTAGE 753
#define MAXIMUM_BATTERY_ADC_VOLTAGE 856

#define BATTERY_TX_DELAY 500

#define RX_DAT PB7
#define TX_DAT PB6

static uint8_t s_buffer[3] = { 0 };
HardwareSerial cmd_serial = HardwareSerial(RX_CMD, TX_CMD);
HardwareSerial dat_serial = HardwareSerial(RX_DAT, TX_DAT);

#define DIRECTION_CENTER 0b00000000
#define DIRECTION_RIGHT 0b00000100
#define DIRECTION_LEFT 0b00001000

#define POSITION_CENTER 245
#define POSITION_RIGHT 0
#define POSITION_LEFT 473
#define POSITION_READOUT_MARGIN 30

void steerRight() {
  digitalWrite(STEERING_PIN_IA1, HIGH);
  digitalWrite(STEERING_PIN_IA2, LOW);
}

void steerLeft() {
  digitalWrite(STEERING_PIN_IA1, LOW);
  digitalWrite(STEERING_PIN_IA2, HIGH);
}

void steerStop() {
  digitalWrite(STEERING_PIN_IA1, LOW);
  digitalWrite(STEERING_PIN_IA2, LOW);
}

void steer() {
  uint8_t dir = s_buffer[0] & STEERING_DIRECTION_MASK;
  uint8_t turn = s_buffer[1];

  int position = analogRead(STEERING_ANGLE_SENSOR_PIN);
  int target{0}, delta{0};

  switch (dir) {
    case DIRECTION_CENTER:
      target = POSITION_CENTER;
      break;
    case DIRECTION_RIGHT:
      target = POSITION_CENTER - turn/100.0 * (POSITION_CENTER - POSITION_RIGHT);
      break;
    case DIRECTION_LEFT:
      target = POSITION_CENTER + turn/100.0 * (POSITION_LEFT - POSITION_CENTER);
      break;
    default:
      target = position;
      break;
  }

  delta = position - target;

  if (abs(delta) > POSITION_READOUT_MARGIN) {
    if (delta >= 0) {
      steerRight();
    }
    else {
      steerLeft();
    }
  }
  else {
    steerStop();
  }
}

#define DRIVE_DIRECTION_FORWARD 0b00000010
#define DRIVE_DIRECTION_REVERSE 0b00000001
#define DRIVE_DIRECTION_STOP 0b00000000

void driveForward() {
  digitalWrite(DRIVE_DIRECTION_PIN, LOW);
}

void driveReverse() {
  digitalWrite(DRIVE_DIRECTION_PIN, HIGH);
}

void driveStop() {
  digitalWrite(DRIVE_SPEED_PIN, LOW);
}

void drive() {
  uint8_t dir = s_buffer[0] & DRIVE_DIRECTION_MASK;
  uint8_t speed = s_buffer[2] / 100.0 * 255;

  switch (dir) {
    case DRIVE_DIRECTION_FORWARD:
      driveForward();
      break;
    case DRIVE_DIRECTION_REVERSE:
      driveReverse();
      break;
    case DRIVE_DIRECTION_STOP:
      driveStop();
      break;
    default:
      driveStop();
      break;
  }

  analogWrite(DRIVE_SPEED_PIN, speed);
}

float readBattery() {
  return 100.0 * (analogRead(BATTERY_VOLTAGE_LEVEL_PIN) - MINIMUM_BATTERY_ADC_VOLTAGE) / (MAXIMUM_BATTERY_ADC_VOLTAGE - MINIMUM_BATTERY_ADC_VOLTAGE);
}

unsigned long int prevRXtime{0}, lastRXtime{0};
unsigned long int prevTXtime{0}, lastTXtime{0};

bool keep_driving = true;

void talk() {
  if (cmd_serial.available() >= 3) {
    cmd_serial.readBytes(s_buffer, 3);

    prevRXtime = lastRXtime;
    lastRXtime = millis();
  }

  if (millis() - lastRXtime > 1000 || s_buffer[0] & 0b10000000) {
    keep_driving = false;
  }
  else {
    keep_driving = true;
  }

  if (millis() - lastTXtime > BATTERY_TX_DELAY) {
    float battery_percentage = readBattery();
    dat_serial.println((int)battery_percentage);
    prevTXtime = lastTXtime;
    lastTXtime = millis();
  }
}

void setup() {
  pinMode(STEERING_PIN_IA1, OUTPUT);
  pinMode(STEERING_PIN_IA2, OUTPUT);

  pinMode(DRIVE_DIRECTION_PIN, OUTPUT);
  pinMode(DRIVE_SPEED_PIN, OUTPUT);

  cmd_serial.begin(115200);
  dat_serial.begin(115200);
}

void loop() {
  talk();
  if (keep_driving){
    drive();
    steer();
  }
  else {
    driveStop();
    steerStop();
  }
}
