import time

from dot3k.menu import MenuOption

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)


class Myclock(MenuOption):
    def __init__(self, backlight=None):
        self.modes = ['date', 'week', 'binary', 'day', 'night']
        self.mode = 0
        self.binary = True
        self.running = False

        self.option_time = 0

        self.day_hour = 20
        self.night_hour = 8

        self.is_setup = False

        MenuOption.__init__(self)

    def begin(self):
        self.is_setup = False
        self.running = True

    def setup(self, config):
        MenuOption.setup(self, config)
        self.load_options()

    def update_options(self):
        self.set_option('myclock', 'day', str(self.day_hour))
        self.set_option('myclock', 'night', str(self.night_hour))
        self.set_option('myclock', 'binary', str(self.binary))

    def load_options(self):
        self.day_hour = int(self.get_option('myclock', 'day', str(self.day_hour)))
        self.night_hour = int(self.get_option('myclock', 'night', str(self.night_hour)))
        self.binary = self.get_option('myclock', 'binary', str(self.binary)) == 'True'

    def cleanup(self):
        self.running = False
        time.sleep(0.01)
        self.set_backlight(1.0)
        self.is_setup = False

    def left(self):
        if self.modes[self.mode] == 'binary':
            self.binary = False
        elif self.modes[self.mode] == 'day':
            self.day_hour = (self.day_hour - 1) % 24
        elif self.modes[self.mode] == 'night':
            self.night_hour = (self.night_hour - 1) % 24
        else:
            return False
        self.update_options()
        self.option_time = self.millis()
        return True

    def right(self):
        if self.modes[self.mode] == 'binary':
            self.binary = True
        elif self.modes[self.mode] == 'day':
            self.day_hour = (self.day_hour + 1) % 24
        elif self.modes[self.mode] == 'night':
            self.night_hour = (self.night_hour + 1) % 24
        self.update_options()
        self.option_time = self.millis()
        return True

    def up(self):
        self.mode = (self.mode - 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def down(self):
        self.mode = (self.mode + 1) % len(self.modes)
        self.option_time = self.millis()
        return True

    def daylights_on(self):
        GPIO.output(13,0)
        GPIO.output(5,1)
        GPIO.output(13,1)

    def nightlights_off(self):
        GPIO.output(13,0)
        GPIO.output(5,1)
        GPIO.output(13,0)

    def redraw(self, menu):
        if not self.running:
            return False

        if self.millis() - self.option_time > 5000 and self.option_time > 0:
            self.option_time = 0
            self.mode = 0

        if not self.is_setup:
            menu.lcd.create_char(0, [0, 0, 0, 14, 17, 17, 14, 0])
            menu.lcd.create_char(1, [0, 0, 0, 14, 31, 31, 14, 0])
            menu.lcd.create_char(2, [0, 14, 17, 17, 17, 14, 0, 0])
            menu.lcd.create_char(3, [0, 14, 31, 31, 31, 14, 0, 0])
            menu.lcd.create_char(4, [0, 4, 14, 0, 0, 14, 4, 0])  # Up down arrow
            menu.lcd.create_char(5, [0, 0, 10, 27, 10, 0, 0, 0])  # Left right arrow
            self.is_setup = True

        hour = float(time.strftime('%H'))
        brightness = 1.0
        if self.day_hour == True:
            self.daylights_on()
        elif self.night_hour == True:
            self.nightlights_off()

        menu.write_row(0, time.strftime('  %a %H:%M:%S  '))


        if self.binary:
            binary_hour = str(bin(int(time.strftime('%I'))))[2:].zfill(4).replace('0', chr(0)).replace('1', chr(1))
            binary_min = str(bin(int(time.strftime('%M'))))[2:].zfill(6).replace('0', chr(2)).replace('1', chr(3))
            binary_sec = str(bin(int(time.strftime('%S'))))[2:].zfill(6).replace('0', chr(0)).replace('1', chr(1))
            menu.write_row(1, binary_hour + binary_min + binary_sec)
        else:
            menu.write_row(1, '-' * 16)

        if self.idling:
            menu.clear_row(2)
            return True

        bottom_row = ''

        if self.modes[self.mode] == 'date':
            bottom_row = time.strftime('%b %Y:%m:%d ')
        elif self.modes[self.mode] == 'week':
            bottom_row = time.strftime('   Week: %W')
        elif self.modes[self.mode] == 'binary':
            bottom_row = ' Binary ' + chr(5) + ('Y' if self.binary else 'N')
        elif self.modes[self.mode] == 'day':
            bottom_row = ' day at ' + chr(5) + str(self.day_hour).zfill(2)
        elif self.modes[self.mode] == 'night':
            bottom_row = ' night at ' + chr(5) + str(self.night_hour).zfill(2)

        menu.write_row(2, chr(4) + bottom_row)
