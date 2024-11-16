import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import glob

def analyze_pressure_temperature(steady_state_time):
    base_dir = "outputs/fixed_solution"
    velocities = [1, 3.6, 10.0]  # m/s

    # Almacenar resultados
    results = {
        'velocity': [],
        'temperature': [],  # proporcional a v²
        'avg_pressure': [],
        'std_pressure': []  # para barras de error
    }

    # Procesar cada velocidad
    for v0 in velocities:
        pressure_path = os.path.join(base_dir, f"v_{v0:.2f}", "pressure.csv")

        if not os.path.exists(pressure_path):
            print(f"Error: Archivo no encontrado en {pressure_path}")
            continue

        # Leer datos
        pressure_df = pd.read_csv(pressure_path)

        # Filtrar datos desde el tiempo de estado estacionario
        steady_state_data = pressure_df[pressure_df['time'] >= steady_state_time]

        if steady_state_data.empty:
            print(f"Error: No hay datos después de t = {steady_state_time} para v = {v0}")
            continue

        # Calcular promedio de todas las paredes (excepto static)
        wall_pressures = ['bottom', 'right', 'top', 'left']
        avg_pressure = steady_state_data[wall_pressures].mean().mean()
        std_pressure = steady_state_data[wall_pressures].mean().std()

        # Temperatura proporcional a v²
        temperature = v0 * v0

        # Guardar resultados
        results['velocity'].append(v0)
        results['temperature'].append(temperature)
        results['avg_pressure'].append(avg_pressure)
        results['std_pressure'].append(std_pressure)

    # Convertir a DataFrame
    results_df = pd.DataFrame(results)

    # Graficar P vs T
    plt.figure(figsize=(10, 6))

    # Graficar puntos con barras de error
    plt.errorbar(results_df['temperature'], results_df['avg_pressure'],
                 yerr=results_df['std_pressure'],
                 fmt='o', capsize=5, label='Datos simulados')

    # Ajuste lineal manual
    p = np.polyfit(results_df['temperature'], results_df['avg_pressure'], 1)
    T = np.array(results_df['temperature'])
    P_fit = p[0] * T + p[1]

    # Calcular R² manualmente
    residuals = results_df['avg_pressure'] - P_fit
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((results_df['avg_pressure'] - np.mean(results_df['avg_pressure'])) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    plt.plot(T, P_fit, '--r',
             label=f'Ajuste lineal (R² = {r_squared:.3f})')

    plt.xlabel('Temperatura (∝ v²)')
    plt.ylabel('Presión promedio')
    plt.title(f'Relación entre Presión y Temperatura\n(Estado estacionario desde t = {steady_state_time})')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Guardar resultados
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Guardar gráfica
    plt.savefig(os.path.join(output_dir, "pressure_vs_temperature.png"), dpi=300, bbox_inches='tight')
    plt.show()

    # Guardar datos numéricos
    results_df.to_csv(os.path.join(output_dir, "pressure_temperature_data.csv"), index=False)

    # Imprimir resultados
    print("\nResultados del análisis:")
    print(results_df)
    print("\nCoeficientes del ajuste lineal:")
    print(f"Pendiente: {p[0]:.4f}")
    print(f"Ordenada al origen: {p[1]:.4f}")

if __name__ == "__main__":
    # Especifica aquí el tiempo a partir del cual consideras estado estacionario
    steady_state_time = 0  # segundos
    analyze_pressure_temperature(steady_state_time)