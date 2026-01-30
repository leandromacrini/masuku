from abc import ABC, abstractmethod


class Controls(ABC):
    NUM_BUTTONS = 4

    def __init__(self):
        self.button_previously_down = [False for _ in range(Controls.NUM_BUTTONS)]
        self.is_button_pressed = [False for _ in range(Controls.NUM_BUTTONS)]

    def update(self):
        # Call each frame to update button status
        for button in range(Controls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_button_pressed[button] = button_down and not self.button_previously_down[button]
            self.button_previously_down[button] = button_down

    @abstractmethod
    def get_x(self):
        # Overridden by subclasses
        raise NotImplementedError

    @abstractmethod
    def get_y(self):
        # Overridden by subclasses
        raise NotImplementedError

    @abstractmethod
    def button_down(self, button):
        # Overridden by subclasses
        raise NotImplementedError

    def button_pressed(self, button):
        return self.is_button_pressed[button]
