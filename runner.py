import subprocess
import pandas as pd # Great for the score table
import numpy as np
import argparse
import yaml

from solvers.sudokusolver import Sudoku

def validate_solution(board_str):
    # convert to array, then use _check()
    arr = np.array(list(map(int, board_str)))
    return Sudoku._check(arr)

def run_external_solver(command_list):
    # This runs the command and waits for it to finish
    result = subprocess.run(
        command_list, 
        capture_output=True, 
        text=True  # This turns the raw bytes into a Python string
    )
    
    # result.stdout now contains everything the solver printed
    output = result.stdout
    print(output)
    
    # Now we parse the string to find our data
    data = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key] = value
            
    return data # Returns {'SOLUTION': '123...', 'TIME_NS': '4500'} -- many options for expansion

def getAllSudokuPaths(config):
    mixed = config.get('sudokus', [])
    res = list(map(lambda dict: dict.get("easy"), mixed)) + list(map(lambda dict: dict.get("medium"), mixed))
    return list(filter(lambda x: x is not None, res))


def getDataForAllSolversAllSudokus(n = 10, config_path = "config.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    index = 0
    files_run = []

    results = []

    for solver in config.get('solvers', []):
        name = solver.get('name')
        build_cmd = solver.get('build')
        cwd = solver.get('cwd')
        run_cmd = solver.get('command')
        index = files_run.count(run_cmd) # use the next version of the solver

        files_run.append(run_cmd)
        
        print(f"--- Processing: {name} ---")

        # 3. Build it (if a build command exists)
        if build_cmd:
            print(f"Building {name}...")
            if cwd: subprocess.run(build_cmd, cwd=cwd, shell=True, check=True)
            else: subprocess.run(build_cmd, shell=True, check=True)

        times = [] # collect all times for the different sudokus
        correct = 0

        for spath in getAllSudokuPaths(config):
            # 4. Prepare the run command with arguments
            # We append our specific test arguments to the base command
            # We split the base command and add our extra args
            full_command = run_cmd.split() + [spath, str(n), str(index)]
            
            print(f"Running: {' '.join(full_command)}")
            data = run_external_solver(full_command)
            language = data.get("LANGUAGE")
            times.append(int(data.get("MEAN_TIME_NS")))
            if validate_solution(data.get("SOLUTION")):
                correct += 1

        avg_time_ms = sum(times)/1000000 # elements of times are already means for a single sudoku
        results.append({"Name": name, "Language": language, "Mean (ms)": avg_time_ms, "Correctness": float(correct)/len(spath)})
    return results
    
    


# ----------- solver api ------------
# takes:
#   path: String
#   number_it: int
#   which_solver: int
# 
# prints:
# SOLUTION:1235...
# MEAN_TIME_NS:8249368934
# LANGUAGE:Python
# -----------------------------------


def main():
    # first parse the arguments, namely 
    parser = argparse.ArgumentParser(description="Sudoku Solver")
    parser.add_argument("--path", type=str, default="all", help="Path to the sudoku .txt file")
    parser.add_argument("--runs", type=int, default=20, help="Number of times to run")
    
    args = parser.parse_args()

    if args.path == "all":
        results = getDataForAllSolversAllSudokus(n = args.runs)


    
    # Create the Score Table
    df = pd.DataFrame(results)
    summary = df.groupby("Name")["Mean (ms)"].mean().sort_values()
    print(summary)



if __name__ == "__main__":
    main()


# "✅" if is_correct else "❌" save for later
"""
https://www.markdownguide.org/extended-syntax/
maybe sort by mean time
| Name | Language | Mean Time | approach |
| :--- | :--- | :---: | ---: |
| Left Aligned | Centered | Right Aligned |
| Content 1 | Content 2 | Content 3 |

some extra information: sudokus tested,
"""
