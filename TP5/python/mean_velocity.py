import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mean_velocity_analysis.log'
)

class MeanVelocityAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute() / "outputs"
        if not self.base_path.exists():
            raise FileNotFoundError(f"No se encontró el directorio outputs en {base_path}")

    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y calcula la velocidad media
        v(t) = (1/N) Σ|vi(t)|
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            times = []
            mean_velocities = []
            
            i = 0
            while i < len(lines):
                # Leer tiempo
                try:
                    time = float(lines[i].strip())
                    times.append(time)
                except ValueError:
                    i += 1
                    continue
                
                # Leer velocidades de todas las partículas
                velocities = []
                i += 1
                while i < len(lines) and ',' in lines[i]:
                    parts = lines[i].strip().split(',')
                    if len(parts) >= 5:
                        vx = float(parts[3])
                        vy = float(parts[4])
                        v_magnitude = np.sqrt(vx**2 + vy**2)
                        velocities.append(v_magnitude)
                    i += 1
                
                if velocities:
                    # Calcular velocidad media para este timestep
                    mean_v = np.mean(velocities)
                    mean_velocities.append(mean_v)
            
            return np.array(times), np.array(mean_velocities)
            
        except Exception as e:
            logging.error(f"Error al parsear archivo {file_path}: {str(e)}")
            return None, None

    def analyze_mean_velocity(self, ap_value, bp_value):
        """
        Analiza la velocidad media para un set específico de parámetros
        """
        dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
        param_dir = self.base_path / "heuristic_analysis" / dir_name
        
        if not param_dir.exists():
            logging.error(f"No se encontró el directorio: {param_dir}")
            return None
        
        all_times = []
        all_mean_velocities = []
        valid_simulations = 0
        
        # Procesar cada simulación
        for sim_dir in param_dir.glob("sim_*"):
            dynamic_file = sim_dir / "dynamic.txt"
            if not dynamic_file.exists():
                continue
            
            times, mean_velocities = self.parse_dynamic_file(dynamic_file)
            if times is None or len(times) <= 1:
                continue
            
            # Normalizar tiempo a [0,1]
            norm_times = times/times[-1]
            
            all_times.append(norm_times)
            all_mean_velocities.append(mean_velocities)
            valid_simulations += 1
        
        if not all_mean_velocities:
            return None
        
        # Interpolar todas las simulaciones a puntos de tiempo comunes
        time_points = np.linspace(0, 1, 100)
        interpolated_velocities = []
        
        for t, v in zip(all_times, all_mean_velocities):
            if len(t) > 1:  # Asegurar suficientes puntos para interpolar
                interp_v = np.interp(time_points, t, v)
                interpolated_velocities.append(interp_v)
        
        # Calcular promedio y desviación estándar entre realizaciones
        mean_v = np.mean(interpolated_velocities, axis=0)
        std_v = np.std(interpolated_velocities, axis=0)
        
        print(f"\nSimulaciones válidas procesadas: {valid_simulations}")
        
        return {
            'times': time_points,
            'mean_v': mean_v,
            'std_v': std_v,
            'valid_sims': valid_simulations
        }

    def plot_mean_velocity(self, data, ap_value, bp_value):
        """
        Genera gráfico de velocidad media vs tiempo normalizado
        """
        if data is None:
            logging.error("No hay datos para graficar")
            return
        
        plt.figure(figsize=(12, 8))
        
        plt.plot(data['times'], data['mean_v'], 
                color='blue', linewidth=2)
        plt.fill_between(data['times'],
                        data['mean_v'] - data['std_v'],
                        data['mean_v'] + data['std_v'],
                        alpha=0.3, color='blue')
        
        #plt.title(f'Velocidad Media del Sistema (ap={ap_value}, bp={bp_value})')
        plt.xlabel('Tiempo normalizado (s)')
        plt.ylabel('Velocidad media (m/s)')
        plt.grid(True)
        
        # Calcular y mostrar promedios globales
        overall_mean = np.mean(data['mean_v'])
        overall_std = np.mean(data['std_v'])
        plt.axhline(y=overall_mean, color='r', linestyle='--', 
                   label=f'Promedio global: {overall_mean:.2f} ± {overall_std:.2f} m/s')
        
        plt.legend()
        
        output_file = self.base_path / f'mean_velocity_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\nGráfico guardado en: {output_file}")

if __name__ == "__main__":
    # Especificar los valores de ap y bp a analizar
    ap_value = 35.0  # Modifica este valor
    bp_value = 1.2   # Modifica este valor
    
    try:
        analyzer = MeanVelocityAnalyzer()
        data = analyzer.analyze_mean_velocity(ap_value, bp_value)
        
        if data is not None:
            print(f"\nEstadísticas de velocidad media para ap={ap_value}, bp={bp_value}:")
            print(f"Promedio global: {np.mean(data['mean_v']):.2f} ± "
                  f"{np.mean(data['std_v']):.2f} m/s")
            print(f"Velocidad máxima: {np.max(data['mean_v']):.2f} m/s")
            print(f"Velocidad mínima: {np.min(data['mean_v']):.2f} m/s")
            print(f"Simulaciones válidas: {data['valid_sims']}")
            
            analyzer.plot_mean_velocity(data, ap_value, bp_value)
        else:
            print("No se pudo analizar la velocidad media")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")
        print(f"Error: {str(e)}")