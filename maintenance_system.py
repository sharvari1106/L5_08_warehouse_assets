"""Warehouse Asset Maintenance Registry.

Registers warehouse machines, records service dates, raises alerts for
overdue inspections and exports a JSON report.
"""

import json
import tempfile
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SERVICE_INTERVAL_DAYS = 90


class MaintenanceRegistry:
    """Holds the registered assets and the inspection interval."""

    def __init__(self, service_interval_days=DEFAULT_SERVICE_INTERVAL_DAYS):
        self.assets = {}
        self.registration_log = []
        self.service_interval_days = service_interval_days

    def register_asset(self, asset_id, machine_type):
        """Register a new machine; reject blank or duplicate IDs."""
        asset_id = asset_id.strip()
        if not asset_id:
            print("Rejected registration: asset ID is empty")
            return False
        if asset_id in self.assets:
            print("Rejected registration:", asset_id, "is already registered",
                  "as a", self.assets[asset_id]["type"])
            return False
        self.assets[asset_id] = {
            "type": machine_type,
            "last_service": datetime.now().strftime(DATE_FORMAT),
        }
        self.registration_log.append(asset_id)
        print("Registered", asset_id, "- total registrations this run:",
              len(self.registration_log))
        return True

    def update_service_date(self, asset_id, date):
        """Record a service date given as YYYY-MM-DD (not in the future)."""
        if asset_id not in self.assets:
            print("Could not update", asset_id, "- no such asset")
            return False
        try:
            parsed = datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            print("Could not update", asset_id, "- invalid date", repr(date),
                  "(expected YYYY-MM-DD)")
            return False
        if parsed > datetime.now():
            print("Could not update", asset_id, "- date", date,
                  "is in the future")
            return False
        self.assets[asset_id]["last_service"] = date
        return True

    def due_for_inspection(self):
        """Return the IDs of assets whose last service is overdue."""
        limit = timedelta(days=self.service_interval_days)
        now = datetime.now()
        return [
            asset_id for asset_id, info in self.assets.items()
            if now - datetime.strptime(info["last_service"], DATE_FORMAT)
            > limit
        ]

    def change_interval(self, days):
        """Set the inspection interval; it must be a positive whole number."""
        if not isinstance(days, int) or days <= 0:
            print("Rejected interval", days,
                  "- must be a positive number of days; keeping",
                  self.service_interval_days)
            return False
        self.service_interval_days = days
        return True

    def print_alerts(self):
        """Print an alert line for every overdue asset."""
        for asset_id in self.due_for_inspection():
            print("ALERT: inspection overdue for", asset_id,
                  self.assets[asset_id]["type"])

    def export_service_report(self, file="maintenance.json"):
        """Write all assets to a JSON report file."""
        with open(file, "w", encoding="utf-8") as report:
            json.dump(self.assets, report, indent=2)
        print("Report written to " + file)

    def write_scratch_copy(self):
        """Write a scratch copy of the registry to a secure temp file."""
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False,
                encoding="utf-8") as scratch:
            json.dump(self.assets, scratch)
            path = scratch.name
        print("Scratch copy at", path)


def main():
    """Run a demo session, including some deliberately bad inputs."""
    registry = MaintenanceRegistry()
    registry.register_asset("FL-01", "Forklift")
    registry.register_asset("CV-07", "Conveyor")
    registry.register_asset("", "Pallet Jack")
    registry.register_asset("FL-01", "Crane")
    registry.update_service_date("FL-01", "2025-01-15")
    registry.update_service_date("XX-99", "2025-02-01")
    registry.change_interval(-30)
    answer = input("Last service date for CV-07 (YYYY-MM-DD, Enter to skip): ")
    if answer.strip():
        registry.update_service_date("CV-07", answer.strip())
    if not registry.assets:
        print("No assets registered; nothing to report.")
        return
    registry.print_alerts()
    registry.export_service_report()
    registry.write_scratch_copy()


if __name__ == "__main__":
    main()
