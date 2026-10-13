import csv
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

MEASURES = {
    "HKQuantityTypeIdentifierWalkingSpeed": ("walking_speed", "mean"),
    "HKQuantityTypeIdentifierWalkingStepLength": ("step_length", "mean"),
    "HKQuantityTypeIdentifierWalkingAsymmetryPercentage": ("asymmetry", "mean"),
    "HKQuantityTypeIdentifierWalkingDoubleSupportPercentage": ("double_support", "mean"),
    "HKQuantityTypeIdentifierStepCount": ("step_count", "sum"),
}


def to_standard_unit(value, unit, measure):
    unit = unit.lower()
    if measure == "walking_speed":
        return {"km/hr": value / 3.6, "mi/hr": value * 0.44704, "ft/s": value * 0.3048}.get(unit, value)
    if measure == "step_length":
        return {"m": value * 100.0, "in": value * 2.54, "ft": value * 30.48}.get(unit, value)
    if measure in ("asymmetry", "double_support"):
        return value * 100.0 if 0.0 <= value <= 1.0 else value
    return value


def is_iphone(device):
    device = device.lower()
    return "name:iphone" in device or "model:iphone" in device


def parse(xml_path):
    totals = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    context = ET.iterparse(xml_path, events=("start", "end"))
    _, root = next(context)
    for event, elem in context:
        if event == "end" and elem.tag == "Record":
            record_type = elem.get("type")
            date = (elem.get("startDate") or "")[:10]
            if record_type in MEASURES and date and is_iphone(elem.get("device", "")):
                measure = MEASURES[record_type][0]
                try:
                    value = to_standard_unit(float(elem.get("value")), elem.get("unit", ""), measure)
                except (TypeError, ValueError):
                    pass
                else:
                    totals[date][measure][0] += value
                    totals[date][measure][1] += 1
            elem.clear()
            root.clear()
    return totals


def write_csv(totals, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date"] + [name for name, _ in MEASURES.values()])
        for date in sorted(totals):
            row = [date]
            for name, agg in MEASURES.values():
                total, n = totals[date].get(name, (0.0, 0))
                row.append("" if n == 0 else (total / n if agg == "mean" else total))
            writer.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python parse_apple_health.py export.xml output.csv")
    write_csv(parse(sys.argv[1]), sys.argv[2])
