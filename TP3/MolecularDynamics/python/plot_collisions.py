import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

SOLUTIONS = ["fixed_solution"]

def group_data_by_interval(df, dt):
    """Groups data into dt intervals"""
    df['time_bin'] = (df['time'] // dt) * dt
    grouped = df.groupby('time_bin').sum().reset_index()
    return grouped.iloc[:-2]  # Remove last 2 rows

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

        return df_count, df_unique

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None

def create_collision_plots(velocity_data, output_dir, solution_type):
    title_prefix = "Solución no estática" if "common" in solution_type else "Solución estática"
    colors = plt.cm.viridis(np.linspace(0, 1, len(velocity_data)))

    # 1. Total collisions from count.csv
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (df_count, _)) in enumerate(velocity_data.items()):
        total_collisions = df_count[['bottom', 'right', 'top', 'left', 'static']].sum(axis=1).cumsum()
        plt.plot(df_count['time_bin'], total_collisions,
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Cantidad Total de Choques', fontsize=14)
    plt.title(f'{title_prefix} - Choques Totales (count.csv)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"total_collisions_count_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Total collisions from unique_count.csv
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (_, df_unique)) in enumerate(velocity_data.items()):
        plt.plot(df_unique['time_bin'], df_unique['static'].cumsum(),
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Cantidad Total de Choques Únicos', fontsize=14)
    plt.title(f'{title_prefix} - Choques Únicos (unique_count.csv)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"total_collisions_unique_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Average collisions from count.csv
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (df_count, _)) in enumerate(velocity_data.items()):
        all_collisions = df_count[['bottom', 'right', 'top', 'left', 'static']]
        avg_collisions = all_collisions.mean(axis=1).cumsum()
        plt.plot(df_count['time_bin'], avg_collisions,
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Promedio de Choques', fontsize=14)
    plt.title(f'{title_prefix} - Promedio de Choques (count.csv)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"average_collisions_count_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Average collisions rate from count.csv
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (df_count, _)) in enumerate(velocity_data.items()):
        all_collisions = df_count[['bottom', 'right', 'top', 'left', 'static']]
        collision_rates = all_collisions.mean(axis=1)  # No cumsum for rate
        plt.plot(df_count['time_bin'], collision_rates,
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Tasa Promedio de Choques', fontsize=14)
    plt.title(f'{title_prefix} - Tasa Promedio de Choques (count.csv)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"average_collision_rate_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 5. NEW: Time to maximum unique collisions vs Temperature
    temperatures = [v**2 for v in velocity_data.keys()]
    max_collision_times = []

    for velocity, (_, df_unique) in velocity_data.items():
        cumsum_collisions = df_unique['static'].cumsum()
        max_collision_time = df_unique['time_bin'][cumsum_collisions.idxmax()]
        max_collision_times.append(max_collision_time)

    plt.figure(figsize=(15, 10), dpi=300)
    plt.scatter(temperatures, max_collision_times, color='blue', s=100)
    plt.plot(temperatures, max_collision_times, color='red', linestyle='--', alpha=0.7)

    plt.xlabel('Temperatura (v²)', fontsize=14)
    plt.ylabel('Tiempo de Máximas Colisiones Únicas (s)', fontsize=14)
    plt.title(f'{title_prefix} - Tiempo de Máximas Colisiones vs Temperatura', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_dir / f"max_collisions_time_vs_temperature_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_collisions(dt=0.1):
    output_dir = Path("outputs/analysis/collisions_plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    for solution_type in SOLUTIONS:
        base_path = Path(f"outputs/{solution_type}")
        if not base_path.exists() or not any(base_path.glob("v_*")):
            continue

        velocity_data = {}
        velocity_dirs = sorted(base_path.glob("v_*"),
                               key=lambda x: float(x.name.split("_")[1]))

        for vel_dir in velocity_dirs:
            try:
                velocity = float(vel_dir.name.split("_")[1])
                df_count, df_unique = load_collision_data(
                    vel_dir / "0" / "count.csv",
                    vel_dir / "0" / "unique_counts.csv",
                    dt
                )
                if df_count is not None and df_unique is not None:
                    velocity_data[velocity] = (df_count, df_unique)

            except Exception as e:
                print(f"Error procesando velocidad {vel_dir.name}: {str(e)}")
                continue

        if velocity_data:
            create_collision_plots(velocity_data, output_dir, solution_type)

if __name__ == "__main__":
    try:
        plot_collisions()
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        sys.exit(1)