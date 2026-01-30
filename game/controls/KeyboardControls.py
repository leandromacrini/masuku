from pgzero.builtins import keyboard

from game.controls.Controls import Controls


class KeyboardControls(Controls):
    def get_x(self):
        if keyboard.left:
            return -1
        if keyboard.right:
            return 1
        return 0

    def get_y(self):
        if keyboard.up:
            return -1
        if keyboard.down:
            return 1
        return 0

    def button_down(self, button):
        if button == 0:
            return keyboard.space or keyboard.z or keyboard.lctrl   # punch
        if button == 1:
            return keyboard.x or keyboard.lalt      # kick
        if button == 2:
            return keyboard.c or keyboard.lshift    # elbow
        if button == 3:
            return keyboard.a   # flying kick
        return False
