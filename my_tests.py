import os
import time

num_trials = int(input("Number trials: "))
num_per_trial = int(input("Number to run in each trial: "))
output_file = input("Output file name: ")

for i in range(num_trials):
    command = f"python3 evaluate_heuristic >> {output_file} & " * num_per_trial
    os.system(command)
    time.sleep(120)
    print(f"Finished running trial {i}")