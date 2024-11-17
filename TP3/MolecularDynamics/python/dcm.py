import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pathlib import Path

# Tiempos fijos para el análisis
FIXED_TIMES = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                        1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])

def calculate_dcm_for_iteration(df, static_df):
    """
    Calcula el DCM para una iteración en los tiempos fijos especificados
    """
    df_merged = pd.merge(df, static_df[['time', 'x', 'y']],
                         on='time',
                         suffixes=('', '_static'))

    # Calcular desplazamiento respecto al centro (partícula estática)
    df_merged['dx'] = df_merged['x'] - df_merged['x_static']
    df_merged['dy'] = df_merged['y'] - df_merged['y_static']
    df_merged['z2'] = df_merged['dx']**2 + df_merged['dy']**2

    # Calcular DCM solo para los tiempos fijos
    dcm_values = []
    for t in FIXED_TIMES:
        z2_mean = df_merged[df_merged['time'] == t]['z2'].mean()
        dcm_values.append(z2_mean)

    return np.array(dcm_values)

def calculate_dcm_with_iterations(solution_type, velocity):
    """
    Calcula el DCM promediando todas las iteraciones
    """
    base_path = Path(f"outputs/{solution_type}")
    velocity_path = base_path / f"v_{velocity:.2f}"

    if not velocity_path.exists():
        raise ValueError(f"No se encontró el directorio para velocidad {velocity}")

    iteration_dirs = [d for d in velocity_path.iterdir() if d.is_dir()]
    iteration_dirs.sort(key=lambda x: int(x.name))

    if len(iteration_dirs) < 10:
        raise ValueError(f"Se necesitan al menos 10 iteraciones, se encontraron {len(iteration_dirs)}")

    print(f"Procesando {len(iteration_dirs)} iteraciones para v = {velocity}")
    print(f"Calculando DCM para {len(FIXED_TIMES)} puntos de tiempo")

    all_dcm = []
    valid_iterations = 0

    for iter_dir in iteration_dirs:
        particles_file = iter_dir / "particles.csv"
        if not particles_file.exists():
            continue

        try:
            df = pd.read_csv(particles_file)
            static_df = df[df['id'] == 0].copy()
            particles_df = df[df['id'] != 0].copy()

            dcm = calculate_dcm_for_iteration(particles_df, static_df)
            all_dcm.append(dcm)
            valid_iterations += 1
        except Exception as e:
            print(f"Error procesando iteración {iter_dir}: {str(e)}")
            continue

    print(f"Procesadas {valid_iterations} iteraciones válidas")

    if valid_iterations < 10:
        raise ValueError("Se necesitan al menos 10 iteraciones válidas")

    all_dcm = np.array(all_dcm)
    mean_dcm = np.mean(all_dcm, axis=0)
    std_dcm = np.std(all_dcm, axis=0) / np.sqrt(valid_iterations)

    return FIXED_TIMES, mean_dcm, std_dcm

def plot_dcm(times, dcm_values, dcm_errors, velocity, solution_type):
    """
    Genera el gráfico de DCM vs tiempo con ajuste lineal
    """
    # Realizar ajuste lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(times, dcm_values)
    D = slope / 2  # Coeficiente de difusión según la ecuación <z²> = 2Dt

    plt.figure(figsize=(10, 8))

    # Graficar cada iteración
    plt.errorbar(times, dcm_values, yerr=dcm_errors, fmt='o-',
                 label=f'DCM (v={velocity:.2f})', color='#1f77b4', capsize=5,
                 markersize=6, linewidth=2)

    # Plotear ajuste lineal
    x_line = np.linspace(0, max(times), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, '--', color='red',
             label=f'Ajuste lineal (D={D:.3e})', linewidth=2)

    plt.xlabel('Tiempo (s)', fontsize=12)
    plt.ylabel('DCM (m²)', fontsize=12)
    plt.title(f'DCM vs Tiempo - {solution_type.replace("_", " ").title()}', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.tight_layout()

    output_dir = Path("outputs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f"dcm_{solution_type}_v{velocity:.2f}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\nAnálisis de DCM para {solution_type}, v = {velocity:.2f}:")
    print("-" * 40)
    print(f"Puntos analizados: {len(times)}")
    print(f"Tiempo máximo: {max(times):.3f} s")
    print(f"Coeficiente de difusión (D): {D:.3e} m²/s")
    print(f"R²: {r_value**2:.3f}")
    print(f"Error estándar de la pendiente: {std_err:.3e}")

    return D, r_value**2, std_err

def get_velocities(solution_type):
    """
    Obtiene todas las velocidades disponibles para un tipo de solución
    """
    base_path = Path(f"outputs/{solution_type}")
    if not base_path.exists():
        return []

    velocities = []
    for dir_path in base_path.iterdir():
        if dir_path.is_dir() and dir_path.name.startswith("v_"):
            try:
                velocity = float(dir_path.name.split('_')[1])
                velocities.append(velocity)
            except:
                continue

    return sorted(velocities)

def main():
    try:
        solution_types = ["common_solution", "fixed_solution"]

        for solution_type in solution_types:
            print(f"\nProcesando {solution_type}...")
            velocities = get_velocities(solution_type)

            if not velocities:
                print(f"No se encontraron velocidades para {solution_type}")
                continue

            results = []
            for velocity in velocities:
                try:
                    print(f"\nProcesando velocidad {velocity}...")
                    times, mean_dcm, std_dcm = calculate_dcm_with_iterations(solution_type, velocity)
                    D, R2, std_err = plot_dcm(times, mean_dcm, std_dcm, velocity, solution_type)

                    results.append({
                        'velocity': velocity,
                        'D': D,
                        'R2': R2,
                        'std_err': std_err
                    })

                except Exception as e:
                    print(f"Error procesando velocidad {velocity}: {str(e)}")
                    continue

            if results:
                print(f"\nResumen de resultados para {solution_type}:")
                print("-" * 60)
                df_results = pd.DataFrame(results)
                print(df_results.sort_values('velocity').to_string(index=False))

                output_dir = Path("outputs/analysis")
                df_results.to_csv(output_dir / f"dcm_results_{solution_type}.csv", index=False)

    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        print("\nDetalles del error:")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())