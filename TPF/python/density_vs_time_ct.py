import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class DensityAnalyzer:
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

            return pd.DataFrame(particles_data)

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def read_doors_file(self, sim_path):
        """Lee el archivo doors.csv con la información de las puertas"""
        doors_path = sim_path / "doors.csv"
        try:
            # Leer CSV con encabezado y manejo de espacios
            df = pd.read_csv(doors_path, skipinitialspace=True)
            df['door_number'] = range(len(df))
            return df
        except Exception as e:
            print(f"Error reading doors file: {e}")
            return pd.DataFrame()

    def calculate_density(self, particles_data, doors_data, time, r_k=5):
        """Calcula la densidad en un tiempo específico para cada puerta y total"""
        if len(particles_data) == 0 or len(doors_data) == 0:
            return None

        # Obtener partículas en el tiempo específico
        particles_t = particles_data[particles_data['time'] == time]

        # Calcular densidades por puerta
        door_densities = {}

        for _, door in doors_data.iterrows():
            # Calcular centro de la puerta
            door_center_x = (door['initial_x'] + door['end_x']) / 2
            door_center_y = (door['initial_y'] + door['end_y']) / 2

            # Calcular distancias a esta puerta
            distances = np.sqrt(
                (particles_t['x'] - door_center_x)**2 +
                (particles_t['y'] - door_center_y)**2
            )

            if len(distances) >= r_k:
                # Obtener el radio r_k (distancia a la k-ésima partícula más cercana)
                r = np.sort(distances.values)[r_k-1]
                # Contar partículas dentro del radio
                n = len(distances[distances <= r])
                # Área de semicircunferencia
                area = np.pi * r**2 / 2
                density = n / area
            else:
                density = 0

            door_densities[f'door_{door["door_number"]}'] = density

        # Calcular densidad media total (promedio de todas las puertas)
        total_density = np.mean(list(door_densities.values()))

        return {
            'time': time,
            'total_density': total_density,
            'door_densities': door_densities
        }

    def analyze_densities(self, t_values, p_value):
        """Analiza la densidad para varios valores de t con un p fijo"""
        results = {}

        for t_value in t_values:
            sim_path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}" / "sim_000"

            particles_data = self.read_particles_file(sim_path)
            doors_data = self.read_doors_file(sim_path)

            if len(particles_data) > 0 and len(doors_data) > 0:
                # Calcular densidades para cada tiempo
                times = sorted(particles_data['time'].unique())
                densities = []

                for time in times:
                    density = self.calculate_density(particles_data, doors_data, time)
                    if density:
                        densities.append(density)

                if densities:
                    results[t_value] = {
                        'times': [d['time'] for d in densities],
                        'total_density': [d['total_density'] for d in densities]
                    }

        return results

    def plot_densities(self, results, p_value, output_dir="plots/density"):
        """Genera gráficos de densidad total vs tiempo para distintos valores de t"""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 6))

        for t_value, data in results.items():
            plt.plot(data['times'], data['total_density'], label=f't = {t_value}')

        plt.title(f'Densidad Total vs Tiempo (p = {p_value:.2f})')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Densidad Total (partículas/m²)')
        plt.legend(title="Valores de t")
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/density_vs_time_p{p_value:.2f}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    # Crear el analizador
    analyzer = DensityAnalyzer()

    # Definir parámetros a analizar
    t_values = [5, 10, 15, 20, 25, 30]  # Valores de tiempo de redecisión
    p_value = 0.5  # Valor fijo de probabilidad

    # Analizar densidades
    print("Analizando densidades...")
    results = analyzer.analyze_densities(t_values, p_value)

    # Generar gráficos
    print("Generando gráficos...")
    analyzer.plot_densities(results, p_value)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()
