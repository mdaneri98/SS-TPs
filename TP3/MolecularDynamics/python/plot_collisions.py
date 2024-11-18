import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

SOLUTIONS = ["common_solution", "fixed_solution"]

def group_data_by_interval(df, dt):
    """Groups data into dt intervals"""
    df['time_bin'] = (df['time'] // dt) * dt
    return df.groupby('time_bin').sum().reset_index()

def load_collision_data(count_path, unique_path, dt):
    try:
        if not Path(count_path).exists() or not Path(unique_path).exists():
            return None, None

        df_count = pd.read_csv(count_path)
        df_unique = pd.read_csv(unique_path)

        required_columns = ['time', 'bottom', 'right', 'top', 'left', 'static']
        if not all(col in df_count.columns for col in required_columns):
            return None, None

        if 'static' not in df_unique.columns:
            return None, None

        # Group data by dt intervals
        df_count = group_data_by_interval(df_count, dt)
        df_unique = group_data_by_interval(df_unique, dt)

        # Calculate cumulative sums
        for col in required_columns[1:]:
            df_count[f'{col}_cumsum'] = df_count[col].fillna(0).cumsum()

        df_unique['static_cumsum'] = df_unique['static'].fillna(0).cumsum()

        return df_count, df_unique

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None

def create_collision_plots(df_count, df_unique, output_dir, velocity, solution_type):
    """Creates collision analysis plots"""
    title_prefix = "Solución no estática" if "common" in solution_type else "Solución estática"
    velocity_dir = output_dir / f"v_{velocity:.2f}"
    velocity_dir.mkdir(parents=True, exist_ok=True)

    # Wall collisions plot
    plt.figure(figsize=(10, 6))
    for wall in ['bottom', 'right', 'top', 'left']:
        plt.plot(df_count['time_bin'], df_count[f'{wall}_cumsum'],
                 label=f'Pared {wall}', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Colisiones con Paredes (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(velocity_dir / f"wall_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Static particle total collisions
    plt.figure(figsize=(10, 6))
    plt.plot(df_count['time_bin'], df_count['static_cumsum'], color='blue', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Colisiones Totales con Partícula Estática (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(velocity_dir / f"static_total_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Static particle unique collisions
    plt.figure(figsize=(10, 6))
    plt.plot(df_unique['time_bin'], df_unique['static_cumsum'], color='green', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Únicas Acumuladas')
    plt.title(f'{title_prefix} - Colisiones Únicas con Partícula Estática (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(velocity_dir / f"static_unique_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Combined collisions plot
    plt.figure(figsize=(10, 6))
    walls_total = df_count[['bottom_cumsum', 'right_cumsum', 'top_cumsum', 'left_cumsum']].sum(axis=1)
    plt.plot(df_count['time_bin'], walls_total, label='Total Paredes', linewidth=2)
    plt.plot(df_count['time_bin'], df_count['static_cumsum'], label='Total Partícula Estática', linewidth=2)
    plt.plot(df_unique['time_bin'], df_unique['static_cumsum'], label='Únicas Partícula Estática', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Todas las Colisiones (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(velocity_dir / f"all_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Print statistics
    print(f"\nEstadísticas para v={velocity:.2f} - {title_prefix}")
    print("-" * 50)
    print(f"Tiempo total de simulación: {df_count['time_bin'].iloc[-1]:.2f} s")
    print(f"Colisiones totales con paredes: {walls_total.iloc[-1]:.0f}")
    print(f"Colisiones totales con partícula estática: {df_count['static_cumsum'].iloc[-1]:.0f}")
    print(f"Colisiones únicas con partícula estática: {df_unique['static_cumsum'].iloc[-1]:.0f}")

def plot_collisions(dt=0.1):
    output_dir = Path("outputs/analysis/collisions_plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    for solution_type in SOLUTIONS:
        base_path = Path(f"outputs/{solution_type}")
        if not base_path.exists():
            print(f"No se encuentra el directorio: {base_path}")
            continue

        velocity_dirs = [d for d in base_path.glob("v_*") if d.is_dir()]
        if not velocity_dirs:
            print(f"No se encontraron directorios de velocidad en {base_path}")
            continue

        velocity_dirs.sort(key=lambda x: float(x.name.split("_")[1]))

        for vel_dir in velocity_dirs:
            try:
                velocity = float(vel_dir.name.split("_")[1])
                iter_dir = vel_dir / "0"

                df_count, df_unique = load_collision_data(
                    iter_dir / "count.csv",
                    iter_dir / "unique_counts.csv",
                    dt
                )

                if df_count is not None and df_unique is not None:
                    create_collision_plots(df_count, df_unique, output_dir, velocity, solution_type)

            except Exception as e:
                print(f"Error procesando velocidad {vel_dir.name}: {str(e)}")
                continue

if __name__ == "__main__":
    try:
        plot_collisions()
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        sys.exit(1)