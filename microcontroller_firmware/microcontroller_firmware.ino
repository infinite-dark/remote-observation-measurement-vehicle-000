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
uint8_t s_buffer[3];

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

void steerToTarget(int target) {

}

void steer() {
  uint8_t dir = (s_buffer[0] >> 2) & STEERING_DIRECTION_MASK;
  uint8_t angle = s_buffer[1];

  int target;

  switch (dir) {
    case DIRECTION_CENTER:
      target = POSITION_CENTER;
      break;
    case DIRECTION_RIGHT:
      steerRight();
      break;
    case DIRECTION_LEFT:
      steerLeft();
    default:
      break;
  }
}

void driveForward() {
  digitalWrite(DRIVE_DIRECTION_PIN, LOW);
}

void driveReverse() {
  digitalWrite(DRIVE_DIRECTION_PIN, HIGH);
}

void drive() {

}


void setup() {
  pinMode(STEERING_PIN_IA1, OUTPUT);
  pinMode(STEERING_PIN_IA2, OUTPUT);

  pinMode(DRIVE_DIRECTION_PIN, OUTPUT);
  pinMode(DRIVE_SPEED_PIN, OUTPUT);

  hw_serial.begin(115200);
}

void loop() {
  if (hw_serial.available() == 3) {
    hw_serial.readBytes(s_buffer, 3);
  }
}

