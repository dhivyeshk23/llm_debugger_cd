void setup() {
  pinMode(2, OUTPUT); // Syntax error → RED
  pinMode(3, OUTPUT); // Semantic error → YELLOW
  pinMode(4, OUTPUT); // Runtime error → BLUE
  pinMode(5, OUTPUT); // Success → GREEN

  Serial.begin(9600);
}

void turnOffAll() {
  digitalWrite(2, LOW);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
}

void loop() {
  if (Serial.available()) {
    char code = Serial.read();
    turnOffAll();

    if (code == 'S') { digitalWrite(5, HIGH); }   // Success
    if (code == 'X') { digitalWrite(2, HIGH); }   // Syntax Error
    if (code == 'M') { digitalWrite(3, HIGH); }   // Semantic Error
    if (code == 'R') { digitalWrite(4, HIGH); }   // Runtime Error
  }
}
