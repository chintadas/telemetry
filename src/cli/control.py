"""
CLI Control Utility for Liquid Cooling Engine Simulation & Fault Injection.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error


def send_post_request(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print(f"Success ({response.status}): {res_body}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Liquid Cooling Loop Simulation CLI Controller")
    parser.add_argument("--host", default="http://localhost:8000", help="Mock engine server host URL")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # heat-load
    heat_parser = subparsers.add_parser("heat-load", help="Set simulated workload heat load in Watts")
    heat_parser.add_argument("watts", type=float, help="Heat load value in Watts (e.g. 15000)")

    # pump-rpm
    pump_parser = subparsers.add_parser("pump-rpm", help="Set pump speed in RPM")
    pump_parser.add_argument("rpm", type=float, help="Pump RPM value (e.g. 2500)")

    # fault
    fault_parser = subparsers.add_parser("inject-fault", help="Inject fault scenario")
    fault_parser.add_argument(
        "fault_type",
        choices=["pump_failure", "leak", "thermal_surge"],
        help="Fault scenario type",
    )

    # reset
    subparsers.add_parser("reset", help="Clear all fault scenarios and reset state")

    args = parser.parse_args()

    if args.command == "heat-load":
        send_post_request(f"{args.host}/api/v1/simulation/heat_load", {"watts": args.watts})
    elif args.command == "pump-rpm":
        send_post_request(f"{args.host}/api/v1/simulation/pump_rpm", {"rpm": args.rpm})
    elif args.command == "inject-fault":
        send_post_request(f"{args.host}/api/v1/simulation/fault", {"fault_type": args.fault_type})
    elif args.command == "reset":
        send_post_request(f"{args.host}/api/v1/simulation/reset", {})


if __name__ == "__main__":
    main()
