import sys
import time

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from dot3k.menu import Menu, MenuOption
from time import sleep


sys.path.append ('/usr/local/lib/python2.7/dist-packages')
sys.path.append('/home/pi/Pimoroni/displayotron/examples')
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
sys.path.append('/home/pi/Aquarium/')

from Myclock import Myclock
from plugins.clock import Clock
from plugins.graph import IPAddress, GraphTemp, GraphCPU, GraphNetSpeed, GraphSysReboot, GraphSysShutdown
from plugins.text import Text
from plugins.utils import Backlight, Contrast

class Lights(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)


#Unordered menu
menu = Menu(
    structure={
            'Power Options': {
                'Reboot':GraphSysReboot(),
                'Shutdown':GraphSysShutdown(),
                },
            'Aquarium': {
                'Lighting': {
                    'Control': Myclock(),
                    }
                },
        'Clock': Clock(backlight),
        'Status': {
            'IP': IPAddress(),
            'CPU': GraphCPU(backlight),
            'Temp': GraphTemp()
        },
        'Settings': {
            'Display': {
                'Contrast': Contrast(lcd),
                'Backlight': Backlight(backlight)
            }
        }
    },
    lcd=lcd,
    
    input_handler=Text())

nav.bind_defaults(menu)

while True:

    menu.redraw()
    time.sleep(1.0 / 20)

