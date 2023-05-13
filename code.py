# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
MacroPad HID keyboard and mouse demo. The demo sends "a" when the first key is pressed, a "B" when
the second key is pressed, "Hello, World!" when the third key is pressed, and decreases the volume
when the fourth key is pressed. It sends a right mouse click when the rotary encoder switch is
pressed. Finally, it moves the mouse left and right when the rotary encoder is rotated
counterclockwise and clockwise respectively.
"""
from adafruit_macropad import MacroPad
from colours import col

macropad = MacroPad()

last_position = 0

COLOUR_RATE = 16
col_tick = 0

IDLE = 0
PRESSED = 1
RELEASED = 2

KEY_REPEAT_THRESHOLD = 20

sign = 1
key_depressed = False
last_key_pressed = 5

def highlight_key(key_number):
    black = (0, 0, 0)
    for p in range(0, 12):
        if p == key_number:
            macropad.pixels[p] = (255, 255, 255)
        else:
            macropad.pixels[p] = black

def voidfunc(val):
    pass

class Status:
    def __init__(self, func = voidfunc, params = []) -> None:
        self.status = IDLE
        self.ticks_pressed = 0
        self.function = func
        self.params = params
        
    def press(self):
        self.status = PRESSED
        
    def release(self):
        self.status = RELEASED
        
    def get(self):
        return self.status
    
    def process(self):
        if (self.status == RELEASED):
            self.ticks_pressed = 0
            self.status = IDLE

        elif self.status == PRESSED:
            if (self.ticks_pressed == 0) or (self.ticks_pressed > KEY_REPEAT_THRESHOLD):
                if len(self.params) > 0:
                    self.function(*self.params)
            self.ticks_pressed += 1
            
        elif self.status == IDLE:
            pass

class pix_status:
    def __init__(self) -> None:
        self.status = ( Status(macropad.keyboard.send, (macropad.Keycode.A,)), \
                        Status(macropad.keyboard_layout.write, ("B",)), \
                        Status(macropad.keyboard_layout.write, ("Hello, World!",)), \
                        Status(macropad.consumer_control.send, (macropad.ConsumerControlCode.VOLUME_DECREMENT,)), \
                        Status(macropad.consumer_control.send, (macropad.ConsumerControlCode.VOLUME_INCREMENT,)), \
                        Status(), \
                        Status(), \
                        Status(), \
                        Status(), \
                        Status(), \
                        Status(), \
                        Status())
        
        self.last_key_pressed = 0
        
    def press_key(self, idx):
        self.status[idx].press()

    def release_key(self, idx):
        self.status[idx].release()
        
    def is_pressed(self, idx):
        if self.status[idx].get() == PRESSED:
            return True
        else:
            return False
         
    def any_pressed(self):
        for i in range(0, 12):
            if self.status[i].get() == PRESSED:
                return True
        return False
    
    def highlight_keys(self):
        for i in range(0, 12):
            if self.status[i].get() == PRESSED:
                macropad.pixels[i] = (255, 255, 255)
            else:
                macropad.pixels[i] = (0, 0, 0)
                
    def process_events(self):
        for i in range(0, 12):
            self.status[i].process()

pixels = pix_status()

class pix_scheme:
        
    def __init__(self, first_col, second_col) -> None:
        self.first = first_col
        self.second = second_col

pixel_colours = (   pix_scheme(col["RED"], col["BLUE"]), pix_scheme(col["RED"], col["GREEN"]), pix_scheme(col["GREEN"], col["BLUE"]), \
                    pix_scheme(col["RED"], col["BLUE"]), pix_scheme(col["RED"], col["GREEN"]), pix_scheme(col["GREEN"], col["BLUE"]), \
                    pix_scheme(col["RED"], col["BLUE"]), pix_scheme(col["RED"], col["GREEN"]), pix_scheme(col["GREEN"], col["BLUE"]), \
                    pix_scheme(col["RED"], col["BLUE"]), pix_scheme(col["RED"], col["GREEN"]), pix_scheme(col["GREEN"], col["BLUE"]))

def blend_colours(colour_1, colour_2, idx):
    return (abs(colour_2[0] - colour_1[0] * idx), abs(colour_2[1] - colour_1[1] * idx), abs(colour_2[2] - colour_1[2] * idx))

def update_colours():
    for i in range(0, 12):
        macropad.pixels[i] = blend_colours(pixel_colours[i].first, pixel_colours[i].second, col_tick/255)


while True:
    key_event = macropad.keys.events.get()

    col_tick += COLOUR_RATE * sign
    
    if (col_tick > 255 or col_tick < 0):
        sign = sign * -1
        if (col_tick < 0):
            col_tick = 0
        if (col_tick > 255):
            col_tick = 255

    if (pixels.any_pressed()):       
        pixels.highlight_keys()
    else:
        update_colours()
    
    if key_event:
        if key_event.pressed:
            pixels.press_key(key_event.key_number)
                
            # if key_event.key_number == 0:
            #     macropad.keyboard.send(macropad.Keycode.A)
            # if key_event.key_number == 1:
            #     macropad.keyboard.press(macropad.Keycode.SHIFT, macropad.Keycode.B)
            #     macropad.keyboard.release_all()
            # if key_event.key_number == 2:
            #     macropad.keyboard_layout.write("Hello, World!")
            # if key_event.key_number == 3:
            #     macropad.consumer_control.send(
            #         macropad.ConsumerControlCode.VOLUME_DECREMENT
            #     )            
                
            # if key_event.key_number == 4:
            #     macropad.consumer_control.send(
            #         macropad.ConsumerControlCode.VOLUME_INCREMENT
            #     )
            
        if key_event.released:
            pixels.release_key(key_event.key_number)

    pixels.process_events()

    macropad.encoder_switch_debounced.update()

    if macropad.encoder_switch_debounced.pressed:
        macropad.mouse.click(macropad.Mouse.RIGHT_BUTTON)

    current_position = macropad.encoder

    if macropad.encoder > last_position:
        macropad.mouse.move(x=+5)
        last_position = current_position

    if macropad.encoder < last_position:
        macropad.mouse.move(x=-5)
        last_position = current_position
