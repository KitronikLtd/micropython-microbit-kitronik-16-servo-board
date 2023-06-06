# microbit-module: KitronikServoBoard@1.0.0
# Copyright (c) Kitronik Ltd 2022. 
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from microbit import i2c
# the following imports are for the example code at the end of the file
from microbit import sleep, button_a, button_b


class KitronikServoBoard:
    #
    # This class is used to drive the Kitronik 16 Servo add on for microbit
    # www.kitronik.co.uk/5612

    # Some useful parameters

    # In the future there may be several 16 Servo boards
    # all controlled from a single micro:bit
    # In that case extend the functions to include more board addresses
    # or pass an address in a constructor for the object to know.
    BOARD_1 = 0x6A

    # the prescale register address
    PRESCALE_REG = 0xFE

    # The mode 1 register address
    MODE_1_REG = 0x00

    # If you wanted to write some code that stepped through
    # the servos then this is the Base and size to do that
    SERVO_1_REG_BASE = 0x08
    SERVO_REG_DISTANCE = 4

    # To get the PWM pulses to the correct size and zero
    # offset these are the default numbers.
    SERVO_MULTIPLIER = 226
    SERVO_ZERO_OFFSET = 0x66

    class Servos:
        # nice big list of servos to use.
        # These represent register offsets in the PCA9865
        SERVO_1 = 0x08
        SERVO_2 = 0x0C
        SERVO_3 = 0x10
        SERVO_4 = 0x14
        SERVO_5 = 0x18
        SERVO_6 = 0x1C
        SERVO_7 = 0x20
        SERVO_8 = 0x24
        SERVO_9 = 0x28
        SERVO_10 = 0x2C
        SERVO_11 = 0x30
        SERVO_12 = 0x34
        SERVO_13 = 0x38
        SERVO_14 = 0x3C
        SERVO_15 = 0x40
        SERVO_16 = 0x44

    # Trim the servo pulses. These are here for advanced users,
    # It appears that servos I've tested are actually expecting
    # 0.5 - 2.5mS pulses, not the widely reported 1-2mS.
    # that equates to multiplier of 226, and offset of 0x66
    # a better trim function that does the maths for the end
    # user could be written, the basics are here for reference

    def trim_servo_multiplier(self, trim_value):
        if trim_value < 113:
            self.SERVO_MULTIPLIER = 113
        else:
            if trim_value > 226:
                self.SERVO_MULTIPLIER = 226
            else:
                self.SERVO_MULTIPLIER = trim_value

    def trim_servo_zero_offset(self, trim_value):
        if trim_value < 0x66:
            self.SERVO_ZERO_OFFSET = 0x66
        else:
            if (trim_value > 0xCC):
                self.SERVO_ZERO_OFFSET = 0xCC
            else:
                self.SERVO_ZERO_OFFSET = trim_value

    def __init__(self):
        # This secret incantation sets up the PCA9865 I2C driver chip to
        # be running at 50Hz pulse repetition, and then sets the 16 output
        # registers to 1.5mS - centre travel on the servos.
        # It should not need to be called directly be a user -
        # the first servo write will call it.

        buf = bytearray(2)
        # Should really do a soft reset of the I2C chip here
        # First set the prescaler to 50 hz
        buf[0] = self.PRESCALE_REG
        buf[1] = 0x85
        i2c.write(self.BOARD_1, buf, False)
        # Block write via the all leds register to set all of them to 0 deg
        buf[0] = 0xFA
        buf[1] = 0x00
        i2c.write(self.BOARD_1, buf, False)
        buf[0] = 0xFB
        buf[1] = 0x00
        i2c.write(self.BOARD_1, buf, False)
        buf[0] = 0xFC
        buf[1] = 0x66
        i2c.write(self.BOARD_1, buf, False)
        buf[0] = 0xFD
        buf[1] = 0x00
        i2c.write(self.BOARD_1, buf, False)
        # Set the mode 1 register to come out of sleep
        buf[0] = self.MODE_1_REG
        buf[1] = 0x01
        i2c.write(self.BOARD_1, buf, False)

    def servo_write(self, Servo, degrees):
        # @param Servo Which servo to set
        # @param degrees the angle to set the servo to
        buf = bytearray(2)
        HighByte = False
        deg100 = degrees * 100
        PWMVal100 = deg100 * self.SERVO_MULTIPLIER
        PWMVal = PWMVal100 / 10000
        PWMVal = PWMVal + self.SERVO_ZERO_OFFSET
        if (PWMVal > 0xFF):
            HighByte = True
        buf[0] = Servo
        buf[1] = int(PWMVal)
        i2c.write(self.BOARD_1, buf, False)
        if (HighByte):
            buf[0] = Servo + 1
            buf[1] = 0x01
        else:
            buf[0] = Servo + 1
            buf[1] = 0x00
        i2c.write(self.BOARD_1, buf, False)


# Example code which sets a servo to various angles on different button
# presses.
#
# Replace this code with your own

theServoBoard = KitronikServoBoard()
while True:
    if button_a.is_pressed() and button_b.is_pressed():
        theServoBoard.servo_write(KitronikServoBoard.Servos.SERVO_1,
                                  90)
    elif button_a.is_pressed():
        theServoBoard.servo_write(KitronikServoBoard.Servos.SERVO_1,
                                  0)
    elif button_b.is_pressed():
        theServoBoard.servo_write(KitronikServoBoard.Servos.SERVO_1,
                                  180)
    sleep(100)

