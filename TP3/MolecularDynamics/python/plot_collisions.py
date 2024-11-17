import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import sys
from pathlib import Path

SOLUTIONS = ["common_solution", "fixed_solution"]

def load_collision_data(count_path, unique_path):
    """
    Carga y valida los datos de colisiones con manejo de errores mejorado
    """
    try:
        if not os.path.exists(count_path) or not os.path.exists(unique_path):
            return None, None

        # Cargar datos de colisiones totales
        df_count = pd.read_csv(count_path)
        df_unique = pd.read_csv(unique_path)

        required_columns = ['time', 'bottom', 'right', 'top', 'left', 'static']
        if not all(col in df_count.columns for col in required_columns):
            return None, None

        if 'static' not in df_unique.columns:
            return None, None

        # Calcular valores acumulados
        for col in required_columns[1:]:
            df_count[f'{col}_cumsum'] = df_count[col].fillna(0).cumsum()

        df_unique['static_cumsum'] = df_unique['static'].fillna(0).cumsum()

        return df_count, df_unique

    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        return None, None

def create_collision_plots(df_count, df_unique, output_dir, velocity, solution_type):
    """
    Crea los cuatro gráficos para una velocidad específica
    """
    title_prefix = "Solución Común" if "common" in solution_type else "Solución Fija"

    # Crear subcarpeta para la velocidad
    velocity_dir = output_dir / f"v_{velocity:.2f}"
    velocity_dir.mkdir(parents=True, exist_ok=True)

    # 1. Colisiones totales con las paredes
    plt.figure(figsize=(10, 6))
    for wall in ['bottom', 'right', 'top', 'left']:
        plt.plot(df_count['time'], df_count[f'{wall}_cumsum'],
                 label=f'Pared {wall}',
                 linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Colisiones con Paredes (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(velocity_dir / f"wall_collisions_{solution_type}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Colisiones totales con la partícula estática
    plt.figure(figsize=(10, 6))
    plt.plot(df_count['time'], df_count['static_cumsum'],
             color='blue', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Colisiones Totales con Partícula Estática (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(velocity_dir / f"static_total_collisions_{solution_type}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Colisiones únicas con la partícula estática
    plt.figure(figsize=(10, 6))
    plt.plot(df_unique['time'], df_unique['static_cumsum'],
             color='green', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Únicas Acumuladas')
    plt.title(f'{title_prefix} - Colisiones Únicas con Partícula Estática (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(velocity_dir / f"static_unique_collisions_{solution_type}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Todas las colisiones en un solo gráfico
    plt.figure(figsize=(10, 6))
    walls_total = df_count[['bottom_cumsum', 'right_cumsum',
                            'top_cumsum', 'left_cumsum']].sum(axis=1)
    plt.plot(df_count['time'], walls_total,
             label='Total Paredes', linewidth=2)
    plt.plot(df_count['time'], df_count['static_cumsum'],
             label='Total Partícula Estática', linewidth=2)
    plt.plot(df_unique['time'], df_unique['static_cumsum'],
             label='Únicas Partícula Estática', linewidth=2)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Colisiones Acumuladas')
    plt.title(f'{title_prefix} - Todas las Colisiones (v={velocity:.2f})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(velocity_dir / f"all_collisions_{solution_type}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    # Imprimir estadísticas
    print(f"\nEstadísticas para v={velocity:.2f} - {title_prefix}")
    print("-" * 50)
    final_time = df_count['time'].iloc[-1]
    print(f"Tiempo total de simulación: {final_time:.2f} s")
    print(f"Colisiones totales con paredes: {walls_total.iloc[-1]:.0f}")
    print(f"Colisiones totales con partícula estática: {df_count['static_cumsum'].iloc[-1]:.0f}")
    print(f"Colisiones únicas con partícula estática: {df_unique['static_cumsum'].iloc[-1]:.0f}")

def plot_collisions():
    output_dir = Path("outputs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    for solution_type in SOLUTIONS:
        base_path = Path(f"outputs/{solution_type}")
        if not base_path.exists():
            print(f"No se encuentra el directorio: {base_path}")
            continue

        # Encontrar todos los directorios de velocidad
        velocity_dirs = [d for d in base_path.glob("v_*") if d.is_dir()]
        if not velocity_dirs:
            print(f"No se encontraron directorios de velocidad en {base_path}")
            continue

        velocity_dirs.sort(key=lambda x: float(x.name.split("_")[1]))

        for vel_dir in velocity_dirs:
            try:
                velocity = float(vel_dir.name.split("_")[1])
                iter_dir = vel_dir / "0"  # Primera iteración

                count_file = iter_dir / "count.csv"
                unique_file = iter_dir / "unique_counts.csv"

                df_count, df_unique = load_collision_data(count_file, unique_file)
                if df_count is None or df_unique is None:
                    continue

                # Crear los cuatro gráficos para esta velocidad
                create_collision_plots(df_count, df_unique, output_dir,
                                       velocity, solution_type)

            except Exception as e:
                print(f"Error procesando velocidad {vel_dir.name}: {str(e)}")
                continue

if __name__ == "__main__":
    try:
        plot_collisions()
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)