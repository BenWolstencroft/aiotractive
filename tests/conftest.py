"""Shared pytest fixtures for aiotractive tests.

These fixtures are based on real anonymized API responses from the Tractive API.
"""

from typing import Any

import pytest


@pytest.fixture
def auth_response() -> dict[str, Any]:
    """Standard authentication response."""
    return {
        "user_id": "test_user_123",
        "client_id": "test_client_456",
        "expires_at": 9999999999,
        "access_token": "test_access_token_xyz",
    }


@pytest.fixture
def tracker_data() -> dict[str, Any]:
    """Standard tracker data from trackers list endpoint."""
    return {
        "_id": "test_6b3d1679",
        "_type": "tracker",
        "_version": "SN5c80c58d",
    }


@pytest.fixture
def trackable_object_data() -> dict[str, Any]:
    """Standard trackable object (pet) data from list endpoint."""
    return {
        "_id": "test_a96d8e9c",
        "_type": "pet",
        "_version": "SN3052bcba",
    }


@pytest.fixture
def tracker_details() -> dict[str, Any]:
    """Real API response structure for tracker details (anonymized)."""
    return {
        "_id": "test_6b3d1679",
        "_version": "SN5c80c58d",
        "hw_id": "SN6b3d1679",
        "model_number": "TG4XL",
        "hw_edition": "RUGGED-GREY-LED",
        "bluetooth_mac": None,
        "geofence_sensitivity": "HIGH",
        "read_only": False,
        "demo": False,
        "self_test_available": False,
        "capabilities": [
            "LT",
            "BUZZER",
            "LT_BLE",
            "LED_BLE",
            "BUZZER_BLE",
            "HW_REPORTS_BLE",
            "WIFI_SCAN_REPORTS_BLE",
            "LED",
            "ACTIVITY_TRACKING",
            "WIFI_ZONE",
            "SLEEP_TRACKING",
            "VITALITY_TRACKING",
            "LOW_POWER_MODE",
        ],
        "supported_geofence_types": ["CIRCLE", "RECTANGLE", "POLYGON"],
        "fw_version": "009.044-TRV4-008-8c9222",
        "battery_save_mode": False,
        "state": "OPERATIONAL",
        "state_reason": "POWER_SAVING",
        "charging_state": "NOT_CHARGING",
        "battery_state": "REGULAR",
        "power_saving_zone_id": "id_902614ee",
        "prioritized_zone_id": "id_902614ee",
        "prioritized_zone_type": "POWER_SAVING",
        "prioritized_zone_last_seen_at": 1767295745,
        "prioritized_zone_entered_at": 1767183473,
        "_type": "tracker",
    }


@pytest.fixture
def hw_info() -> dict[str, Any]:
    """Real API response structure for hardware info (anonymized)."""
    return {
        "time": 1704067200,
        "battery_level": 42,
        "temperature_state": None,
        "clip_mounted_state": None,
        "_id": "test_6b3d1679",
        "_type": "device_hw_report",
        "_version": "SN6bb22acf",
        "report_id": "id_7577e427",
        "power_saving_zone_id": "id_902614ee",
        "hw_status": None,
    }


@pytest.fixture
def pos_report() -> dict[str, Any]:
    """Real API response structure for position report (anonymized)."""
    return {
        "time": 1704067200,
        "time_rcvd": 1767295754,
        "pos_status": None,
        "latlong": [51.5074, -0.1278],
        "speed": None,
        "pos_uncertainty": 30,
        "_id": "test_6b3d1679",
        "_type": "device_pos_report",
        "_version": "SNa3d67380",
        "altitude": 149,
        "report_id": "id_1e85b739",
        "sensor_used": "KNOWN_WIFI",
        "nearby_user_id": None,
        "power_saving_zone_id": "id_902614ee",
    }


@pytest.fixture
def positions_history() -> list[list[dict[str, Any]]]:
    """Real API response structure for positions history (anonymized)."""
    return [
        [
            {
                "time": 1704067200,
                "latlong": [51.5074, -0.1278],
                "alt": 149,
                "speed": None,
                "course": None,
                "pos_uncertainty": 30,
                "sensor_used": "KNOWN_WIFI",
            },
            {
                "time": 1704067260,
                "latlong": [51.5075, -0.1279],
                "alt": 150,
                "speed": None,
                "course": None,
                "pos_uncertainty": 25,
                "sensor_used": "KNOWN_WIFI",
            },
        ]
    ]


@pytest.fixture
def pet_details() -> dict[str, Any]:
    """Real API response structure for trackable object details (anonymized)."""
    return {
        "_id": "test_a96d8e9c",
        "_version": "SN3052bcba",
        "leaderboard_opt_out": False,
        "device_id": "test_6b3d1679",
        "_type": "pet",
        "details": {
            "_id": "test_36f14c8e",
            "_version": "SN136838f3",
            "name": "Anonymous",
            "pet_type": "DOG",
            "breed_ids": ["166"],
            "gender": "F",
            "birthday": 1704067200,
            "height": 0.61,
            "length": None,
            "weight": 28000,
            "chip_id": None,
            "neutered": False,
            "personality": [],
            "lost_or_dead": None,
            "lim": None,
            "ribcage": None,
            "weight_is_default": None,
            "height_is_default": None,
            "birthday_is_default": None,
            "breed_is_default": None,
            "instagram_username": None,
            "profile_picture_id": "id_fd26bbc8",
            "cover_picture_id": None,
            "gallery_picture_ids": [],
            "activity_settings": {
                "_id": "test_5a48098b",
                "_version": "SN5d15a986",
                "daily_goal": 1000,
                "daily_distance_goal": 0,
                "daily_active_minutes_goal": 220,
                "activity_category_thresholds_override": None,
                "daily_active_minutes_goal_is_default": None,
                "_type": "activity_setting",
            },
            "_type": "pet_detail",
            "read_only": False,
        },
        "read_only": False,
        "created_at": 1704067200,
        "home_location": [51.5074, -0.1278],
    }


@pytest.fixture
def health_overview() -> dict[str, Any]:
    """Real API response structure for health overview from APS API (anonymized)."""
    return {
        "petId": "test_a96d8e9c",
        "activityDataSyncedAt": "2024-01-01T00:00:00.000Z",
        "activity": {"minutesActive": 418, "minutesGoal": 220},
        "rest": None,
        "sleep": {"minutesDaySleep": 237, "minutesNightSleep": 390, "minutesCalm": 50},
        "bark": None,
        "restingHeartRate": {"status": "NORMAL", "dayOffset": 0},
        "restingRespiratoryRate": {"status": "NORMAL", "dayOffset": 0},
        "healthAlerts": {"unseenCount": 0},
        "associatedData": [{"type": "WEEKLY_REPORT"}, {"type": "HEALTH_WEEKLY_REPORT"}],
    }
