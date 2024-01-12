//---------------OUTPUTS---------------//

#define STEERING_PIN_IA1 PB6
#define STEERING_PIN_IA2 PB1

#define DRIVE_DIRECTION_PIN PB7
#define DRIVE_SPEED_PIN PB0

//---------------INPUTS---------------//

#define STEERING_ANGLE_SENSOR_PIN PA2
#define BATTERY_VOLTAGE_LEVEL_PIN PA7

//---------------SERIAL---------------//

#define STEERING_DIRECTION_MASK 0b00001100
#define DRIVE_DIRECTION_MASK 0b00000011

#define RX PA10
#define TX PA9

HardwareSerial hw_serial = HardwareSerial(RX, TX);
uint8_t s_buffer[3] = { 0 };

//---------------STEERING---------------//

#define DIRECTION_CENTER 0b00000000
#define DIRECTION_RIGHT 0b00000100
#define DIRECTION_LEFT 0b00001000

#define POSITION_CENTER 382
#define POSITION_RIGHT 29
#define POSITION_LEFT 681
#define POSITION_INACCURACY 20

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
  uint8_t dir = (s_buffer[0] >> 2) & STEERING_DIRECTION_MASK;
  uint8_t turn = s_buffer[1];

  int position = analogRead(STEERING_ANGLE_SENSOR_PIN);
  int target, delta;

  switch (dir) {
    case DIRECTION_CENTER:
      target = POSITION_CENTER;
      break;
    case DIRECTION_RIGHT:
      target = POSITION_CENTER - turn/100.0 * (POSITION_CENTER - POSITION_RIGHT);
      break;
    case DIRECTION_LEFT:
      target = POSITION_CENTER + turn/100.0 * (POSITION_LEFT - POSITION_CENTER);
    default:
      target = position;
      break;
  }

  delta = position - target;

  if (abs(delta) > POSITION_INACCURACY) {
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

//---------------DRIVE---------------//

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

//---------------FUNCTIONALITY---------------//

void receiveCommands() {
  if (hw_serial.available() == 3) {
    hw_serial.readBytes(s_buffer, 3);
  }
}

void setup() {
  pinMode(STEERING_PIN_IA1, OUTPUT);
  pinMode(STEERING_PIN_IA2, OUTPUT);

  pinMode(DRIVE_DIRECTION_PIN, OUTPUT);
  pinMode(DRIVE_SPEED_PIN, OUTPUT);

  hw_serial.begin(115200);
}

void loop() {
  receiveCommands();
  steer();
  drive();
}
