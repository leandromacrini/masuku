import pygame

from game.controls.Controls import Controls


class JoystickControls(Controls):
    def __init__(self, joystick):
        super().__init__()
        self.joystick = joystick
        joystick.init()  # Not necessary in Pygame 2.0.0 onwards

    def get_axis(self, axis_num):
        if self.joystick.get_numhats() > 0 and self.joystick.get_hat(0)[axis_num] != 0:
            # For some reason, dpad up/down are inverted when getting inputs from
            # an Xbox controller, so need to negate the value if axis_num is 1
            return self.joystick.get_hat(0)[axis_num] * (-1 if axis_num == 1 else 1)

        axis_value = self.joystick.get_axis(axis_num)
        if abs(axis_value) < 0.6:
            # Dead-zone
            return 0
        # digital movement
        return 1 if axis_value > 0 else -1

    def get_x(self):
        return self.get_axis(0)

    def get_y(self):
        return self.get_axis(1)

    def button_down(self, button):
        # Before checking button, check to make sure that the controller actually has enough buttons
        # There are some weird devices out there which could cause a crash if this check were not present
        if self.joystick.get_numbuttons() <= button:
            print("Warning: main controller does not have enough buttons!")
            return False
        return self.joystick.get_button(button) != 0
