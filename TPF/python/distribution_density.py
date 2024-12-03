import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def read_doors(file_path):
    df = pd.read_csv(file_path, skiprows=1, header=None)
    return df.astype(float).values.tolist()

def calculate_circular_density(p_value, radius=3):
    input_path = Path('outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('circular_density') / f'p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    # Read door positions using the provided function
    doors = read_doors(input_path / 'doors.csv')

    # Calculate door centers
    door_centers = []
    for door in doors:
        center_x = (door[0] + door[2]) / 2
        center_y = (door[1] + door[3]) / 2
        door_centers.append([center_x, center_y])
    door_centers = np.array(door_centers)

    # Calculate centroid
    centroid = np.mean(door_centers, axis=0)
    all_centers = np.vstack([door_centers, centroid])

    # Read dynamic data
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

    # Calculate densities for each circle
    times = []
    circle_densities = [[] for _ in range(len(all_centers))]

    for state in dynamic_data:
        times.append(state['time'])
        positions = np.array([[p[1], p[2]] for p in state['particles']])

        for i, center in enumerate(all_centers):
            distances = np.sqrt(np.sum((positions - center)**2, axis=1))
            particles_in_circle = np.sum(distances <= radius)
            circle_area = np.pi * radius**2
            density = particles_in_circle / circle_area
            circle_densities[i].append(density)

    # Plot densities over time
    plt.figure(figsize=(12, 8))
    for i in range(len(door_centers)):
        plt.plot(times, circle_densities[i], label=f'Door {i+1}')
    plt.plot(times, circle_densities[-1], label='Centroid', linestyle='--', linewidth=2)

    plt.title(f'Particle Density in Circles (r={radius}, p={p_value})')
    plt.xlabel('Time')
    plt.ylabel('Density (particles/unit area)')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path / 'circular_density.png', bbox_inches='tight', dpi=300)
    plt.close()

def analyze_circular_density_variation(p_value, radius=3):
    input_path = Path('outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('circular_density_variation') / f'p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    # Read door positions using the provided function
    doors = read_doors(input_path / 'doors.csv')

    # Calculate door centers
    door_centers = []
    for door in doors:
        center_x = (door[0] + door[2]) / 2
        center_y = (door[1] + door[3]) / 2
        door_centers.append([center_x, center_y])
    door_centers = np.array(door_centers)

    # Calculate centroid
    centroid = np.mean(door_centers, axis=0)
    all_centers = np.vstack([door_centers, centroid])

    # Read dynamic data
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

    # Calculate densities and variations
    times = []
    mean_densities = []
    std_densities = []

    for state in dynamic_data:
        times.append(state['time'])
        positions = np.array([[p[1], p[2]] for p in state['particles']])

        current_densities = []
        for center in all_centers:
            distances = np.sqrt(np.sum((positions - center)**2, axis=1))
            particles_in_circle = np.sum(distances <= radius)
            circle_area = np.pi * radius**2
            density = particles_in_circle / circle_area
            current_densities.append(density)

        mean_densities.append(np.mean(current_densities))
        std_densities.append(np.std(current_densities))

    # Plot mean density
    plt.figure(figsize=(12, 6))
    plt.plot(times, mean_densities)
    plt.title(f'Mean Circular Density over Time (r={radius}, p={p_value})')
    plt.xlabel('Time')
    plt.ylabel('Average Density')
    plt.grid(True)
    plt.savefig(output_path / 'circular_density_mean.png', bbox_inches='tight', dpi=300)
    plt.close()

    # Plot density standard deviation
    plt.figure(figsize=(12, 6))
    plt.plot(times, std_densities)
    plt.title(f'Circular Density Standard Deviation over Time (r={radius}, p={p_value})')
    plt.xlabel('Time')
    plt.ylabel('Density Standard Deviation')
    plt.grid(True)
    plt.savefig(output_path / 'circular_density_std.png', bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    p_values = np.arange(0, 1.1, 0.1)
    radius = 3  # Radio de las circunferencias
    for p in p_values:
        calculate_circular_density(p, radius)
        analyze_circular_density_variation(p, radius)