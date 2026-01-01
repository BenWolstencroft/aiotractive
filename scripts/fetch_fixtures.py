#!/usr/bin/env python
"""
Fetch real API responses from Tractive to use as fixture recommendations.
All sensitive data will be anonymized before output.

Usage:
    python scripts/fetch_fixtures.py --email YOUR_EMAIL --password YOUR_PASSWORD
"""

import argparse
import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

# Add parent directory to path so we can import aiotractive
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiotractive import Tractive


def anonymize_id(value: str, prefix: str = "abc") -> str:
    """Replace an ID with a deterministic but anonymous version."""
    if not value:
        return value
    # Use first 8 chars of hash for consistent but anonymous IDs
    hashed = hashlib.sha256(value.encode()).hexdigest()[:8]
    return f"{prefix}{hashed}"


def anonymize_email(email: str) -> str:
    """Anonymize email address."""
    if not email or "@" not in email:
        return email
    return "user@example.com"


def anonymize_coordinates(lat: float | None, lon: float | None) -> tuple[float, float]:
    """Return fixed anonymous coordinates (London)."""
    return (51.5074, -0.1278)


def anonymize_value(key: str, value, parent_key: str = "") -> any:
    """Anonymize a value based on its key name."""
    if value is None:
        return None
    
    key_lower = key.lower()
    
    # IDs - keep structure but anonymize
    if key in ("_id", "id", "user_id", "device_id", "tracker_id", "pet_id", "petId"):
        return anonymize_id(str(value), "test_")
    
    if key.endswith("_id") and isinstance(value, str) and len(value) > 10:
        return anonymize_id(str(value), "id_")
    
    if key == "_type" or key == "type":
        return value  # Keep type identifiers
    
    # Names
    if key in ("name", "first_name", "last_name", "pet_name"):
        return "Anonymous"
    
    # Email
    if "email" in key_lower:
        return anonymize_email(str(value))
    
    # Phone
    if "phone" in key_lower:
        return "+1234567890"
    
    # Coordinates - handle latlong arrays and individual values
    if key == "latlong" and isinstance(value, list) and len(value) == 2:
        return [51.5074, -0.1278]
    if key == "home_location" and isinstance(value, list) and len(value) == 2:
        return [51.5074, -0.1278]
    if key in ("latitude", "lat"):
        return 51.5074
    if key in ("longitude", "lon", "lng"):
        return -0.1278
    
    # Addresses
    if key in ("address", "street", "city", "zip", "postal_code", "country"):
        return "Anonymous"
    
    # Timestamps - keep structure but normalize if it looks like a recent timestamp
    if key in ("time", "timestamp", "created_at", "updated_at", "last_seen", "birthday"):
        if isinstance(value, (int, float)) and value > 1600000000:  # After 2020
            return 1704067200  # 2024-01-01 00:00:00 UTC
        return value
    
    # ISO date strings
    if key.endswith("SyncedAt") or key.endswith("_at"):
        if isinstance(value, str) and "T" in value:
            return "2024-01-01T00:00:00.000Z"
    
    # URLs with potential user data
    if "url" in key_lower and isinstance(value, str) and ("user" in value or "pet" in value):
        return re.sub(r"/[a-f0-9]{24}/", "/test_id123456/", value)
    
    # Serial numbers, IMEI, etc.
    if key in ("serial_number", "imei", "hw_id", "_version"):
        if isinstance(value, str):
            return anonymize_id(value, "SN")
        return value
    
    # Picture IDs
    if "picture_id" in key_lower and value:
        return anonymize_id(str(value), "pic_")
    
    return value


def anonymize_dict(data: dict, parent_key: str = "") -> dict:
    """Recursively anonymize a dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = anonymize_dict(value, key)
        elif isinstance(value, list):
            result[key] = anonymize_list(key, value)
        else:
            result[key] = anonymize_value(key, value, parent_key)
    return result


def anonymize_list(key: str, data: list) -> list:
    """Recursively anonymize a list."""
    # Special case for coordinate arrays (latlong, home_location)
    if key in ("latlong", "home_location") and len(data) == 2:
        if all(isinstance(x, (int, float)) for x in data):
            return [51.5074, -0.1278]
    
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(anonymize_dict(item, key))
        elif isinstance(item, list):
            result.append(anonymize_list(key, item))
        else:
            result.append(anonymize_value(key, item, ""))
    return result


def format_fixture(name: str, data: dict | list) -> str:
    """Format data as a pytest fixture."""
    if isinstance(data, list):
        anonymized = anonymize_list(name, data)
    else:
        anonymized = anonymize_dict(data)
    json_str = json.dumps(anonymized, indent=4)
    # Convert to Python dict syntax
    json_str = json_str.replace("null", "None").replace("true", "True").replace("false", "False")
    
    return f'''
@pytest.fixture
def {name}() -> dict[str, Any]:
    """Real API response structure (anonymized)."""
    return {json_str}
'''


async def fetch_all_fixtures(email: str, password: str) -> dict[str, any]:
    """Fetch all available API responses."""
    import asyncio as aio
    fixtures = {}
    
    async with Tractive(email, password) as client:
        print("✓ Authenticated successfully")
        
        # Get trackers list - need to call API directly to get raw response
        print("\nFetching trackers...")
        trackers_raw = await client._api.request(f"user/{await client._api.user_id()}/trackers")
        fixtures["trackers_list"] = trackers_raw
        print(f"  Found {len(trackers_raw)} tracker(s)")
        
        await aio.sleep(1)  # Rate limit protection
        
        if trackers_raw:
            tracker_id = trackers_raw[0]["_id"]
            tracker = client.tracker(tracker_id)
            
            # Tracker details
            print("\nFetching tracker details...")
            try:
                details = await tracker.details()
                fixtures["tracker_details"] = details
                print("  ✓ Got tracker details")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
            
            await aio.sleep(1)
            
            # Hardware info
            print("\nFetching hardware info...")
            try:
                hw = await tracker.hw_info()
                fixtures["tracker_hw_info"] = hw
                print("  ✓ Got hardware info")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
            
            await aio.sleep(1)
            
            # Position report
            print("\nFetching position report...")
            try:
                pos = await tracker.pos_report()
                fixtures["tracker_pos_report"] = pos
                print("  ✓ Got position report")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
            
            await aio.sleep(1)
            
            # Positions history (last 24h)
            print("\nFetching positions history...")
            try:
                import time
                now = int(time.time())
                day_ago = now - 86400
                positions = await tracker.positions(day_ago, now, "json_segments")
                fixtures["tracker_positions"] = positions
                print(f"  ✓ Got {len(positions) if isinstance(positions, list) else 'unknown'} positions")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        await aio.sleep(1)
        
        # Get trackable objects (pets) - raw API response
        print("\nFetching trackable objects...")
        try:
            trackables_raw = await client._api.request(f"user/{await client._api.user_id()}/trackable_objects")
            fixtures["trackable_objects_list"] = trackables_raw
            print(f"  Found {len(trackables_raw)} trackable object(s)")
            
            await aio.sleep(1)
            
            if trackables_raw:
                obj_id = trackables_raw[0]["_id"]
                obj = client.trackable_object(obj_id)
                
                # Trackable object details
                print("\nFetching trackable object details...")
                try:
                    details = await obj.details()
                    fixtures["trackable_object_details"] = details
                    print("  ✓ Got trackable object details")
                except Exception as e:
                    print(f"  ✗ Failed: {e}")
                
                await aio.sleep(1)
                
                # Health overview (uses APS API)
                print("\nFetching health overview (APS API)...")
                try:
                    health = await obj.health_overview()
                    fixtures["health_overview"] = health
                    print("  ✓ Got health overview")
                except Exception as e:
                    print(f"  ✗ Failed: {e}")
        except Exception as e:
            print(f"  ✗ Failed to fetch trackable objects: {e}")
    
    return fixtures


def main():
    parser = argparse.ArgumentParser(description="Fetch Tractive API fixtures")
    parser.add_argument("--email", "-e", required=True, help="Tractive account email")
    parser.add_argument("--password", "-p", required=True, help="Tractive account password")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Tractive API Fixture Fetcher")
    print("=" * 60)
    print("\nNote: All output will be anonymized")
    print()
    
    fixtures = asyncio.run(fetch_all_fixtures(args.email, args.password))
    
    print("\n" + "=" * 60)
    print("ANONYMIZED FIXTURE DATA")
    print("=" * 60)
    
    output_lines = [
        "# Auto-generated fixture recommendations from real API responses",
        "# All data has been anonymized",
        "",
        "from typing import Any",
        "import pytest",
        "",
    ]
    
    for name, data in fixtures.items():
        if data:
            output_lines.append(format_fixture(name, data))
    
    output = "\n".join(output_lines)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"\nOutput written to: {args.output}")
    else:
        print(output)
    
    print("\n" + "=" * 60)
    print("Raw JSON (for inspection)")
    print("=" * 60)
    for name, data in fixtures.items():
        if data:
            print(f"\n### {name} ###")
            if isinstance(data, list):
                anonymized = anonymize_list(name, data)
            else:
                anonymized = anonymize_dict(data)
            print(json.dumps(anonymized, indent=2))


if __name__ == "__main__":
    main()
