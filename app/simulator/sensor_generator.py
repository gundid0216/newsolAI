from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Sequence


DEFAULT_SITE_ID = "SITE-001"
DEFAULT_SOURCE = "simulator"
DEFAULT_RECORD_COUNT = 100_000
DEFAULT_INTERVAL_MINUTES = 5

CSV_COLUMNS: tuple[str, ...] = (
    "site_id",
    "measured_at",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_direction",
    "pressure",
    "h2s",
    "nh3",
    "voc",
    "odor_intensity",
    "source",
)


@dataclass(frozen=True)
class SensorReading:
    """Single simulated environmental sensor reading."""

    site_id: str
    measured_at: datetime
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    h2s: float
    nh3: float
    voc: float
    odor_intensity: float
    source: str = DEFAULT_SOURCE

    def to_row(self) -> dict[str, str | float]:
        return {
            "site_id": self.site_id,
            "measured_at": self.measured_at.isoformat(),
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "wind_speed": round(self.wind_speed, 2),
            "wind_direction": round(self.wind_direction, 2),
            "pressure": round(self.pressure, 2),
            "h2s": round(self.h2s, 4),
            "nh3": round(self.nh3, 4),
            "voc": round(self.voc, 4),
            "odor_intensity": round(self.odor_intensity, 4),
            "source": self.source,
        }


class SensorGenerator:
    """Generates realistic environmental sensor data for odor monitoring simulations."""

    def __init__(
        self,
        *,
        site_id: str = DEFAULT_SITE_ID,
        start_at: datetime | None = None,
        interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
        seed: int | None = None,
    ) -> None:
        self.site_id = site_id
        self.start_at = start_at or datetime(2025, 1, 1, tzinfo=timezone.utc)
        self.interval = timedelta(minutes=interval_minutes)
        self._rng = random.Random(seed)

        # Smoothed state carried across readings for natural temporal variation.
        self._wind_speed = self._rng.uniform(1.5, 4.0)
        self._wind_direction = self._rng.uniform(0.0, 360.0)
        self._pressure = self._rng.uniform(1005.0, 1020.0)

    def generate(self, count: int = DEFAULT_RECORD_COUNT) -> Iterator[SensorReading]:
        """Yield `count` sequential sensor readings."""
        if count <= 0:
            return

        timestamp = self.start_at
        for _ in range(count):
            yield self._generate_reading(timestamp)
            timestamp += self.interval

    def generate_list(self, count: int = DEFAULT_RECORD_COUNT) -> list[SensorReading]:
        """Return `count` sensor readings as a list."""
        return list(self.generate(count))

    def save_to_csv(
        self,
        output_path: str | Path,
        count: int = DEFAULT_RECORD_COUNT,
    ) -> Path:
        """Generate readings and write them to a CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for reading in self.generate(count):
                writer.writerow(reading.to_row())

        return path

    def _generate_reading(self, measured_at: datetime) -> SensorReading:
        temperature = self._generate_temperature(measured_at)
        humidity = self._generate_humidity(temperature)
        wind_speed, wind_direction = self._generate_wind()
        pressure = self._generate_pressure(temperature)

        nh3, h2s, voc = self._generate_gases(
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            pressure=pressure,
        )
        odor_intensity = self._calculate_odor_intensity(nh3=nh3, h2s=h2s, voc=voc)

        return SensorReading(
            site_id=self.site_id,
            measured_at=measured_at,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            pressure=pressure,
            h2s=h2s,
            nh3=nh3,
            voc=voc,
            odor_intensity=odor_intensity,
        )

    def _generate_temperature(self, measured_at: datetime) -> float:
        """Model a day/night temperature cycle with seasonal drift and noise."""
        hour_fraction = measured_at.hour + measured_at.minute / 60.0
        day_cycle = math.sin((2.0 * math.pi * (hour_fraction - 6.0)) / 24.0)
        seasonal_cycle = math.sin((2.0 * math.pi * measured_at.timetuple().tm_yday) / 365.25)

        base_temperature = 18.0 + 4.0 * seasonal_cycle
        daily_amplitude = 7.5 + 1.5 * seasonal_cycle
        temperature = base_temperature + daily_amplitude * day_cycle
        temperature += self._rng.gauss(0.0, 0.35)

        return self._clamp(temperature, -5.0, 42.0)

    def _generate_humidity(self, temperature: float) -> float:
        """Humidity decreases as temperature rises, with stochastic variation."""
        inverse_component = 88.0 - 1.35 * (temperature - 15.0)
        humidity = inverse_component + self._rng.gauss(0.0, 4.0)
        return self._clamp(humidity, 25.0, 98.0)

    def _generate_wind(self) -> tuple[float, float]:
        """Produce smoothly varying wind speed and direction."""
        self._wind_speed += self._rng.gauss(0.0, 0.25)
        self._wind_speed = self._clamp(self._wind_speed, 0.2, 18.0)

        direction_delta = self._rng.gauss(0.0, 18.0)
        if self._wind_speed > 8.0:
            direction_delta *= 1.6
        self._wind_direction = (self._wind_direction + direction_delta) % 360.0

        gust = max(0.0, self._rng.gauss(0.0, 0.6))
        wind_speed = self._wind_speed + gust

        return round(wind_speed, 2), round(self._wind_direction, 2)

    def _generate_pressure(self, temperature: float) -> float:
        """Pressure varies slowly and responds mildly to temperature changes."""
        self._pressure += self._rng.gauss(0.0, 0.08)
        self._pressure -= 0.05 * (temperature - 18.0)
        self._pressure = self._clamp(self._pressure, 980.0, 1040.0)
        return self._pressure

    def _generate_gases(
        self,
        *,
        temperature: float,
        humidity: float,
        wind_speed: float,
        pressure: float,
    ) -> tuple[float, float, float]:
        """
        Gas concentrations respond to weather:
        - low wind allows accumulation
        - higher temperature increases volatilization
        - humidity moderates release and dispersion
        """
        dispersion = 1.0 / (1.0 + wind_speed * 0.45)
        pressure_effect = 1.0 + (1013.0 - pressure) * 0.002
        temperature_effect = 1.0 + max(0.0, temperature - 15.0) * 0.025
        humidity_effect = 1.0 + max(0.0, humidity - 70.0) * 0.004

        nh3_base = 0.18 + self._rng.uniform(0.0, 0.08)
        h2s_base = 0.05 + self._rng.uniform(0.0, 0.03)
        voc_base = 0.12 + self._rng.uniform(0.0, 0.06)

        nh3 = nh3_base * dispersion * humidity_effect * pressure_effect
        h2s = h2s_base * dispersion * humidity_effect * pressure_effect
        voc = voc_base * dispersion * temperature_effect * pressure_effect

        nh3 += self._rng.gauss(0.0, 0.01)
        h2s += self._rng.gauss(0.0, 0.004)
        voc += self._rng.gauss(0.0, 0.008)

        return (
            self._clamp(nh3, 0.0, 5.0),
            self._clamp(h2s, 0.0, 2.0),
            self._clamp(voc, 0.0, 4.0),
        )

    def _calculate_odor_intensity(
        self,
        *,
        nh3: float,
        h2s: float,
        voc: float,
    ) -> float:
        """
        Derive odor intensity from gas concentrations.

        H2S contributes strongly at low concentrations; NH3 and VOC add broader impact.
        """
        weighted_sum = (
            (nh3 * 1.15) ** 1.05
            + (h2s * 2.40) ** 1.10
            + (voc * 0.95) ** 1.00
        )
        odor_intensity = math.sqrt(weighted_sum) * 1.8
        return self._clamp(odor_intensity, 0.0, 20.0)

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))


def save_sensor_data_to_csv(
    output_path: str | Path,
    count: int = DEFAULT_RECORD_COUNT,
    *,
    site_id: str = DEFAULT_SITE_ID,
    start_at: datetime | None = None,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
    seed: int | None = None,
) -> Path:
    """Convenience wrapper to generate sensor data and save it as CSV."""
    generator = SensorGenerator(
        site_id=site_id,
        start_at=start_at,
        interval_minutes=interval_minutes,
        seed=seed,
    )
    return generator.save_to_csv(output_path, count=count)


def main(argv: Sequence[str] | None = None) -> None:
    """Generate the default dataset and save it under ./data/."""
    output = save_sensor_data_to_csv(
        Path("data") / "sensor_readings.csv",
        count=DEFAULT_RECORD_COUNT,
        seed=42,
    )
    print(f"Generated {DEFAULT_RECORD_COUNT:,} records -> {output}")


if __name__ == "__main__":
    main()
