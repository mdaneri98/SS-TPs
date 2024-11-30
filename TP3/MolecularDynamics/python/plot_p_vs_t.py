import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from scipy import stats

def get_average_pressure(velocity_dir, dt=0.05):
    pressure_file = velocity_dir / '0' / 'pressure.csv'
    if not pressure_file.exists():
        return None

    try:
        df = pd.read_csv(pressure_file)
        required_cols = ['time', 'bottom', 'right', 'top', 'left']
        if not all(col in df.columns for col in required_cols):
            print(f"Advertencia: Faltan columnas en {pressure_file}")
            return None

        # Group by time intervals and sum pressures
        df['time_bin'] = (df['time'] // dt) * dt
        steady_state = df.groupby('time_bin').sum().reset_index()

        if steady_state.empty:
            print(f"Advertencia: No hay datos en estado estacionario para {velocity_dir}")
            return None

        # Calculate average wall pressure
        wall_pressure = steady_state[['bottom', 'right', 'top', 'left']].sum(axis=1).mean()
        return wall_pressure

    except Exception as e:
        print(f"Error procesando {pressure_file}: {e}")
        return None

def analyze_pressure_temperature(dt=0.05):
    base_path = Path('outputs/fixed_solution')
    data = []

    for vel_dir in base_path.glob('v_*'):
        try:
            velocity = float(vel_dir.name.split('_')[1])
            avg_pressure = get_average_pressure(vel_dir, dt)

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

    results_df = pd.DataFrame(data)

    if results_df.empty:
        print("No se encontraron datos válidos para analizar")
        return

    results_df.sort_values('velocity', inplace=True)

    if len(results_df) > 1:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            results_df['temperature'],
            results_df['pressure']
        )
        r_squared = r_value ** 2

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=results_df, x='temperature', y='pressure', s=100)

        x_line = np.array([results_df['temperature'].min(), results_df['temperature'].max()])
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, "r--", alpha=0.8,
                 label=f'Ajuste lineal:\nP = {slope:.2f}T + {intercept:.2f}\nR² = {r_squared:.4f}')

        plt.xlabel('Temperatura', fontsize=12)
        plt.ylabel('Presión promedio en paredes (N/m)', fontsize=12)
        #plt.title('Relación entre Presión y Temperatura', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        output_dir = Path('outputs/analysis/p_vs_t')
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / 'pressure_vs_temperature.png',
                    dpi=300, bbox_inches='tight')
        plt.close()

        results_df.to_csv(output_dir / 'pressure_temperature_data.csv',
                          index=False)

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