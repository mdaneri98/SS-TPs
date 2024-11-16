import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from glob import glob
import os
import re

def get_velocities_from_dirs(base_path):
    """Obtiene las velocidades disponibles de los directorios existentes"""
    # Busca directorios que coincidan con el patrón v_X.XX
    paths = glob(os.path.join(base_path, "v_*"))
    velocities = []
    for path in paths:
        # Extrae el número de velocidad del nombre del directorio
        match = re.search(r'v_(\d+\.\d+)', path)
        if match:
            velocities.append(float(match.group(1)))
    return sorted(velocities)

def read_collision_data(solution_type, velocity):
    """Lee los datos de colisiones para una solución y velocidad específica"""
    path = f"outputs/{solution_type}_solution/v_{velocity:.2f}/count.csv"
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        print(f"No se encontró el archivo: {path}")
        return None

def plot_collisions_comparison():
    # Obtener las velocidades disponibles para ambas soluciones
    common_velocities = get_velocities_from_dirs("outputs/common_solution")
    fixed_velocities = get_velocities_from_dirs("outputs/fixed_solution")

    # Usar solo las velocidades que están presentes en ambos conjuntos
    velocities = sorted(list(set(common_velocities) & set(fixed_velocities)))

    if not velocities:
        print("No se encontraron velocidades comunes entre las soluciones")
        return

    # Configurar el estilo de las gráficas
    plt.style.use('default')

    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Paleta de colores para las diferentes velocidades
    colors = plt.cm.viridis(np.linspace(0, 1, len(velocities)))

    # Plotear para cada velocidad
    for v, color in zip(velocities, colors):
        # Leer datos
        common_data = read_collision_data('common', v)
        fixed_data = read_collision_data('fixed', v)

        if common_data is not None and fixed_data is not None:
            # Plot para datos common
            ax1.plot(common_data['time'], common_data['static'],
                     label=f'v = {v:.2f} (común)',
                     color=color, linestyle='-')
            ax2.plot(fixed_data['time'], fixed_data['static'],
                     label=f'v = {v:.2f} (fijo)',
                     color=color, linestyle='-')

    # Configurar primer subplot (common solution)
    ax1.set_xlabel('Tiempo (s)')
    ax1.set_ylabel('Número de colisiones')
    ax1.set_title('Solución con masa variable')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Configurar segundo subplot (fixed solution)
    ax2.set_xlabel('Tiempo (s)')
    ax2.set_ylabel('Número de colisiones')
    ax2.set_title('Solución con masa fija')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Ajustar layout
    plt.tight_layout()

    # Guardar figura
    plt.savefig('collision_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Imprimir velocidades analizadas
    print("\nVelocidades analizadas:", velocities)

if __name__ == "__main__":
    plot_collisions_comparison()