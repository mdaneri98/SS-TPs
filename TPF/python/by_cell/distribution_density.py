import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

def calculate_average_density(p_value, nx, ny):
    input_path = Path('../outputs/probabilistic_analysis') / f'p_{p_value:.2f}' / 'sim_000'
    output_path = Path('../density') / f'p_{p_value:.2f}'
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

    # Ajustamos los límites del campo a 30x30
    x_min, x_max = 0, 30
    y_min, y_max = 0, 30

    # Creamos bordes para celdas de 1x1
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # El área de cada celda es 1x1 = 1
    cell_area = 1

    total_density = np.zeros((nx, ny))
    valid_states = 0

    for state in dynamic_data:
        positions = np.array([[p[1], p[2]] for p in state['particles']])
        if len(positions) > 0:
            H, _, _ = np.histogram2d(positions[:, 0], positions[:, 1],
                                     bins=[x_edges, y_edges])
            total_density += H
            valid_states += 1

    avg_density = total_density / (valid_states * cell_area)

    plt.figure(figsize=(12, 10))

    # Ajustamos el heatmap para mostrar coordenadas correctas
    sns.heatmap(avg_density.T, cmap='YlOrRd',
                xticklabels=np.arange(0, nx),
                yticklabels=np.arange(0, ny)[::-1],  # Invertimos para coordenadas correctas
                cbar_kws={'label': 'Average Particles per Cell'})

    plt.title(f'Average Particle Density (p={p_value})')
    plt.xlabel('X position')
    plt.ylabel('Y position')

    # Ajustamos los ticks para mostrar cada 5 unidades
    plt.xticks(np.arange(0, nx + 1, 5))
    plt.yticks(np.arange(0, ny + 1, 5))

    plt.savefig(output_path / 'avg_density.png', bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    x_max, y_max = 30, 30  # Campo de 30x30
    nx, ny = x_max, y_max  # Cada celda es de 1x1
    p_values = np.arange(0, 1.1, 0.1)
    for p in p_values:
        calculate_average_density(p, nx, ny)