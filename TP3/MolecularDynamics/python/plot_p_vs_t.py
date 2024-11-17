import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def get_average_pressure(velocity_dir):
    """
    Calcula la presión promedio para una velocidad dada usando solo la iteración 0
    """
    # Leer específicamente de la iteración 0
    pressure_file = velocity_dir / '0' / 'pressure.csv'
    if pressure_file.exists():
        # Leer el archivo de presión
        df = pd.read_csv(pressure_file)

        # Calcular la presión total como la suma de todas las componentes
        # Excluimos los primeros segundos para evitar el transitorio
        start_time = 2  # Empezamos desde t=2s para evitar el transitorio
        steady_state = df[df['time'] > start_time]

        if not steady_state.empty:
            # Sumamos las presiones de todas las paredes (ignoramos static)
            wall_pressure = steady_state[['bottom', 'right', 'top', 'left']].sum(axis=1).mean()
            return wall_pressure

    return None

def analyze_pressure_temperature():
    base_path = Path('outputs/fixed_solution')

    # Almacenar resultados
    velocities = []
    pressures = []

    # Procesar cada directorio de velocidad
    for vel_dir in base_path.glob('v_*'):
        try:
            # Extraer velocidad del nombre del directorio
            velocity = float(vel_dir.name.split('_')[1])

            # Calcular presión promedio
            avg_pressure = get_average_pressure(vel_dir)

            if avg_pressure is not None:
                velocities.append(velocity)
                pressures.append(avg_pressure)
                print(f"Velocidad: {velocity}, Presión promedio: {avg_pressure:.2f}")
        except Exception as e:
            print(f"Error procesando {vel_dir}: {e}")

    # Convertir a numpy arrays
    velocities = np.array(velocities)
    temperatures = velocities ** 2  # T ∝ v²
    pressures = np.array(pressures)

    # Crear el gráfico
    plt.figure(figsize=(10, 6))

    # Scatter plot
    sns.scatterplot(x=temperatures, y=pressures, s=100)

    # Ajuste lineal
    z = np.polyfit(temperatures, pressures, 1)
    p = np.poly1d(z)
    r2 = np.corrcoef(temperatures, pressures)[0,1]**2  # Calcular R²

    plt.plot(temperatures, p(temperatures), "r--", alpha=0.8,
             label=f'Ajuste lineal:\nP = {z[0]:.2f}T + {z[1]:.2f}\nR² = {r2:.4f}')

    plt.xlabel('Temperatura (v²)', fontsize=12)
    plt.ylabel('Presión promedio en paredes', fontsize=12)
    plt.title('Relación entre Presión y Temperatura\n(Usando iteración 0)', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Guardar el gráfico
    output_dir = Path('outputs/analysis/p_vs_t')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'pressure_vs_temperature_iter0.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Guardar los datos procesados
    results_df = pd.DataFrame({
        'velocity': velocities,
        'temperature': temperatures,
        'pressure': pressures
    })
    results_df.sort_values('velocity', inplace=True)
    results_df.to_csv(output_dir / 'pressure_temperature_data_iter0.csv', index=False)

    # Imprimir resultados
    print("\nResultados ordenados por velocidad:")
    print(results_df)
    print(f"\nAjuste lineal: P = {z[0]:.4f}T + {z[1]:.4f}")
    print(f"R² = {r2:.4f}")

if __name__ == "__main__":
    analyze_pressure_temperature()