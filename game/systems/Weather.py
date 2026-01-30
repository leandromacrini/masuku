import random

from game import config


class RainEffect:
    def __init__(
        self,
        width=config.WIDTH,
        height=config.HEIGHT,
        drop_count=140,
        wind=0.0,
        speed_range=(7.0, 12.0),
        length_range=(6.0, 12.0),
        ramp_seconds=2.0,
    ):
        self.width = width
        self.height = height
        self.intensity_max = max(0, int(drop_count))
        self.current_count = 0.0
        self.target_count = float(self.intensity_max)
        self.wind = wind
        self.speed_range = speed_range
        self.length_range = length_range
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        self.drops = []

    def _calc_ramp_speed(self, ramp_seconds, intensity_max, fps=60):
        ramp_frames = max(1, int(ramp_seconds * fps))
        if intensity_max <= 0:
            return 0.0
        return intensity_max / ramp_frames

    def _new_drop(self, start_above=False):
        x = random.uniform(0, self.width)
        y = random.uniform(-self.height, 0) if start_above else random.uniform(0, self.height)
        speed = random.uniform(*self.speed_range)
        length = random.uniform(*self.length_range)
        drift = random.uniform(-0.8, 0.8) + self.wind
        return [x, y, speed, length, drift]

    def update(self):
        if self.current_count != self.target_count:
            delta = self.target_count - self.current_count
            step = self.ramp_speed if delta > 0 else -self.ramp_speed
            if abs(delta) <= abs(step) or step == 0:
                self.current_count = self.target_count
            else:
                self.current_count += step

            desired = int(round(self.current_count))
            if desired > len(self.drops):
                for _ in range(desired - len(self.drops)):
                    self.drops.append(self._new_drop(start_above=True))
            elif desired < len(self.drops):
                del self.drops[desired:]

        for drop in self.drops:
            drop[0] += drop[4]
            drop[1] += drop[2]
            if drop[1] - drop[3] > self.height:
                drop[:] = self._new_drop(start_above=True)
            elif drop[0] < -10 or drop[0] > self.width + 10:
                drop[:] = self._new_drop(start_above=True)

    def draw(self, screen):
        if screen is None:
            return
        color = (130, 180, 230)
        for x, y, _speed, length, _drift in self.drops:
            screen.draw.line((x, y), (x + 1, y + length), color)

    def set_target(self, intensity, ramp_seconds=None):
        self.target_count = max(0.0, float(intensity))
        if ramp_seconds is not None:
            self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, max(self.intensity_max, self.target_count))

    def is_finished(self):
        return self.target_count <= 0 and self.current_count <= 0 and len(self.drops) == 0


def create_weather(kind):
    if isinstance(kind, dict):
        kind_type = kind.get("type")
        if kind_type == "rain":
            intensity = int(kind.get("intensity", 140))
            wind = float(kind.get("wind", 0.0))
            speed_mult = float(kind.get("speed", 1.0))
            length_mult = float(kind.get("length", 1.0))
            ramp_seconds = float(kind.get("ramp_seconds", 2.0))
            speed_range = (7.0 * speed_mult, 12.0 * speed_mult)
            length_range = (6.0 * length_mult, 12.0 * length_mult)
            return RainEffect(
                drop_count=intensity,
                wind=wind,
                speed_range=speed_range,
                length_range=length_range,
                ramp_seconds=ramp_seconds,
            )
        return None
    if kind == "rain":
        return RainEffect()
    return None
