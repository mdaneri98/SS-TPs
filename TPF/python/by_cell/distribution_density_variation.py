import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

def analyze_density_variation(p_value, nx, ny):
    input_path = Path('../outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('../density_variation') / f'p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    dynamic_data = []
    with open(input_path / 'dynamic.txt', 'r') as f:
        current_time = None
        particles = []
        for line in f:
            line = line.strip()
            if ',' not in line:
                if particles:
                    dynamic_data.append({'time': current_time, 'particles': particles})
                current_time = float(line)
                particles = []
            else:
                particle = list(map(float, line.split(',')))
                particles.append(particle)
        if particles:
            dynamic_data.append({'time': current_time, 'particles': particles})

    x_min, x_max = 0, 30
    y_min, y_max = 0, 30
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    times = []
    densities = []

    for state in dynamic_data:
        positions = np.array([[p[1], p[2]] for p in state['particles']])
        if len(positions) > 0:
            H, _, _ = np.histogram2d(positions[:, 0], positions[:, 1],
                                     bins=[x_edges, y_edges])
            times.append(state['time'])
            densities.append(H)

    densities = np.array(densities)

    # Plot mean density over time
    plt.figure(figsize=(12, 6))
    mean_density = np.mean(densities, axis=(1,2))
    plt.plot(times, mean_density)
    plt.title(f'Mean Particle Density over Time (p={p_value})')
    plt.xlabel('Time')
    plt.ylabel('Average Particles per Cell')
    plt.grid(True)
    plt.savefig(output_path / 'density_time_variation.png', bbox_inches='tight', dpi=300)
    plt.close()

    # Plot density standard deviation over time
    plt.figure(figsize=(12, 6))
    std_density = np.std(densities, axis=(1,2))
    plt.plot(times, std_density)
    plt.title(f'Particle Density Standard Deviation over Time (p={p_value})')
    plt.xlabel('Time')
    plt.ylabel('Std Dev of Particles per Cell')
    plt.grid(True)
    plt.savefig(output_path / 'density_variation_std.png', bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    x_max, y_max = 30, 30
    nx, ny = x_max, y_max
    p_values = np.arange(0, 1.1, 0.1)
    for p in p_values:
        analyze_density_variation(p, nx, ny)