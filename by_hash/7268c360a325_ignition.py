#!/usr/bin/env python3
"""JANUS IGNITION — Boot the entire system, run diagnostics, and start a derby round."""

import sys, os
sys.path.insert(0, os.path.expanduser("~/RootBase/Janus"))

from core.janus_system import JanusSystem

if __name__ == "__main__":
    print("🚀 IGNITION SEQUENCE")
    system = JanusSystem()
    status = system.ignition()
    for comp, green in status.items():
        if comp != "all_systems_nominal":
            print(f"  {'✅' if green else '❌'} {comp}")
    if status["all_systems_nominal"]:
        print("\n✅ ALL SYSTEMS NOMINAL\n")
        report = system.system_report()
        for k, v in report.items():
            print(f"  {k}: {v}")
        print("\n🏆 Current leader: " + report["leader"])
        print("🎡 " + report["rideOfDay"])
    else:
        print("\n❌ Some systems degraded. Check smoke_test.py for details.")
