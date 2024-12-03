import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

def get_evacuation_time(dynamic_file):
    with open(dynamic_file, 'r') as f:
        times = []
        for line in f:
            try:
                time = float(line.strip())
                times.append(time)
            except ValueError:
                continue
        return max(times) if times else 0

def analyze_p_values():
    base_dir = Path('outputs/probabilistic_analysis')
    p_times = {}
    output_dir = Path('times')
    output_dir.mkdir(exist_ok=True)

    for p_dir in base_dir.glob('p_*'):
        try:
            p_value = float(p_dir.name.split('_')[1])
            times = []

            for sim_dir in p_dir.glob('sim_*'):
                dynamic_file = sim_dir / 'dynamic.txt'
                if dynamic_file.exists():
                    evac_time = get_evacuation_time(dynamic_file)
                    if evac_time > 0:
                        times.append(evac_time)

            if times:
                p_times[p_value] = times
        except Exception as e:
            print(f"Error processing {p_dir}: {e}")

    if not p_times:
        print("No valid data found")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    p_values = sorted(p_times.keys())
    means = [np.mean(p_times[p]) for p in p_values]
    stds = [np.std(p_times[p]) for p in p_values]

    ax.errorbar(p_values, means, yerr=stds, fmt='o-', capsize=5)
    ax.set_xlabel('p value')
    ax.set_ylabel('Evacuation Time (s)')
    ax.set_title('Average Evacuation Time vs p Value')
    ax.grid(True)

    plt.savefig(output_dir / 'evacuation_times.png')

    results_df = pd.DataFrame({
        'p_value': p_values,
        'mean_time': means,
        'std_dev': stds
    })
    results_df.to_csv(output_dir / 'evacuation_times.csv', index=False)

if __name__ == '__main__':
    analyze_p_values()