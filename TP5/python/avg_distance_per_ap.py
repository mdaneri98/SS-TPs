import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bp_distance_analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class BpAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute()
        logging.info(f"Ruta base inicial: {self.base_path}")
        
        if not (self.base_path / "outputs").exists():
            logging.error(f"No se encontró el directorio outputs en {self.base_path}")
            raise FileNotFoundError(f"No se encontró el directorio outputs en {self.base_path}")
            
        self.base_path = self.base_path / "outputs"
        logging.info(f"Ruta base final: {self.base_path}")
        self.setup_output_dirs()
        
    def setup_output_dirs(self):
        self.output_dir = self.base_path / "bp_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_available_parameters(self):
        heuristic_path = self.base_path / "heuristic_analysis"
        bp_values = set()
        ap_values = set()
        
        for param_dir in heuristic_path.iterdir():
            if param_dir.is_dir() and param_dir.name.startswith("ap_"):
                try:
                    match = re.match(r"ap_(\d+\.\d+)_bp_(\d+\.\d+)", param_dir.name)
                    if match:
                        ap = float(match.group(1))
                        bp = float(match.group(2))
                        ap_values.add(ap)
                        bp_values.add(bp)
                except ValueError:
                    continue
        
        return sorted(list(ap_values)), sorted(list(bp_values))

    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y retorna todas las posiciones
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            time_positions = []
            current_step = []
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:  # Saltar líneas vacías
                    i += 1
                    continue
                    
                if ',' not in line:  # Marca de tiempo
                    if current_step:  # Guardar paso anterior si existe
                        time_positions.append(current_step)
                        current_step = []
                else:  # Línea de posición
                    try:
                        parts = line.split(',')
                        if len(parts) >= 3:
                            pos = {
                                'id': int(parts[0]),
                                'x': float(parts[1]),
                                'y': float(parts[2])
                            }
                            current_step.append(pos)
                    except (ValueError, IndexError) as e:
                        logging.debug(f"Error al procesar línea {i}: {line}")
                i += 1
            
            # Agregar el último paso si existe
            if current_step:
                time_positions.append(current_step)
                
            return time_positions if time_positions else None
            
        except Exception as e:
            logging.error(f"Error al parsear {file_path}: {str(e)}")
            return None

    def calculate_mean_distance(self, file_path):
        """
        Calcula la distancia media entre el rugbier y los oponentes para una simulación
        """
        time_positions = self.parse_dynamic_file(file_path)
        if not time_positions:
            return None
            
        distances_per_timestep = []
        
        for step_positions in time_positions:
            # Separar rugbier y oponentes
            rugbier = None
            opponents = []
            
            for pos in step_positions:
                if pos['id'] == 0:
                    rugbier = pos
                else:
                    opponents.append(pos)
            
            if not rugbier or not opponents:
                continue
                
            # Calcular distancias a cada oponente
            step_distances = []
            for opp in opponents:
                dist = np.sqrt(
                    (rugbier['x'] - opp['x'])**2 + 
                    (rugbier['y'] - opp['y'])**2
                )
                step_distances.append(dist)
            
            if step_distances:
                # Promedio de distancias para este paso de tiempo
                distances_per_timestep.append(np.mean(step_distances))
        
        if not distances_per_timestep:
            return None
            
        # Promedio de todas las distancias medias
        return np.mean(distances_per_timestep)

    def analyze_ap_variation(self, bp_value):
        """
        Analiza todas las simulaciones para un valor de bp dado
        """
        results = []
        heuristic_path = self.base_path / "heuristic_analysis"
        
        for ap in self.ap_values:
            dir_name = f"ap_{ap:.2f}_bp_{bp_value:.2f}"
            param_dir = heuristic_path / dir_name
            
            if not param_dir.exists():
                logging.warning(f"Directorio no encontrado: {param_dir}")
                continue
            
            logging.info(f"Analizando Ap = {ap}")
            simulation_distances = []
            
            # Analizar cada simulación en el directorio
            for sim_dir in param_dir.glob("sim_*"):
                dynamic_path = sim_dir / "dynamic.txt"
                if not dynamic_path.exists():
                    continue
                
                mean_distance = self.calculate_mean_distance(dynamic_path)
                if mean_distance is not None:
                    simulation_distances.append(mean_distance)
            
            if simulation_distances:
                results.append({
                    'ap': ap,
                    'mean_distance': np.mean(simulation_distances),
                    'std_distance': np.std(simulation_distances),
                    'n_sims': len(simulation_distances)
                })
                logging.info(f"Ap={ap}: media={results[-1]['mean_distance']:.2f}, "
                        f"std={results[-1]['std_distance']:.2f}, "
                        f"n={results[-1]['n_sims']}")
        
        return pd.DataFrame(results)

def plot_ap_analysis(self, results):
    """
    Genera el gráfico de distancia media vs ap
    """
    plt.figure(figsize=(10, 6))
    
    plt.errorbar(results['ap'], results['mean_distance'],
                yerr=results['std_distance'],
                fmt='o-', color='blue', 
                capsize=5, capthick=1,
                label='Distancia media')
    
    plt.xlabel('$A_p$')
    plt.ylabel('Distancia media (m)')
    plt.grid(True)
    
    output_path = self.output_dir / 'ap_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    def plot_bp_analysis(self, results):
        """
        Genera el gráfico de distancia media vs bp
        """
        plt.figure(figsize=(10, 6))
        
        plt.errorbar(results['bp'], results['mean_distance'],
                    yerr=results['std_distance'],
                    fmt='o-', color='blue', 
                    capsize=5, capthick=1,
                    label='Distancia media')
        
        plt.xlabel('$B_p$ (m)')
        plt.ylabel('Distancia media (m)')
        plt.grid(True)
        
        output_path = self.output_dir / 'bp_analysis.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    try:
        current_dir = Path.cwd()
        print(f"Directorio actual: {current_dir}")
        print(f"Contenido del directorio:")
        for item in current_dir.iterdir():
            print(f"  {item}")
        
        analyzer = BpAnalyzer()
        ap_values, bp_values = analyzer.get_available_parameters()
        
        if not ap_values or not bp_values:
            logging.error("No se encontraron valores de parámetros")
            exit(1)
            
        analyzer.ap_values = ap_values
        
        print(f"\nValores de Ap disponibles: {ap_values}")
        print(f"Valores de Bp disponibles: {bp_values}")
        
        # Usar el primer valor de bp encontrado
        bp_value = 0.8 # bp_values[0]
        print(f"\nAnalizando con Bp = {bp_value}")
        
        results = analyzer.analyze_ap_variation(bp_value)
        
        if not results.empty:
            analyzer.plot_ap_analysis(results)
            print("\nEstadísticas de distancia media vs Ap:")
            print(results.to_string(index=False))
            print(f"\nResultados guardados en {analyzer.output_dir}")
        else:
            logging.error("No se pudo completar el análisis")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")