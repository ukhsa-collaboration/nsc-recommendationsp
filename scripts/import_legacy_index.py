import json
import os
from nsc.policy.models import Policy
from nsc.utils.markdown import convert

def run():
    fixture_path = "fixtures/legacy_index.json"
    if not os.path.exists(fixture_path):
        print(f"Could not find fixture file: {fixture_path}")
        return

    with open(fixture_path) as f:
        data = json.load(f)

    if not data:
        print("No data to import. legacy_index.json is empty.")
        return

    count = 0
    for item in data:
        if not item.get("name") or not item.get("url"):
            continue

        obj, created = Policy.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "ages": item["ages"],
                "is_active": item["is_active"],
                "recommendation": item["recommendation"],
                "condition": item.get("condition", ""),
                "summary": item.get("summary", ""),
                "background": item.get("background", ""),
                "condition_html": convert(item.get("condition", "")),
                "summary_html": convert(item.get("summary", "")),
                "background_html": convert(item.get("background", "")),
            },
        )
        print(f"{'Created' if created else 'Updated'}: {obj.name}")
        count += 1 if created else 0

    print(f"\nImported or updated {count} policies.")
