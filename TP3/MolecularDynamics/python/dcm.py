import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path
import pandas as pd

# Tiempos fijos para el análisis
INITIAL_TIMES = np.arange(0, 0.3 + 0.05, 0.05)
FIXED_TIMES = np.arange(1, 5 + 0.05, 0.5)

def load_and_process_data(solution_type, velocity, iteration):
    """
    Carga y procesa los datos de una iteración específica
    """
    base_path = Path(f"outputs/{solution_type}/v_{velocity:.2f}/{iteration}")
    particles_file = base_path / "particles.csv"

    df = pd.read_csv(particles_file)
    static_df = df[df['id'] == 0].copy()
    particles_df = df[df['id'] != 0].copy()

    return particles_df, static_df

def calculate_dcm_values(times, solution_type, velocity):
    """
    Calcula los valores DCM para los tiempos dados
    """
    all_dcm = []
    valid_iterations = 0

    for iteration in range(10):  # Asumimos 10 iteraciones
        try:
            particles_df, static_df = load_and_process_data(solution_type, velocity, iteration)

            # Calcular DCM para esta iteración
            iteration_dcm = []
            for t in times:
                # Encontrar el tiempo más cercano en los datos
                closest_time = particles_df['time'].values[
                    np.abs(particles_df['time'].values - t).argmin()
                ]

                # Filtrar datos para el tiempo más cercano
                current_particles = particles_df[particles_df['time'] == closest_time]
                current_static = static_df[static_df['time'] == closest_time]

                # Calcular desplazamiento cuadrático medio
                dx = current_particles['x'].values - current_static['x'].values[0]
                dy = current_particles['y'].values - current_static['y'].values[0]
                z2 = dx**2 + dy**2
                dcm = np.mean(z2)

                iteration_dcm.append(dcm)

            all_dcm.append(iteration_dcm)
            valid_iterations += 1

        except Exception as e:
            print(f"Error en iteración {iteration}: {str(e)}")
            continue

    if valid_iterations < 1:
        raise ValueError("No se encontraron iteraciones válidas")

    all_dcm = np.array(all_dcm)
    mean_dcm = np.mean(all_dcm, axis=0)
    std_dcm = np.std(all_dcm, axis=0) / np.sqrt(valid_iterations)

    return mean_dcm, std_dcm

def analyze_initial_times(solution_type, velocity):
    """
    Realiza el análisis con INITIAL_TIMES
    """
    dcm_values, dcm_errors = calculate_dcm_values(INITIAL_TIMES, solution_type, velocity)

    # Ajuste lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(INITIAL_TIMES, dcm_values)
    D = slope / 2

    plt.figure(figsize=(10, 8))

    plt.errorbar(INITIAL_TIMES, dcm_values, yerr=dcm_errors, fmt='o-',
                 label=f'DCM (v={velocity:.2f})', color='#1f77b4', capsize=5,
                 markersize=6, linewidth=2)

    x_line = np.linspace(0, max(INITIAL_TIMES), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, '--', color='red',
             label=f'Ajuste lineal (D={D:.3e})', linewidth=2)

    plt.xlabel('Tiempo (s)', fontsize=12)
    plt.ylabel('DCM (m²)', fontsize=12)
    plt.title(f'DCM vs Tiempo (Initial Times) - {solution_type.replace("_", " ").title()}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    output_dir = Path("outputs/analysis/dcm_plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f"dcm_initial_{solution_type}_v{velocity:.2f}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    return D, r_value**2

def analyze_fixed_times(solution_type, velocity):
    """
    Realiza el análisis con FIXED_TIMES
    """
    dcm_values, dcm_errors = calculate_dcm_values(FIXED_TIMES, solution_type, velocity)

    plt.figure(figsize=(10, 8))

    plt.errorbar(FIXED_TIMES, dcm_values, yerr=dcm_errors, fmt='o-',
                 label=f'DCM (v={velocity:.2f})', color='#1f77b4', capsize=5,
                 markersize=6, linewidth=2)

    plt.xlabel('Tiempo (s)', fontsize=12)
    plt.ylabel('DCM (m²)', fontsize=12)
    plt.title(f'DCM vs Tiempo (Fixed Times) - {solution_type.replace("_", " ").title()}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    output_dir = Path("outputs/analysis/dcm_plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f"dcm_fixed_{solution_type}_v{velocity:.2f}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    return dcm_values, dcm_errors

def find_optimal_coefficient(times, dcm_values, velocity, solution_type):
    """
    Encuentra el coeficiente óptimo que minimiza el error E(c)
    según la teoría de regresión lineal
    """
    c_values = np.linspace(0.001, 0.01, 200)
    errors = []

    # E(c) = Σ[yi - f(xi,c)]²
    for c in c_values:
        model_predictions = c * times  # f(xi,c) = c*xi para modelo lineal
        squared_errors = (dcm_values - model_predictions)**2
        total_error = np.sum(squared_errors)
        errors.append(total_error)

    min_error_idx = np.argmin(errors)
    c_optimal = c_values[min_error_idx]

    plt.figure(figsize=(10, 8))

    # Graficar error vs coeficiente (curva parabólica como en teoría)
    plt.plot(c_values, errors, 'r-', linewidth=2)
    plt.plot(c_optimal, errors[min_error_idx], 'bo',
             label=f'Mínimo en c* = {c_optimal:.6f}')

    plt.axvline(x=c_optimal, color='black', linestyle='--', alpha=0.5)
    plt.axhline(y=errors[min_error_idx], color='black', linestyle='--', alpha=0.5)

    plt.xlabel('Coeficiente c', fontsize=12)
    plt.ylabel('Error E(c)', fontsize=12)
    plt.title('Función de Error del Modelo Lineal')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)

    output_dir = Path("outputs/analysis/dcm_plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f"error_minimization_{solution_type}_v{velocity:.2f}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

    return c_optimal

def main():
    solution_type = "common_solution"
    velocity = 1.0  # Ejemplo de velocidad

    try:
        # Análisis con INITIAL_TIMES
        D, r_squared = analyze_initial_times(solution_type, velocity)
        print(f"\nAnálisis con INITIAL_TIMES:")
        print(f"Coeficiente de difusión (D): {D:.3e}")
        print(f"R²: {r_squared:.3f}")

        # Análisis con FIXED_TIMES
        dcm_values, dcm_errors = analyze_fixed_times(solution_type, velocity)

        # Encontrar coeficiente óptimo
        c_optimal = find_optimal_coefficient(FIXED_TIMES, dcm_values, velocity, solution_type)
        print(f"\nAnálisis de minimización de error:")
        print(f"Coeficiente óptimo: {c_optimal:.6f}")

    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    main()