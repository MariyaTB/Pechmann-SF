#!/usr/bin/env python3
import os
import csv
import re

csv_file = "excitation_energies.csv"

# Initialize CSV with header if it doesn't exist
header = ["filename", "triplet1_eV", "triplet2_eV", "singlet1_eV",
          "2T1_minus_S1", "2T1_minus_T2", "HOMO", "LUMO"]

if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def extract_values(filepath):
    triplets, singlets = [], []
    homo, lumo = None, None

    with open(filepath, "r", errors="ignore") as f:
        lines = f.readlines()

    # Extract excited states
    for line in lines:
        if "Excited State" in line:
            if "Triplet-A" in line:
                match = re.search(r"Triplet-A\s+(\d+\.\d+)", line)
                if match:
                    triplets.append(float(match.group(1)))
            elif "Singlet-A" in line:
                match = re.search(r"Singlet-A\s+(\d+\.\d+)", line)
                if match:
                    singlets.append(float(match.group(1)))

    # Extract HOMO (last Alpha occ. eigenvalues line)
    for line in reversed(lines):
        if "Alpha  occ. eigenvalues" in line:
            parts = line.split("--")
            if len(parts) > 1:
                values = parts[1].split()
                homo = float(values[-1]) if values else None
            break

    # Extract LUMO (first Alpha virt. eigenvalues line)
    for line in lines:
        if "Alpha  virt. eigenvalues" in line:
            parts = line.split("--")
            if len(parts) > 1:
                values = parts[1].split()
                lumo = float(values[0]) if values else None
            break

    # Assign values
    triplet1 = triplets[0] if len(triplets) > 0 else None
    triplet2 = triplets[1] if len(triplets) > 1 else None
    singlet1 = singlets[0] if len(singlets) > 0 else None

    # Calculations
    twot1_minus_s1 = (2*triplet1 - singlet1) if (triplet1 is not None and singlet1 is not None) else None
    twot1_minus_t2 = (2*triplet1 - triplet2) if (triplet1 is not None and triplet2 is not None) else None

    return [os.path.basename(filepath), triplet1, triplet2, singlet1,
            twot1_minus_s1, twot1_minus_t2, homo, lumo]

# Read existing filenames from CSV to avoid duplicates
existing_files = set()
with open(csv_file, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if row:
            existing_files.add(row[0])

# Process all .log files
results = []
for file in os.listdir("."):
    if file.endswith(".log") and file not in existing_files:
        results.append(extract_values(file))

# Append new rows
if results:
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)

# Sort CSV by filename (descending, like sort -r)
with open(csv_file, "r") as f:
    rows = list(csv.reader(f))

header, data = rows[0], rows[1:]
data.sort(key=lambda x: x[0], reverse=True)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)
