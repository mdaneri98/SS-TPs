import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_pressure_data(velocity_path, dt=0.05):
    iter_path = velocity_path / "0"
    pressure_file = iter_path / "pressure.csv"

    if pressure_file.exists():
        df = pd.read_csv(pressure_file)
        df['time_bin'] = (df['time'] // dt) * dt
        grouped = df.groupby('time_bin').sum().reset_index()

        # Calcular el promedio de las presiones en las paredes
        wall_columns = ['bottom', 'right', 'top', 'left']
        grouped['average_pressure'] = grouped[wall_columns].mean(axis=1)

        return grouped.iloc[:-2]  # Remove last 2 rows
    return None

def plot_pressure(solution_type, dt):
    base_path = Path(f"outputs/{solution_type}")
    if not base_path.exists():
        print(f"Error: No se encontró el directorio {base_path}")
        return

    output_dir = Path("outputs/analysis/pressures")
    output_dir.mkdir(parents=True, exist_ok=True)

    velocity_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("v_")]
    velocity_dirs.sort(key=lambda x: float(x.name.split('_')[1]))

    if not velocity_dirs:
        print(f"Error: No se encontraron directorios de velocidad en {base_path}")
        return

    colors = sns.color_palette("husl", 6)  # Agregamos un color más para el promedio

    for vel_dir in velocity_dirs:
        try:
            velocity = float(vel_dir.name.split('_')[1])
            print(f"Procesando velocidad {velocity}...")

            pressure_df = load_pressure_data(vel_dir, dt)
            if pressure_df is None:
                print(f"No se encontraron datos para velocidad {velocity}")
                continue

            plt.figure(figsize=(12, 6))

            for col_idx, col in enumerate(['static']):
                plt.plot(pressure_df['time_bin'], pressure_df[col],
                         label=col, color=colors[col_idx], linewidth=1, alpha=1)

            # Agregar la curva del promedio
            plt.plot(pressure_df['time_bin'], pressure_df['average_pressure'],
                     label='Promedio de las paredes', color=colors[5], linewidth=1)

            plt.xlabel('Tiempo (s)', fontsize=12)
            plt.ylabel('Presión (N/m)', fontsize=12)
            plt.legend(fontsize=10)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            plt.savefig(output_dir / f"pressure_{solution_type}_v{velocity:.2f}.png",
                        dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"Error procesando velocidad {velocity}: {str(e)}")
            continue

def main():
    dt = 0.05
    try:
        for solution_type in ["fixed_solution"]:
            print(f"\nProcessing {solution_type}...")
            plot_pressure(solution_type, dt)
    except Exception as e:
        print(f"Execution error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    exit(main())