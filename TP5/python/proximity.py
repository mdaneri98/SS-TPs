import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from scipy.spatial import ConvexHull
from scipy.stats import gaussian_kde
import os
from scipy.interpolate import interp1d

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='rugby_analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class EnhancedCPMAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute()
        self.setup_output_dirs()
        
    def setup_output_dirs(self):
        """Configura los directorios de salida"""
        self.output_dir = self.base_path / "outputs" / "proximity"
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
                    try:
                        parts = line.split(',')
                        if len(parts) >= 6:  # id,x,y,vx,vy,radius
                            pos = {
                                'id': int(parts[0]),
                                'x': float(parts[1]),
                                'y': float(parts[2]),
                                'vx': float(parts[3]),
                                'vy': float(parts[4]),
                                'radius': float(parts[5])
                            }
                            current_positions.append(pos)
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Error al parsear línea: {line}, Error: {str(e)}")
                        continue
            
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

    def calculate_enhanced_metrics(self, time_positions):
        """Calcula métricas mejoradas de proximidad"""
        metrics_data = []
        
        for time_step in time_positions:
            positions = time_step['positions']
            rugbier = next((p for p in positions if p['id'] == 0), None)
            
            if not rugbier:
                continue
            
            distances = []
            velocities_alignment = []
            for pos in positions:
                if pos['id'] != 0:
                    # Distancia
                    dist = np.sqrt((pos['x'] - rugbier['x'])**2 + 
                                 (pos['y'] - rugbier['y'])**2)
                    distances.append(dist)
                    
                    # Alineación de velocidades
                    v1 = np.array([pos['vx'], pos['vy']])
                    v2 = np.array([rugbier['vx'], rugbier['vy']])
                    
                    norm_v1 = np.linalg.norm(v1)
                    norm_v2 = np.linalg.norm(v2)
                    if norm_v1 > 0 and norm_v2 > 0:
                        alignment = np.dot(v1, v2) / (norm_v1 * norm_v2)
                        velocities_alignment.append(alignment)
            
            if distances and velocities_alignment:
                dist_25th = np.percentile(distances, 25)
                dist_75th = np.percentile(distances, 75)
                
                metrics_data.append({
                    'time': time_step['time'],
                    'mean_distance': np.mean(distances),
                    'median_distance': np.median(distances),
                    'distance_25th': dist_25th,
                    'distance_75th': dist_75th,
                    'distance_iqr': dist_75th - dist_25th,
                    'mean_alignment': np.mean(velocities_alignment),
                    'min_distance': np.min(distances),
                    'max_distance': np.max(distances),
                    'std_distance': np.std(distances),
                    'n_close_players': sum(1 for d in distances if d < 10)
                })
        
        return pd.DataFrame(metrics_data)

    def normalize_metrics(self, metrics_df):
        """Normaliza el tiempo de una simulación a un rango [0,1]"""
        if metrics_df is None or len(metrics_df) == 0:
            return None
            
        if 'time' not in metrics_df.columns and metrics_df.index.name != 'time':
            metrics_df = metrics_df.reset_index(level=0)
        
        max_time = metrics_df['time'].max()
        if max_time == 0:
            logging.warning("Tiempo máximo es 0, no se puede normalizar")
            return None
            
        metrics_df['normalized_time'] = metrics_df['time'] / max_time
        return metrics_df

    def interpolate_metrics(self, normalized_df, num_points=100):
        """Interpola las métricas en puntos de tiempo normalizados uniformes"""
        if normalized_df is None or len(normalized_df) == 0:
            return None
            
        time_points = np.linspace(0, 1, num_points)
        interpolated_data = {}
        
        for column in normalized_df.columns:
            if column not in ['time', 'normalized_time']:
                try:
                    interpolator = interp1d(normalized_df['normalized_time'], 
                                         normalized_df[column],
                                         kind='linear',
                                         fill_value='extrapolate')
                    interpolated_data[column] = interpolator(time_points)
                except Exception as e:
                    logging.warning(f"Error interpolando columna {column}: {str(e)}")
                    continue
        
        return pd.DataFrame(interpolated_data, index=time_points)

    def analyze_parameter_set(self, ap_value, bp_value):
        """Analiza todas las simulaciones para un conjunto de parámetros"""
        dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
        param_dir = self.base_path / "outputs" / "heuristic_analysis" / dir_name
        
        all_interpolated_metrics = []
        simulation_durations = []
        single_timestep_count = 0
        valid_simulations = 0
        total_simulations = 0
        
        if not param_dir.exists():
            logging.error(f"No se encontró el directorio: {param_dir}")
            return None, None, None, None
        
        for sim_dir in param_dir.iterdir():
            if not sim_dir.is_dir() or not sim_dir.name.startswith("sim_"):
                continue
                
            total_simulations += 1
            dynamic_path = sim_dir / "dynamic.txt"
            if not dynamic_path.exists():
                logging.warning(f"No se encontró dynamic.txt en {sim_dir}")
                continue
                
            time_positions = self.parse_dynamic_file(dynamic_path)
            if not time_positions:
                logging.warning(f"No se pudieron parsear posiciones en {sim_dir}")
                continue
                
            if len(time_positions) <= 1:
                single_timestep_count += 1
                logging.info(f"Simulación {sim_dir.name} tiene solo {len(time_positions)} timestep(s)")
                continue
            
            try:
                metrics = self.calculate_enhanced_metrics(time_positions)
                if len(metrics) == 0:
                    logging.warning(f"No se pudieron calcular métricas para {sim_dir.name}")
                    continue
                    
                normalized_metrics = self.normalize_metrics(metrics)
                if normalized_metrics is None:
                    continue
                    
                interpolated_metrics = self.interpolate_metrics(normalized_metrics)
                if interpolated_metrics is None:
                    continue
                
                simulation_durations.append(len(time_positions))
                all_interpolated_metrics.append(interpolated_metrics)
                valid_simulations += 1
                
            except Exception as e:
                logging.error(f"Error procesando simulación {sim_dir.name}: {str(e)}")
                continue
        
        logging.info(f"\nEstadísticas para {dir_name}:")
        logging.info(f"Total de simulaciones encontradas: {total_simulations}")
        logging.info(f"Simulaciones con un solo timestep: {single_timestep_count}")
        logging.info(f"Simulaciones válidas procesadas: {valid_simulations}")
        
        if not all_interpolated_metrics:
            logging.error("No hay suficientes simulaciones válidas para analizar")
            return None, None, None, None
            
        avg_metrics = pd.concat(all_interpolated_metrics).groupby(level=0).mean()
        std_metrics = pd.concat(all_interpolated_metrics).groupby(level=0).std()
        
        avg_duration = np.mean(simulation_durations)
        std_duration = np.std(simulation_durations)
        
        return avg_metrics, std_metrics, avg_duration, std_duration

    def plot_enhanced_analysis(self, avg_metrics, std_metrics, ap_value, bp_value, avg_duration, std_duration):
        """Genera visualizaciones mejoradas"""
        plt.style.use('default')
        fig, axes = plt.subplots(2, 1, figsize=(12, 16))
        
        # Plot 1: Distancias y variabilidad
        ax = axes[0]
        time_index = avg_metrics.index
        
        ax.plot(time_index, avg_metrics['median_distance'], 
                label='Distancia mediana', color='blue', linewidth=2)
        ax.fill_between(time_index, 
                       avg_metrics['distance_25th'],
                       avg_metrics['distance_75th'],
                       alpha=0.3, color='blue',
                       label='Rango intercuartil')
        
        ax2 = ax.twinx()
        ax2.plot(time_index, avg_metrics['n_close_players'],
                color='red', linestyle='--', label='Jugadores cercanos (<10u)')
        
        ax.set_xlabel('Tiempo normalizado (0-1)')
        ax.set_ylabel('Distancia al rugbier principal (unidades)')
        ax2.set_ylabel('Número de jugadores cercanos')
        title = f'Análisis de proximidad (ap={ap_value}, bp={bp_value})\n'
        title += f'Duración promedio: {avg_duration:.1f} ± {std_duration:.1f} pasos'
        ax.set_title(title)
        
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        # Plot 2: Alineación y dispersión
        ax = axes[1]
        
        ax.plot(time_index, avg_metrics['mean_alignment'],
                label='Alineación media', color='green', linewidth=2)
        
        ax2 = ax.twinx()
        ax2.plot(time_index, avg_metrics['std_distance'],
                color='purple', linestyle='--', label='Dispersión (std)')
        
        ax.set_xlabel('Tiempo normalizado (0-1)')
        ax.set_ylabel('Alineación de velocidades (-1 a 1)')
        ax2.set_ylabel('Dispersión de distancias')
        ax.set_title('Alineación y dispersión del equipo')
        
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        plt.tight_layout()
        
        output_path = self.output_dir / f'analysis_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    try:
        ap_value = 4.0
        bp_value = 0.8
        
        analyzer = EnhancedCPMAnalyzer()
        avg_metrics, std_metrics, avg_duration, std_duration = analyzer.analyze_parameter_set(ap_value, bp_value)
        
        if avg_metrics is not None:
            analyzer.plot_enhanced_analysis(avg_metrics, std_metrics, ap_value, bp_value, avg_duration, std_duration)
            logging.info("\nAnálisis completado y gráficos guardados")
        else:
            logging.error("No se pudo completar el análisis")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")