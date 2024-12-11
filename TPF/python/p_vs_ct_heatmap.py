import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
from pathlib import Path

def get_evacuation_time(directory):
    """
    Extract evacuation time from a simulation directory by reading dynamic.txt
    Returns the time of the last state where particles were present
    """
    dynamic_file = os.path.join(directory, 'dynamic.txt')
    if not os.path.exists(dynamic_file):
        return None

    last_time_with_particles = None
    current_time = None

    with open(dynamic_file, 'r') as f:
        for line in f:
            line = line.strip()
            if ',' not in line:  # Es una línea de tiempo
                try:
                    current_time = float(line)
                except ValueError:
                    continue
            else:  # Es una línea de partícula
                last_time_with_particles = current_time

    return last_time_with_particles

def create_evacuation_heatmap():
    """
    Create a heatmap of maximum evacuation times based on p and ct parameters
    """
    # Get the current working directory and construct the path
    current_dir = Path.cwd()
    base_directory = current_dir / 'outputs' / 'probabilistic_analysis'

    # Check if directory exists
    if not base_directory.exists():
        print(f"Directory not found: {base_directory}")
        print("Current working directory:", current_dir)
        return

    # Initialize data structures
    data = []

    # Scan through all directories
    for dir_path in base_directory.glob('t_*'):
        if dir_path.is_dir():
            # Parse ct and p from directory name
            dir_name = dir_path.name
            try:
                parts = dir_name.split('_&_')
                ct = int(parts[0].split('_')[1])
                p = float(parts[1].split('_')[1])

                # Process all simulations for this parameter combination
                max_evac_time = 0  # Initialize with 0
                for sim_path in dir_path.glob('sim_*'):
                    if sim_path.is_dir():
                        evac_time = get_evacuation_time(sim_path)
                        if evac_time is not None:
                            max_evac_time = max(max_evac_time, evac_time)

                if max_evac_time > 0:  # Solo agregar si encontramos datos válidos
                    data.append({
                        'ct': ct,
                        'p': p,
                        'evacuation_time': max_evac_time
                    })

            except (IndexError, ValueError) as e:
                print(f"Error processing directory {dir_name}: {e}")

    if not data:
        print("No data found to create heatmap")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Pivot data for heatmap
    pivot_table = df.pivot(index='ct', columns='p', values='evacuation_time')

    # Sort indices to make them ascending
    pivot_table = pivot_table.sort_index(ascending=True)
    pivot_table = pivot_table.sort_index(axis=1, ascending=True)

    # Create heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table,
                cmap='YlOrRd',  # Higher values are red
                annot=True,
                fmt='.1f',
                cbar_kws={'label': 'Maximum Evacuation Time (seconds)'},
                xticklabels=True)

    plt.title('Maximum Evacuation Time by Critical Time (ct) and Probability (p)')
    plt.xlabel('Probability (p)')
    plt.ylabel('Critical Time (ct)')

    # Create output directories
    output_dir = current_dir / 'plots' / 'p_vs_ct'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save plot
    output_path = output_dir / 'evacuation_heatmap.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Heatmap saved to: {output_path}")

    # También guardar los datos en CSV para referencia
    csv_path = output_dir / 'evacuation_times.csv'
    df.to_csv(csv_path, index=False)
    print(f"Data saved to: {csv_path}")

if __name__ == "__main__":
    create_evacuation_heatmap()