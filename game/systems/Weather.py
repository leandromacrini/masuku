import math
import random
import pygame

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
        self.target_count = 0.0
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

    def apply_settings(self, intensity, wind, speed_mult, length_mult, ramp_seconds):
        self.intensity_max = max(0, int(intensity))
        self.wind = float(wind)
        self.speed_range = (7.0 * float(speed_mult), 12.0 * float(speed_mult))
        self.length_range = (6.0 * float(length_mult), 12.0 * float(length_mult))
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        if self.current_count > self.intensity_max:
            self.current_count = float(self.intensity_max)
            desired = int(round(self.current_count))
            if desired < len(self.drops):
                del self.drops[desired:]

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

    def get_kind(self):
        return "rain"

    def set_target(self, intensity, ramp_seconds=None):
        self.target_count = max(0.0, float(intensity))
        if ramp_seconds is not None:
            self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, max(self.intensity_max, self.target_count))

    def get_max_intensity(self):
        return self.intensity_max

    def get_ramp_seconds(self):
        return self.ramp_seconds

    def is_finished(self):
        return self.target_count <= 0 and self.current_count <= 0 and len(self.drops) == 0


class SnowEffect:
    def __init__(
        self,
        width=config.WIDTH,
        height=config.HEIGHT,
        drop_count=140,
        wind=0.0,
        speed_range=(1.0, 3.0),
        size_range=(1.0, 2.0),
        ramp_seconds=2.0,
    ):
        self.width = width
        self.height = height
        self.intensity_max = max(0, int(drop_count))
        self.current_count = 0.0
        self.target_count = 0.0
        self.wind = wind
        self.speed_range = speed_range
        self.size_range = size_range
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        self.flakes = []

    def _calc_ramp_speed(self, ramp_seconds, intensity_max, fps=60):
        ramp_frames = max(1, int(ramp_seconds * fps))
        if intensity_max <= 0:
            return 0.0
        return intensity_max / ramp_frames

    def _new_flake(self, start_above=False):
        x = random.uniform(0, self.width)
        y = random.uniform(-self.height, 0) if start_above else random.uniform(0, self.height)
        speed = random.uniform(*self.speed_range)
        size = random.uniform(*self.size_range)
        drift = random.uniform(-0.4, 0.4) + self.wind
        wobble = random.uniform(0.5, 1.5)
        return [x, y, speed, size, drift, wobble]

    def apply_settings(self, intensity, wind, speed_mult, length_mult, ramp_seconds):
        self.intensity_max = max(0, int(intensity))
        self.wind = float(wind)
        self.speed_range = (1.0 * float(speed_mult), 3.0 * float(speed_mult))
        self.size_range = (1.0 * float(length_mult), 2.0 * float(length_mult))
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        if self.current_count > self.intensity_max:
            self.current_count = float(self.intensity_max)
            desired = int(round(self.current_count))
            if desired < len(self.flakes):
                del self.flakes[desired:]

    def update(self):
        if self.current_count != self.target_count:
            delta = self.target_count - self.current_count
            step = self.ramp_speed if delta > 0 else -self.ramp_speed
            if abs(delta) <= abs(step) or step == 0:
                self.current_count = self.target_count
            else:
                self.current_count += step

            desired = int(round(self.current_count))
            if desired > len(self.flakes):
                for _ in range(desired - len(self.flakes)):
                    self.flakes.append(self._new_flake(start_above=True))
            elif desired < len(self.flakes):
                del self.flakes[desired:]

        for flake in self.flakes:
            flake[0] += flake[4] + (flake[5] * 0.05)
            flake[1] += flake[2]
            if flake[1] - flake[3] > self.height:
                flake[:] = self._new_flake(start_above=True)
            elif flake[0] < -10 or flake[0] > self.width + 10:
                flake[:] = self._new_flake(start_above=True)

    def draw(self, screen):
        if screen is None:
            return
        color = (240, 245, 255)
        for x, y, _speed, size, _drift, _wobble in self.flakes:
            screen.draw.filled_circle((x, y), max(1, int(round(size))), color)

    def get_kind(self):
        return "snow"

    def set_target(self, intensity, ramp_seconds=None):
        self.target_count = max(0.0, float(intensity))
        if ramp_seconds is not None:
            self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, max(self.intensity_max, self.target_count))

    def is_finished(self):
        return self.target_count <= 0 and self.current_count <= 0 and len(self.flakes) == 0


class LeavesEffect:
    def __init__(
        self,
        width=config.WIDTH,
        height=config.HEIGHT,
        drop_count=140,
        wind=0.0,
        speed_range=(1.5, 4.0),
        size_range=(2.0, 4.0),
        ramp_seconds=2.0,
    ):
        self.width = width
        self.height = height
        self.intensity_max = max(0, int(drop_count))
        self.current_count = 0.0
        self.target_count = 0.0
        self.wind = wind
        self.speed_range = speed_range
        self.size_range = size_range
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        self.leaves = []

    def _calc_ramp_speed(self, ramp_seconds, intensity_max, fps=60):
        ramp_frames = max(1, int(ramp_seconds * fps))
        if intensity_max <= 0:
            return 0.0
        return intensity_max / ramp_frames

    def _new_leaf(self, start_above=False):
        x = random.uniform(0, self.width)
        y = random.uniform(-self.height, 0) if start_above else random.uniform(0, self.height)
        speed = random.uniform(*self.speed_range)
        size = random.uniform(*self.size_range)
        drift = random.uniform(-0.6, 0.6) + self.wind
        wobble = random.uniform(0.8, 1.6)
        angle = math.radians(45.0 * (1.0 + random.uniform(-0.1, 0.1)))
        tint = random.choice([(70, 140, 70), (60, 120, 60), (90, 160, 90)])
        return [x, y, speed, size, drift, wobble, angle, tint]

    def apply_settings(self, intensity, wind, speed_mult, length_mult, ramp_seconds):
        self.intensity_max = max(0, int(intensity))
        self.wind = float(wind)
        self.speed_range = (1.5 * float(speed_mult), 4.0 * float(speed_mult))
        self.size_range = (2.0 * float(length_mult), 4.0 * float(length_mult))
        self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, self.intensity_max)
        if self.current_count > self.intensity_max:
            self.current_count = float(self.intensity_max)
            desired = int(round(self.current_count))
            if desired < len(self.leaves):
                del self.leaves[desired:]

    def update(self):
        if self.current_count != self.target_count:
            delta = self.target_count - self.current_count
            step = self.ramp_speed if delta > 0 else -self.ramp_speed
            if abs(delta) <= abs(step) or step == 0:
                self.current_count = self.target_count
            else:
                self.current_count += step

            desired = int(round(self.current_count))
            if desired > len(self.leaves):
                for _ in range(desired - len(self.leaves)):
                    self.leaves.append(self._new_leaf(start_above=True))
            elif desired < len(self.leaves):
                del self.leaves[desired:]

        for leaf in self.leaves:
            leaf[0] += leaf[4] + (leaf[5] * 0.08)
            leaf[1] += leaf[2]
            if leaf[1] - leaf[3] > self.height:
                leaf[:] = self._new_leaf(start_above=True)
            elif leaf[0] < -20 or leaf[0] > self.width + 20:
                leaf[:] = self._new_leaf(start_above=True)

    def draw(self, screen):
        if screen is None:
            return
        for x, y, _speed, size, _drift, _wobble, angle, tint in self.leaves:
            w = size
            h = size * 1.4
            dx = w * 0.6
            dy = h * 0.6
            points = [(-0.0, -dy), (dx, 0.0), (0.0, dy), (-dx, 0.0)]
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rotated = []
            for px, py in points:
                rx = px * cos_a - py * sin_a
                ry = px * sin_a + py * cos_a
                rotated.append((x + rx, y + ry))
            pygame.draw.polygon(screen.surface, tint, rotated, 0)
            # small stem
            stem_len = size * 0.8
            stem_start = (x + cos_a * size * 0.6, y + sin_a * size * 0.6)
            stem_end = (x + cos_a * (size * 0.6 + stem_len), y + sin_a * (size * 0.6 + stem_len))
            screen.draw.line(stem_start, stem_end, (40, 80, 40))

    def get_kind(self):
        return "leaves"

    def set_target(self, intensity, ramp_seconds=None):
        self.target_count = max(0.0, float(intensity))
        if ramp_seconds is not None:
            self.ramp_seconds = max(0.0, float(ramp_seconds))
        self.ramp_speed = self._calc_ramp_speed(self.ramp_seconds, max(self.intensity_max, self.target_count))

    def is_finished(self):
        return self.target_count <= 0 and self.current_count <= 0 and len(self.leaves) == 0


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
        if kind_type == "snow":
            intensity = int(kind.get("intensity", 140))
            wind = float(kind.get("wind", 0.0))
            speed_mult = float(kind.get("speed", 1.0))
            length_mult = float(kind.get("length", 1.0))
            ramp_seconds = float(kind.get("ramp_seconds", 2.0))
            speed_range = (1.0 * speed_mult, 3.0 * speed_mult)
            size_range = (1.0 * length_mult, 2.0 * length_mult)
            return SnowEffect(
                drop_count=intensity,
                wind=wind,
                speed_range=speed_range,
                size_range=size_range,
                ramp_seconds=ramp_seconds,
            )
        if kind_type == "leaves":
            intensity = int(kind.get("intensity", 140))
            wind = float(kind.get("wind", 0.0))
            speed_mult = float(kind.get("speed", 1.0))
            length_mult = float(kind.get("length", 1.0))
            ramp_seconds = float(kind.get("ramp_seconds", 2.0))
            speed_range = (1.5 * speed_mult, 4.0 * speed_mult)
            size_range = (2.0 * length_mult, 4.0 * length_mult)
            return LeavesEffect(
                drop_count=intensity,
                wind=wind,
                speed_range=speed_range,
                size_range=size_range,
                ramp_seconds=ramp_seconds,
            )
        return None
    if kind == "rain":
        return RainEffect()
    if kind == "snow":
        return SnowEffect()
    if kind == "leaves":
        return LeavesEffect()
    return None


def weather_matches(effect, kind):
    if effect is None:
        return False
    if isinstance(kind, dict):
        return effect.get_kind() == kind.get("type")
    return effect.get_kind() == kind


def get_weather_settings(kind):
    if isinstance(kind, dict):
        return {
            "intensity": int(kind.get("intensity", 140)),
            "ramp_seconds": float(kind.get("ramp_seconds", 2.0)),
        }
    if kind == "rain":
        return {"intensity": 140, "ramp_seconds": 2.0}
    return {"intensity": 0, "ramp_seconds": 0.0}


class WeatherSystem:
    def __init__(self):
        self.effect = None
        self.active_kind = None
        self.settings = {
            "intensity": 0,
            "wind": 0.0,
            "speed": 1.0,
            "length": 1.0,
            "ramp_seconds": 2.0,
        }

    def set_weather(self, kind):
        if kind is None:
            self.stop()
            self.active_kind = None
            return
        if isinstance(kind, dict):
            kind_type = kind.get("type")
            if kind_type not in ("rain", "snow", "leaves"):
                self.stop()
                self.active_kind = None
                return
            self.settings = {
                "intensity": int(kind.get("intensity", 140)),
                "wind": float(kind.get("wind", 0.0)),
                "speed": float(kind.get("speed", 1.0)),
                "length": float(kind.get("length", 1.0)),
                "ramp_seconds": float(kind.get("ramp_seconds", 2.0)),
            }
            if self.active_kind != kind_type or self.effect is None:
                if kind_type == "rain":
                    self.effect = RainEffect()
                elif kind_type == "snow":
                    self.effect = SnowEffect()
                else:
                    self.effect = LeavesEffect()
            self.effect.apply_settings(
                self.settings["intensity"],
                self.settings["wind"],
                self.settings["speed"],
                self.settings["length"],
                self.settings["ramp_seconds"],
            )
            self.effect.set_target(self.settings["intensity"], self.settings["ramp_seconds"])
            self.active_kind = kind_type
            return
        if kind in ("rain", "snow", "leaves"):
            self.settings = {
                "intensity": 140,
                "wind": 0.0,
                "speed": 1.0,
                "length": 1.0,
                "ramp_seconds": 2.0,
            }
            if self.active_kind != kind or self.effect is None:
                if kind == "rain":
                    self.effect = RainEffect()
                elif kind == "snow":
                    self.effect = SnowEffect()
                else:
                    self.effect = LeavesEffect()
            self.effect.apply_settings(
                self.settings["intensity"],
                self.settings["wind"],
                self.settings["speed"],
                self.settings["length"],
                self.settings["ramp_seconds"],
            )
            self.effect.set_target(self.settings["intensity"], self.settings["ramp_seconds"])
            self.active_kind = kind
            return
        self.stop()
        self.active_kind = None

    def stop(self):
        if self.effect is not None:
            self.effect.set_target(0, self.settings.get("ramp_seconds", 0.0))

    def update(self):
        if self.effect is not None:
            self.effect.update()

    def draw(self, screen):
        if self.effect is not None:
            self.effect.draw(screen)
