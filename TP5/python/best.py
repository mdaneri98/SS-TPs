import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='outputs/n_analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class NSimulationAnalyzer:
    def __init__(self, base_path="./outputs/players_analysis"):
        self.base_path = Path(base_path).absolute()
        logging.info(f"Ruta base inicial: {self.base_path}")

    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y retorna todas las posiciones x del jugador con id=0
        """
        try:
            logging.debug(f"Intentando abrir archivo: {file_path}")
            with open(file_path, 'r') as f:
                lines = f.readlines()

            positions = []
            i = 0
            while i < len(lines):
                # Saltar la línea de tiempo
                if i >= len(lines):
                    break

                # Procesar líneas hasta encontrar una línea de tiempo
                line = lines[i].strip()
                if line and ',' in line:
                    parts = line.split(',')
                    try:
                        player_id = int(parts[0])
                        if player_id == 0:  # Solo procesar el jugador con id=0
                            x_pos = float(parts[1])
                            positions.append(x_pos)
                    except (ValueError, IndexError) as e:
                        logging.debug(f"Error al procesar línea {i}: {line}")
                i += 1

            return positions if positions else None

        except Exception as e:
            logging.error(f"Error al parsear dynamic.txt: {str(e)}")
            return None

    def analyze_trajectory(self, positions):
        """
        Analiza una trayectoria completa y retorna métricas relevantes
        """
        if not positions or len(positions) < 2:
            return None

        start_pos = positions[0]  # Posición inicial (cerca de x=100)
        final_pos = positions[-1]  # Posición final

        # Calculamos cuánto avanzó hacia la pared (x=0)
        # Un valor positivo significa que se movió hacia la pared
        distance_to_goal = start_pos - final_pos

        # Un try se logra si llegó a x=0 o lo cruzó
        try_achieved = final_pos <= 0

        return {
            'start_pos': start_pos,
            'final_pos': final_pos,
            'distance_to_goal': distance_to_goal,
            'try_achieved': try_achieved
        }

    def analyze_n_directories(self):
        """
        Analiza todas las carpetas N_xx y genera estadísticas para cada una
        """
        results = []
        n_dirs = [d for d in self.base_path.iterdir()
                  if d.is_dir() and d.name.startswith("N_")]

        for n_dir in sorted(n_dirs):
            n_value = int(n_dir.name.split('_')[1])
            logging.info(f"Analizando N = {n_value}")

            distances = []
            tries_achieved = 0
            total_sims = 0
            valid_sims = 0

            sim_dirs = [d for d in n_dir.iterdir()
                        if d.is_dir() and d.name.startswith("sim_")]

            for sim_dir in sim_dirs:
                total_sims += 1
                dynamic_path = sim_dir / "dynamic.txt"

                if not dynamic_path.exists():
                    continue

                positions = self.parse_dynamic_file(dynamic_path)
                if not positions:
                    continue

                sim_data = self.analyze_trajectory(positions)
                if sim_data is None:
                    continue

                valid_sims += 1
                distances.append(sim_data['distance_to_goal'])

                if sim_data['try_achieved']:
                    tries_achieved += 1

            if valid_sims > 0:
                results.append({
                    'N': n_value,
                    'avg_distance': np.mean(distances),
                    'std_distance': np.std(distances),
                    'try_ratio': tries_achieved / valid_sims,
                    'total_sims': total_sims,
                    'valid_sims': valid_sims
                })

        return pd.DataFrame(results)

    def plot_results(self, df):
        """
        Genera gráficos para los resultados
        """
        # Gráfico de distancia promedio vs N
        plt.figure(figsize=(10, 6))
        plt.errorbar(df['N'], df['avg_distance'], yerr=df['std_distance'],
                     fmt='o-', capsize=5)
        plt.xlabel('Cantidad de jugadores')
        plt.ylabel('Distancia (m)')
        #plt.title('Avance promedio hacia el try vs Cantidad de jugadores')
        plt.grid(True)
        plt.savefig('outputs/distance_vs_n.png')
        plt.close()

        # Gráfico de ratio de tries vs N
        plt.figure(figsize=(10, 6))
        plt.plot(df['N'], df['try_ratio'], 'o-')
        plt.xlabel('Cantidad de jugadores')
        plt.ylabel('Ratio de Tries Logrados')
        #plt.title('Ratio de Tries vs Cantidad de jugadores')
        plt.grid(True)
        plt.savefig('outputs/tries_vs_n.png')
        plt.close()

        return True


if __name__ == "__main__":
    try:
        analyzer = NSimulationAnalyzer()

        print("\nAnalizando directorios N...")
        results_df = analyzer.analyze_n_directories()

        if not results_df.empty:
            # Ordenar los resultados por 'N' en orden ascendente
            results_df = results_df.sort_values(by='N').reset_index(drop=True)

            print("\nResultados del análisis (ordenados por N):")
            print(results_df.to_string(index=False))

            print("\nGenerando gráficos...")
            analyzer.plot_results(results_df)

            # Guardar resultados en CSV
            results_df.to_csv('outputs/n_analysis_results.csv', index=False)
            print("\nResultados guardados en outputs/n_analysis_results.csv")

        else:
            print("\nNo se encontraron datos para analizar")

    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")