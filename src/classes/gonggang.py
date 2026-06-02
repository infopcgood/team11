from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


EARTH_RADIUS_M = 6_371_000.0


@dataclass(frozen=True)
class BuildingLocation:
	building_number: str
	latitude: float
	longitude: float


@dataclass(frozen=True)
class NearbyBuilding:
	building_number: str
	distance_to_path_m: float


class Gonggang:
	"""Represents empty-time movement between two consecutive classes.

	The constructor accepts:
	- previous class building number
	- next class building number
	- previous class end time
	- next class start time

	Then it computes and stores:
	- empty time duration (minutes)
	- movement start/end buildings
	- nearby buildings around the straight line path between classes
	"""

	_building_locations_cache: dict[str, BuildingLocation] | None = None

	def __init__(
		self,
		previous_building_number: str,
		next_building_number: str,
		previous_end_time: str,
		next_start_time: str,
	) -> None:
		self.previous_building_number = str(previous_building_number).strip()
		self.next_building_number = str(next_building_number).strip()
		self.previous_end_time = previous_end_time.strip()
		self.next_start_time = next_start_time.strip()

		self.empty_duration_minutes = self._compute_empty_duration_minutes(
			self.previous_end_time,
			self.next_start_time,
		)

		locations = self._get_building_locations()
		if self.previous_building_number not in locations:
			raise ValueError(
				f"Unknown previous building number: {self.previous_building_number}"
			)
		if self.next_building_number not in locations:
			raise ValueError(f"Unknown next building number: {self.next_building_number}")

		self.start_building = self.previous_building_number
		self.end_building = self.next_building_number

		self.start_location = locations[self.start_building]
		self.end_location = locations[self.end_building]

		self.route_distance_m = self._haversine_distance_m(
			self.start_location.latitude,
			self.start_location.longitude,
			self.end_location.latitude,
			self.end_location.longitude,
		)

		self.nearby_buildings = self._find_nearby_buildings(
			locations=locations,
			start=self.start_location,
			end=self.end_location,
		)

	@property
	def empty_duration(self) -> int:
		"""Backward-friendly alias for empty-time minutes."""
		return self.empty_duration_minutes

	@classmethod
	def _get_building_locations(cls) -> dict[str, BuildingLocation]:
		if cls._building_locations_cache is not None:
			return cls._building_locations_cache

		csv_path = Path(__file__).resolve().parents[2] / "data" / "building_latlong.csv"
		if not csv_path.exists():
			raise FileNotFoundError(f"Building coordinate file not found: {csv_path}")

		locations: dict[str, BuildingLocation] = {}
		with csv_path.open(newline="", encoding="utf-8") as fp:
			reader = csv.DictReader(fp)
			for row in reader:
				building_number = str(row["building_number"]).strip()
				locations[building_number] = BuildingLocation(
					building_number=building_number,
					latitude=float(row["latitude"]),
					longitude=float(row["longitude"]),
				)

		if not locations:
			raise ValueError("No building coordinates were loaded from CSV.")

		cls._building_locations_cache = locations
		return locations

	@staticmethod
	def _compute_empty_duration_minutes(previous_end_time: str, next_start_time: str) -> int:
		"""Return the time gap in minutes.

		Input format: HH:MM (24-hour format)
		"""

		end_dt = datetime.strptime(previous_end_time, "%H:%M")
		start_dt = datetime.strptime(next_start_time, "%H:%M")

		delta_minutes = int((start_dt - end_dt).total_seconds() // 60)
		if delta_minutes < 0:
			delta_minutes += 24 * 60
		return delta_minutes

	@staticmethod
	def _haversine_distance_m(
		lat1: float,
		lon1: float,
		lat2: float,
		lon2: float,
	) -> float:
		lat1_r = math.radians(lat1)
		lat2_r = math.radians(lat2)
		d_lat = math.radians(lat2 - lat1)
		d_lon = math.radians(lon2 - lon1)

		a = (
			math.sin(d_lat / 2.0) ** 2
			+ math.cos(lat1_r) * math.cos(lat2_r) * (math.sin(d_lon / 2.0) ** 2)
		)
		c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
		return EARTH_RADIUS_M * c

	@staticmethod
	def _to_local_xy_m(lat: float, lon: float, ref_lat: float, ref_lon: float) -> tuple[float, float]:
		x = math.radians(lon - ref_lon) * EARTH_RADIUS_M * math.cos(math.radians(ref_lat))
		y = math.radians(lat - ref_lat) * EARTH_RADIUS_M
		return (x, y)

	@classmethod
	def _point_to_segment_distance_m(
		cls,
		point: BuildingLocation,
		start: BuildingLocation,
		end: BuildingLocation,
	) -> float:
		"""Compute shortest distance from point to the line segment start-end."""

		ref_lat = (point.latitude + start.latitude + end.latitude) / 3.0
		ref_lon = (point.longitude + start.longitude + end.longitude) / 3.0

		px, py = cls._to_local_xy_m(point.latitude, point.longitude, ref_lat, ref_lon)
		ax, ay = cls._to_local_xy_m(start.latitude, start.longitude, ref_lat, ref_lon)
		bx, by = cls._to_local_xy_m(end.latitude, end.longitude, ref_lat, ref_lon)

		abx = bx - ax
		aby = by - ay
		apx = px - ax
		apy = py - ay

		ab_len_sq = (abx * abx) + (aby * aby)
		if ab_len_sq == 0.0:
			return math.hypot(px - ax, py - ay)

		t = ((apx * abx) + (apy * aby)) / ab_len_sq
		t = max(0.0, min(1.0, t))

		closest_x = ax + t * abx
		closest_y = ay + t * aby
		return math.hypot(px - closest_x, py - closest_y)

	@classmethod
	def _find_nearby_buildings(
		cls,
		locations: dict[str, BuildingLocation],
		start: BuildingLocation,
		end: BuildingLocation,
	) -> list[NearbyBuilding]:
		route_length = cls._haversine_distance_m(
			start.latitude,
			start.longitude,
			end.latitude,
			end.longitude,
		)
		max_distance_to_path = route_length / 5.0

		nearby: list[NearbyBuilding] = []
		for building_number, location in locations.items():
			distance_to_path = cls._point_to_segment_distance_m(location, start, end)
			if distance_to_path <= max_distance_to_path:
				nearby.append(
					NearbyBuilding(
						building_number=building_number,
						distance_to_path_m=distance_to_path,
					)
				)

		nearby.sort(key=lambda building: building.distance_to_path_m)
		return nearby

	def to_dict(self) -> dict[str, object]:
		"""Serialize key Gonggang information for JSON or debug output."""

		return {
			"start_building": self.start_building,
			"end_building": self.end_building,
			"previous_end_time": self.previous_end_time,
			"next_start_time": self.next_start_time,
			"empty_duration_minutes": self.empty_duration_minutes,
			"route_distance_m": round(self.route_distance_m, 2),
			"nearby_buildings": [
				{
					"building_number": item.building_number,
					"distance_to_path_m": round(item.distance_to_path_m, 2),
				}
				for item in self.nearby_buildings
			],
		}
