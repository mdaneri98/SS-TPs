import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from scipy.interpolate import interp1d

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='centroid_analysis.log'
)

class CentroidAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute()
        self.setup_output_dirs()
        
    def setup_output_dirs(self):
        """Configura los directorios de salida"""
        self.output_dir = self.base_path / "outputs" / "centroid_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_dynamic_file(self, file_path):
        """Parser del archivo dynamic.txt"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            time_positions = []
            current_positions = []
            time_step = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if ',' not in line:  # Es una marca de tiempo
                    if current_positions:
                        time_positions.append({
                            'time': time_step,
                            'positions': current_positions
                        })
                    current_positions = []
                    time_step += 1
                else:  # Es una posición
                    parts = line.split(',')
                    if len(parts) >= 3:  # id,x,y,...
                        pos = {
                            'id': int(parts[0]),
                            'x': float(parts[1]),
                            'y': float(parts[2])
                        }
                        current_positions.append(pos)
            
            # Agregar el último conjunto de posiciones
            if current_positions:
                time_positions.append({
                    'time': time_step,
                    'positions': current_positions
                })
                
            return time_positions
            
        except Exception as e:
            logging.error(f"Error al parsear dynamic.txt: {str(e)}")
            return None

    def calculate_centroid_distance(self, time_positions):
        """Calcula la distancia al centroide para cada timestep"""
        metrics_data = []
        
        for time_step in time_positions:
            positions = time_step['positions']
            rugbier = next((p for p in positions if p['id'] == 0), None)
            others = [p for p in positions if p['id'] != 0]
            
            if not rugbier or not others:
                continue
            
            # Calcular centroide
            centroid_x = np.mean([p['x'] for p in others])
            centroid_y = np.mean([p['y'] for p in others])
            
            # Calcular distancia al centroide
            distance = np.sqrt((rugbier['x'] - centroid_x)**2 + 
                             (rugbier['y'] - centroid_y)**2)
            
            metrics_data.append({
                'time': time_step['time'],
                'centroid_distance': distance,
                'centroid_x': centroid_x,
                'centroid_y': centroid_y,
                'rugbier_x': rugbier['x'],
                'rugbier_y': rugbier['y']
            })
        
        return pd.DataFrame(metrics_data)

    def analyze_parameter_set(self, ap_value, bp_value):
        """Analiza todas las simulaciones para un conjunto de parámetros"""
        dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
        param_dir = self.base_path / "outputs" / "heuristic_analysis" / dir_name
        
        all_metrics = []
        valid_simulations = 0
        
        for sim_dir in param_dir.glob("sim_*"):
            dynamic_path = sim_dir / "dynamic.txt"
            if not dynamic_path.exists():
                continue
            
            time_positions = self.parse_dynamic_file(dynamic_path)
            if not time_positions:
                continue
            
            metrics = self.calculate_centroid_distance(time_positions)
            if len(metrics) > 1:  # Asegurar que hay más de un timestep
                # Normalizar tiempo a [0,1]
                metrics['normalized_time'] = metrics['time'] / metrics['time'].max()
                all_metrics.append(metrics)
                valid_simulations += 1
        
        if not all_metrics:
            return None, None
        
        # Interpolar todas las simulaciones a 100 puntos
        time_points = np.linspace(0, 1, 100)
        interpolated_metrics = []
        
        for metrics in all_metrics:
            interpolated = {}
            for column in ['centroid_distance']:
                interpolator = interp1d(metrics['normalized_time'], 
                                      metrics[column],
                                      kind='linear',
                                      fill_value='extrapolate')
                interpolated[column] = interpolator(time_points)
            interpolated_metrics.append(pd.DataFrame(interpolated, index=time_points))
        
        avg_metrics = pd.concat(interpolated_metrics).groupby(level=0).mean()
        std_metrics = pd.concat(interpolated_metrics).groupby(level=0).std()
        
        return avg_metrics, std_metrics

    def plot_centroid_analysis(self, avg_metrics, std_metrics, ap_value, bp_value):
        """Genera visualización de la distancia al centroide"""
        plt.figure(figsize=(12, 8))
        
        time_index = avg_metrics.index
        
        plt.plot(time_index, avg_metrics['centroid_distance'],
                color='blue', 
                linewidth=2)
        
        plt.fill_between(time_index,
                        avg_metrics['centroid_distance'] - std_metrics['centroid_distance'],
                        avg_metrics['centroid_distance'] + std_metrics['centroid_distance'],
                        alpha=0.3,
                        color='blue')
        
        plt.xlabel('Tiempo normalizado (s)')
        plt.ylabel('Distancia (m)')
        #plt.title(f'Distancia al centroide del equipo (ap={ap_value}, bp={bp_value})')
        plt.grid(True)
        #plt.legend()
        
        output_path = self.output_dir / f'centroid_analysis_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    try:
        ap_value = 35.0
        bp_value = 1.2
        
        analyzer = CentroidAnalyzer()
        avg_metrics, std_metrics = analyzer.analyze_parameter_set(ap_value, bp_value)
        
        if avg_metrics is not None:
            analyzer.plot_centroid_analysis(avg_metrics, std_metrics, ap_value, bp_value)
            logging.info("\nAnálisis completado y gráficos guardados")
            
            # Imprimir estadísticas
            print("\nEstadísticas de distancia al centroide:")
            print(f"Distancia media global: {avg_metrics['centroid_distance'].mean():.2f} m")
            print(f"Distancia máxima: {avg_metrics['centroid_distance'].max():.2f} m")
            print(f"Distancia mínima: {avg_metrics['centroid_distance'].min():.2f} m")
        else:
            logging.error("No se pudo completar el análisis")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")