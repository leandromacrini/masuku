import time


def clamp(value, min_val, max_val):
    # Clamp a value within a given range
    return min(max(value, min_val), max_val)


def remap(old_val, old_min, old_max, new_min, new_max):
    # Remap a number from one range to a different range
    # e.g. remapping 5 from source range of 0 to 10, to destination range of 0 to 100, becomes 50
    return (new_max - new_min) * (old_val - old_min) / (old_max - old_min) + new_min


def remap_clamp(old_val, old_min, old_max, new_min, new_max):
    # Like remap, but constrains the resulting value so that it can't be outside the new range
    # These first two lines are in case new_min and new_max are inverted
    lower_limit = min(new_min, new_max)
    upper_limit = max(new_min, new_max)
    return min(upper_limit, max(lower_limit, remap(old_val, old_min, old_max, new_min, new_max)))


def sign(x):
    # Returns 1, 0 or -1 depending on whether number is positive, zero or negative
    if x == 0:
        return 0
    return -1 if x < 0 else 1


def move_towards(n, target, speed):
    # Returns new value, and the direction of travel (-1, 0 or 1)
    if n < target:
        return min(n + speed, target), 1
    if n > target:
        return max(n - speed, target), -1
    return n, 0


class Profiler:
    # Class for measuring how long code takes to run
    def __init__(self, name=""):
        self.start_time = time.perf_counter()
        self.name = name

    def get_ms(self):
        end_time = time.perf_counter()
        diff = end_time - self.start_time
        return diff * 1000

    def __str__(self):
        return f"{self.name}: {self.get_ms()}ms"
