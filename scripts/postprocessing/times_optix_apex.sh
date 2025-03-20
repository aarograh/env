#!/home/aaron/miniconda3/envs/sbir_opt/bin/python
import os
import re
import numpy as np

def find_solution_times(root_dir="."):
    """Recursively find .out files, extract solution times, and compute statistics."""
    solution_times = []
    pattern = re.compile(r"TOTAL SOLUTION TIME \[S\]:\s+([\d.]+)")
    step_times = {}

    # Walk through all directories and find .out files
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".out"):
                filepath = os.path.join(dirpath, filename)
                if "tmp" in filepath:
                    step_index = int(filepath.split("tmp/")[1].split("/")[0])
                else:
                    step_index = -1

                # Read the file and search for the time
                with open(filepath, "r") as f:
                    for line in f:
                        match = pattern.search(line)
                        if match:
                            solution_times.append(float(match.group(1)))
                            if step_index > -1:
                                if step_index not in step_times:
                                    step_times[step_index] = []
                                step_times[step_index].append(float(match.group(1)))
                            break  # Stop reading after finding the first match

    if not solution_times:
        print("No solution times found.")
        return

    print("| Step Index |  Num Files |   Min   Max  Mean |")
    for step_index in sorted(list(step_times.keys())):
        times = np.array(step_times[step_index])
        print(f"|       {step_index:>04d} |       {times.size:>04d} | {times.min():.3f} {times.max():.3f} {times.mean():.3f} |")

    # Compute statistics
    solution_times = np.array(solution_times)
    print(f"Files Processed: {len(solution_times)}")
    print(f"Min Time: {solution_times.min():.3f} s")
    print(f"Max Time: {solution_times.max():.3f} s")
    print(f"Mean Time: {solution_times.mean():.3f} s")
    print(f"Std Dev: {solution_times.std():.3f} s")

# Run the script
find_solution_times()

