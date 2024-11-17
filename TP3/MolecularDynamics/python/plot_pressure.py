import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import savgol_filter
from pathlib import Path

def load_pressure_data(velocity_path):
    """
    Carga los datos de presión únicamente de la iteración 0
    """
    iter_path = velocity_path / "0"  # Solo iteración 0
    pressure_file = iter_path / "pressure.csv"

    if pressure_file.exists():
        return pd.read_csv(pressure_file)
    return None

def plot_smoothed_pressure(solution_type):
    """
    Genera gráficos de presión para la iteración 0 de cada velocidad
    """
    base_path = Path(f"outputs/{solution_type}")
    if not base_path.exists():
        print(f"Error: No se encontró el directorio {base_path}")
        return

    # Crear directorio de salida
    output_dir = Path("outputs/analysis/pressures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Buscar directorios de velocidad
    velocity_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("v_")]
    velocity_dirs.sort(key=lambda x: float(x.name.split('_')[1]))

    if not velocity_dirs:
        print(f"Error: No se encontraron directorios de velocidad en {base_path}")
        return

    colors = sns.color_palette("husl", 5)
    window = 51  # Ventana de suavizado (debe ser impar)
    poly_order = 3

    # Procesar cada velocidad
    for vel_dir in velocity_dirs:
        try:
            velocity = float(vel_dir.name.split('_')[1])
            print(f"Procesando velocidad {velocity}...")

            # Cargar datos de la iteración 0
            pressure_df = load_pressure_data(vel_dir)
            if pressure_df is None:
                print(f"No se encontraron datos para velocidad {velocity}")
                continue

            # Crear figura para esta velocidad
            plt.figure(figsize=(12, 6))

            # Graficar cada componente
            for col_idx, col in enumerate(['bottom', 'right', 'top', 'left', 'static']):
                if len(pressure_df[col]) > window:
                    smoothed_values = savgol_filter(pressure_df[col], window, poly_order)
                else:
                    smoothed_values = pressure_df[col]

                # Plotear línea principal
                plt.plot(pressure_df['time'], smoothed_values,
                         label=col, color=colors[col_idx], linewidth=2)

            plt.xlabel('Tiempo (s)', fontsize=12)
            plt.ylabel('Presión', fontsize=12)
            plt.title(f'Evolución de la Presión - {solution_type.replace("_", " ").title()}\nVelocidad: {velocity:.2f} (Iteración 0)',
                      fontsize=14)
            plt.legend(fontsize=10)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Guardar gráfico en el directorio específico
            plt.savefig(output_dir / f"pressure_{solution_type}_v{velocity:.2f}.png",
                        dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"Error procesando velocidad {velocity}: {str(e)}")
            continue

def main():
    try:
        for solution_type in ["fixed_solution"]:
            print(f"\nProcesando {solution_type}...")
            plot_smoothed_pressure(solution_type)

    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())