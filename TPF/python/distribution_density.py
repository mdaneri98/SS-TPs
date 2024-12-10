import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def read_doors(file_path):
    df = pd.read_csv(file_path, skiprows=1, header=None)
    return df.astype(float).values.tolist()

def calculate_circular_density(ct_value, p_value, radius=3):
    input_path = Path('outputs/probabilistic_analysis') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path = Path('plots/circular_density') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Processing ct={ct_value}, p={p_value:.2f}")
    print(f"Input path: {input_path}")

    if not input_path.exists():
        print(f"Directory not found: {input_path}")
        return None, None

    # Almacenar datos de todas las simulaciones
    all_sims_densities = []
    all_sims_times = []

    # Procesar cada simulación
    for sim_dir in input_path.glob('sim_*'):
        try:
            # Read door positions (usar la primera simulación como referencia)
            if len(all_sims_densities) == 0:
                doors = read_doors(sim_dir / 'doors.csv')
                door_centers = []
                for door in doors:
                    center_x = (door[0] + door[2]) / 2
                    center_y = (door[1] + door[3]) / 2
                    door_centers.append([center_x, center_y])
                door_centers = np.array(door_centers)
                centroid = np.mean(door_centers, axis=0)
                all_centers = np.vstack([door_centers, centroid])

            # Read dynamic data
            dynamic_data = []
            with open(sim_dir / 'dynamic.txt', 'r') as f:
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

            all_sims_densities.append(circle_densities)
            all_sims_times.append(times)

        except Exception as e:
            print(f"Error processing {sim_dir}: {str(e)}")
            continue

    if not all_sims_densities:
        print(f"No valid simulations found for ct={ct_value}, p={p_value}")
        return None, None

    # Encontrar la longitud mínima de tiempo para alinear las simulaciones
    min_time_len = min(len(t) for t in all_sims_times)
    reference_times = all_sims_times[0][:min_time_len]

    # Alinear todas las simulaciones a la misma longitud
    aligned_densities = []
    for sim_densities in all_sims_densities:
        aligned_sim = [door_density[:min_time_len] for door_density in sim_densities]
        aligned_densities.append(aligned_sim)

    # Convertir a array para facilitar cálculos
    densities_array = np.array(aligned_densities)  # [n_sims, n_doors, n_times]

    # Calcular promedio y desviación estándar entre simulaciones
    mean_densities = np.mean(densities_array, axis=0)  # [n_doors, n_times]
    std_densities = np.std(densities_array, axis=0)    # [n_doors, n_times]

    # Plot densities over time with error bands
    plt.figure(figsize=(12, 8))
    for i in range(len(door_centers)):
        plt.plot(reference_times, mean_densities[i], label=f'Door {i+1}')
        plt.fill_between(reference_times,
                         mean_densities[i] - std_densities[i],
                         mean_densities[i] + std_densities[i],
                         alpha=0.2)

    # Plot centroid
    plt.plot(reference_times, mean_densities[-1], label='Centroid', linestyle='--', linewidth=2)
    plt.fill_between(reference_times,
                     mean_densities[-1] - std_densities[-1],
                     mean_densities[-1] + std_densities[-1],
                     alpha=0.2)

    plt.title(f'Average Particle Density in Circles\n(ct={ct_value}, p={p_value:.2f}, r={radius})')
    plt.xlabel('Time (s)')
    plt.ylabel('Density (particles/unit area)')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path / 'circular_density.png', bbox_inches='tight', dpi=300)
    plt.close()

    # Guardar datos en CSV
    data_dict = {'Time': reference_times}
    for i in range(len(door_centers)):
        data_dict[f'Door_{i+1}_Mean'] = mean_densities[i]
        data_dict[f'Door_{i+1}_Std'] = std_densities[i]
    data_dict['Centroid_Mean'] = mean_densities[-1]
    data_dict['Centroid_Std'] = std_densities[-1]

    df = pd.DataFrame(data_dict)
    df.to_csv(output_path / 'circular_density_stats.csv', index=False)

    return reference_times, mean_densities, std_densities

def analyze_circular_density_variation(ct_value, p_value, radius=3):
    output_path = Path('plots/circular_density_variation') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path.mkdir(parents=True, exist_ok=True)

    times, mean_densities, std_densities = calculate_circular_density(ct_value, p_value, radius)
    if times is None:
        return

    # Calculate overall statistics across all circles
    mean_across_circles = np.mean(mean_densities, axis=0)
    std_across_circles = np.mean(std_densities, axis=0)

    # Plot mean density
    plt.figure(figsize=(12, 6))
    plt.plot(times, mean_across_circles)
    plt.fill_between(times,
                     mean_across_circles - std_across_circles,
                     mean_across_circles + std_across_circles,
                     alpha=0.2)
    plt.title(f'Mean Circular Density over Time\n(ct={ct_value}, p={p_value:.2f}, r={radius})')
    plt.xlabel('Time (s)')
    plt.ylabel('Average Density')
    plt.grid(True)
    plt.savefig(output_path / 'circular_density_mean.png', bbox_inches='tight', dpi=300)
    plt.close()

    # Save statistics to CSV
    stats_df = pd.DataFrame({
        'Time': times,
        'Mean_Density': mean_across_circles,
        'Std_Density': std_across_circles
    })
    stats_df.to_csv(output_path / 'density_variation_stats.csv', index=False)

if __name__ == "__main__":
    ct_values = [10, 20, 30]  # Valores de ct para analizar
    p_values = [0.0, 0.5, 1.0]  # Valores de p para analizar
    radius = 3  # Radio de las circunferencias

    for ct in ct_values:
        for p in p_values:
            calculate_circular_density(ct, p, radius)
            analyze_circular_density_variation(ct, p, radius)