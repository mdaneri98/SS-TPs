import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class FlowRateAnalyzer:
    def __init__(self, base_path="outputs/probabilistic_analysis"):
        self.base_path = Path(base_path)

    def read_particles_file(self, sim_path):
        """Lee el archivo dynamic.txt con la información de las partículas"""
        particles_path = sim_path / "dynamic.txt"
        particles_data = []
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        current_time = float(line)
                        continue
                    except ValueError:
                        if current_time is not None:
                            values = line.split(',')
                            if len(values) == 7:
                                particles_data.append({
                                    'time': current_time,
                                    'id': int(float(values[0])),
                                    'x': float(values[1]),
                                    'y': float(values[2]),
                                    'vel_x': float(values[3]),
                                    'vel_y': float(values[4]),
                                    'radius': float(values[5]),
                                    'exit_door': int(float(values[6]))
                                })

            df = pd.DataFrame(particles_data)
            # Ordenar por tiempo para asegurar el cálculo correcto
            return df.sort_values('time')

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def calculate_flow_rate(self, particles_data, dt=1.0):
        """Calcula el caudal instantáneo como la cantidad de partículas que salen en cada intervalo dt"""
        if len(particles_data) == 0:
            return None

        # Identificar cuándo cada partícula sale del sistema
        # Una partícula sale cuando aparece por última vez en los datos
        last_appearances = particles_data.groupby('id')['time'].max()

        # Crear bins de tiempo para contar partículas
        max_time = particles_data['time'].max()
        time_bins = np.arange(0, max_time + dt, dt)

        # Contar cuántas partículas salen en cada intervalo
        particle_exits = pd.cut(last_appearances, bins=time_bins).value_counts().sort_index()

        # Convertir conteos a caudal (partículas por segundo)
        flow_rates = particle_exits.values / dt

        # Los tiempos corresponden al inicio de cada intervalo
        times = time_bins[:-1]

        return {
            'times': times,
            'flow_rates': flow_rates
        }

    def analyze_flow_rates(self, t_value, p_values):
        """Analiza el caudal para un valor de t y varios valores de p"""
        results = {}

        for p_value in p_values:
            path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}" / "sim_000"

            # Usar solo la simulación 000
            particles_data = self.read_particles_file(path)
            if len(particles_data) > 0:
                flow_rate = self.calculate_flow_rate(particles_data)
                if flow_rate:
                    results[p_value] = {
                        'times': flow_rate['times'],
                        'flow_rates': flow_rate['flow_rates'],
                    }

        return results

    def plot_flow_rates(self, results, t_value, output_dir="plots"):
        """Genera gráfico de caudal vs tiempo para diferentes valores de p"""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 8))

        # Color map para diferentes valores de p
        colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

        for (p_value, data), color in zip(results.items(), colors):
            plt.plot(data['times'], data['flow_rates'],
                     label=f'p = {p_value:.2f}',
                     color=color)

        plt.title(f'Caudal vs Tiempo (t = {t_value})')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Caudal (partículas/s)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/flow_rates_t{t_value}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    # Crear el analizador
    analyzer = FlowRateAnalyzer()

    # Definir parámetros
    t_value = 20  # Tiempo de redecisión fijo
    p_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # Valores de probabilidad a analizar

    # Analizar caudales
    print("Analizando caudales...")
    results = analyzer.analyze_flow_rates(t_value, p_values)

    # Generar gráfico
    print("Generando gráfico...")
    analyzer.plot_flow_rates(results, t_value)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()