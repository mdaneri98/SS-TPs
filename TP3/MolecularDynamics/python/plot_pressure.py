import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import savgol_filter
import os
import glob

def plot_smoothed_pressure(base_directory):
    # Buscar todas las subcarpetas de velocidad
    velocity_dirs = glob.glob(os.path.join(base_directory, "v_*"))

    if not velocity_dirs:
        print(f"Error: No se encontraron directorios de velocidad en {base_directory}")
        return

    # Configurar el estilo general
    plt.style.use('default')
    colors = sns.color_palette("husl", 5)

    # Crear un subplot para cada velocidad
    n_velocities = len(velocity_dirs)
    fig, axes = plt.subplots(n_velocities, 1, figsize=(12, 6*n_velocities))
    if n_velocities == 1:
        axes = [axes]

    # Parámetros de suavizado
    window = 51  # Debe ser impar
    poly_order = 3

    # Procesar cada directorio de velocidad
    for idx, vel_dir in enumerate(sorted(velocity_dirs)):
        pressure_path = os.path.join(vel_dir, "pressure.csv")

        if not os.path.exists(pressure_path):
            print(f"Error: Archivo no encontrado en {pressure_path}")
            continue

        # Leer datos
        pressure_df = pd.read_csv(pressure_path)

        # Obtener la velocidad del nombre del directorio
        velocity = float(os.path.basename(vel_dir).split('_')[1])

        # Graficar en el subplot correspondiente
        ax = axes[idx]

        # Suavizar y graficar cada curva
        for col_idx, col in enumerate(['bottom', 'right', 'top', 'left', 'static']):
            # Aplicar filtro Savitzky-Golay para suavizar la curva
            if len(pressure_df[col]) > window:
                smoothed = savgol_filter(pressure_df[col], window, poly_order)
            else:
                smoothed = pressure_df[col]

            ax.plot(pressure_df['time'], smoothed, label=col, color=colors[col_idx], linewidth=2)

        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Presión')
        ax.set_title(f'Evolución de la Presión - Velocidad: {velocity:.2f}')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # Ajustar el espaciado entre subplots
    plt.tight_layout()

    # Guardar y mostrar
    output_dir = os.path.join(base_directory, "plots")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "pressure_curves.png"), dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plot_smoothed_pressure("outputs/fixed_solution")