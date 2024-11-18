import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

SOLUTIONS = ["common_solution", "fixed_solution"]

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

        # Calculate cumulative sums
        for col in required_columns[1:]:
            df_count[f'{col}_cumsum'] = df_count[col].fillna(0).cumsum()

        df_unique['static_cumsum'] = df_unique['static'].fillna(0).cumsum()

        return df_count, df_unique

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None

def create_collision_plots(velocity_data, output_dir, solution_type):
    title_prefix = "Solución no estática" if "common" in solution_type else "Solución estática"
    colors = plt.cm.viridis(np.linspace(0, 1, len(velocity_data)))

    # Wall collisions - cada pared en un gráfico separado
    for wall in ['bottom', 'right', 'top', 'left']:
        plt.figure(figsize=(15, 10), dpi=300)
        for vel_idx, (velocity, (df_count, _)) in enumerate(velocity_data.items()):
            plt.plot(df_count['time_bin'], df_count[f'{wall}_cumsum'],
                     label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
        plt.xlabel('Tiempo (s)', fontsize=14)
        plt.ylabel('Colisiones Acumuladas', fontsize=14)
        plt.title(f'{title_prefix} - Colisiones con Pared {wall}', fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.savefig(output_dir / f"wall_collisions_{wall}_{solution_type}.png", dpi=300, bbox_inches='tight')
        plt.close()

    # Total static particle collisions
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (df_count, _)) in enumerate(velocity_data.items()):
        plt.plot(df_count['time_bin'], df_count['static_cumsum'],
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Colisiones Totales', fontsize=14)
    plt.title(f'{title_prefix} - Colisiones Totales con Partícula Estática', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"static_total_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Unique static particle collisions
    plt.figure(figsize=(15, 10), dpi=300)
    for vel_idx, (velocity, (_, df_unique)) in enumerate(velocity_data.items()):
        plt.plot(df_unique['time_bin'], df_unique['static_cumsum'],
                 label=f'v={velocity:.2f}', color=colors[vel_idx], linewidth=2)
    plt.xlabel('Tiempo (s)', fontsize=14)
    plt.ylabel('Colisiones Únicas', fontsize=14)
    plt.title(f'{title_prefix} - Colisiones Únicas con Partícula Estática', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / f"static_unique_collisions_{solution_type}.png", dpi=300, bbox_inches='tight')
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
                    df_count = df_count.iloc[:-2]  # Remove last two intervals
                    df_unique = df_unique.iloc[:-2]  # Remove last two intervals
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