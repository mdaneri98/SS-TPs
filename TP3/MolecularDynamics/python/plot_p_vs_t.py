import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from scipy import stats

def get_average_pressure(velocity_dir):
    """
    Calcula la presión promedio para una velocidad dada usando solo la iteración 0
    """
    pressure_file = velocity_dir / '0' / 'pressure.csv'
    if not pressure_file.exists():
        return None

    try:
        # Leer el archivo de presión
        df = pd.read_csv(pressure_file)

        # Verificar que tenemos las columnas necesarias
        required_cols = ['time', 'bottom', 'right', 'top', 'left']
        if not all(col in df.columns for col in required_cols):
            print(f"Advertencia: Faltan columnas en {pressure_file}")
            return None

        # Calcular la presión en estado estacionario
        start_time = 0  # Empezamos desde t=2s para evitar el transitorio
        steady_state = df[df['time'] > start_time]

        if steady_state.empty:
            print(f"Advertencia: No hay datos en estado estacionario para {velocity_dir}")
            return None

        # Sumamos las presiones de todas las paredes
        wall_pressure = steady_state[['bottom', 'right', 'top', 'left']].sum(axis=1).mean()
        return wall_pressure

    except Exception as e:
        print(f"Error procesando {pressure_file}: {e}")
        return None

def analyze_pressure_temperature():
    base_path = Path('outputs/fixed_solution')

    # Almacenar resultados
    data = []

    # Procesar cada directorio de velocidad
    for vel_dir in base_path.glob('v_*'):
        try:
            velocity = float(vel_dir.name.split('_')[1])
            avg_pressure = get_average_pressure(vel_dir)

            if avg_pressure is not None:
                data.append({
                    'velocity': velocity,
                    'temperature': velocity ** 2,
                    'pressure': avg_pressure
                })
                print(f"Velocidad: {velocity}, Presión promedio: {avg_pressure:.2f}")

        except ValueError as e:
            print(f"Error en el nombre del directorio {vel_dir}: {e}")
        except Exception as e:
            print(f"Error procesando {vel_dir}: {e}")

    # Crear DataFrame
    results_df = pd.DataFrame(data)

    if results_df.empty:
        print("No se encontraron datos válidos para analizar")
        return

    # Ordenar por velocidad
    results_df.sort_values('velocity', inplace=True)

    # Realizar ajuste lineal solo si tenemos suficientes puntos
    if len(results_df) > 1:
        # Usar scipy.stats para el ajuste lineal (más robusto que np.polyfit)
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            results_df['temperature'],
            results_df['pressure']
        )
        r_squared = r_value ** 2

        # Crear el gráfico
        plt.figure(figsize=(10, 6))

        # Scatter plot
        sns.scatterplot(data=results_df, x='temperature', y='pressure', s=100)

        # Línea de ajuste
        x_line = np.array([results_df['temperature'].min(), results_df['temperature'].max()])
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, "r--", alpha=0.8,
                 label=f'Ajuste lineal:\nP = {slope:.2f}T + {intercept:.2f}\nR² = {r_squared:.4f}')

        plt.xlabel('Temperatura (v²)', fontsize=12)
        plt.ylabel('Presión promedio en paredes', fontsize=12)
        plt.title('Relación entre Presión y Temperatura\n(Usando iteración 0)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # Guardar el gráfico
        output_dir = Path('outputs/analysis/p_vs_t')
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / 'pressure_vs_temperature_iter0.png',
                    dpi=300, bbox_inches='tight')
        plt.close()

        # Guardar los datos procesados
        results_df.to_csv(output_dir / 'pressure_temperature_data_iter0.csv',
                          index=False)

        # Imprimir resultados
        print("\nResultados ordenados por velocidad:")
        print(results_df)
        print(f"\nAjuste lineal: P = {slope:.4f}T + {intercept:.4f}")
        print(f"R² = {r_squared:.4f}")

    else:
        print("\nInsuficientes puntos para realizar el ajuste lineal")
        print("\nResultados ordenados por velocidad:")
        print(results_df)

if __name__ == "__main__":
    analyze_pressure_temperature()