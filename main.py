import json
from collections import defaultdict
from pathlib import Path

from models import Activity, ActivitiesResponse, Holding

# Path to the local JSON file to load (relative to this script's directory)
# JSON_FILE = Path(__file__).parent / "data.json"
activities_json = Path(__file__).parent / ""
holdings_json = Path(__file__).parent  / ""


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def group_activities_by_identifier(
    response: ActivitiesResponse,
) -> dict[str, list[Activity]]:
    """Group all activities by their asset identifier."""
    groups: dict[str, list[Activity]] = defaultdict(list)
    for activity in response.activities:
        if activity.asset is None:
            continue
        groups[activity.asset.identifier].append(activity)
    return dict(groups)


def main() -> None:
    if not activities_json.exists():
        print(f"Error: JSON file not found: {activities_json}")
        return

    activities_data = load_json(activities_json)
    activities_response = ActivitiesResponse.from_dict(activities_data)
    activities_groups = group_activities_by_identifier(activities_response)

    holdings_data = load_json(holdings_json)
    holdings_response = Holding.from_dict(holdings_data)

    for identifier, activities in activities_groups.items():
        asset_name_text = None
        total = 0.0
        for activity in activities:
            total += activity.amount or 0.0
            for holding in holdings_response:
                if holding.asset.identifier == activity.asset.identifier:
                    asset_name_text = holding.sharedAsset.name

        print(f"{asset_name_text}")
        print("Summe: " + str(round(total, 2)) + "€")


if __name__ == "__main__":
    main()
