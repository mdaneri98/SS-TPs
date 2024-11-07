import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='velocity_analysis.log'
)

class VelocityAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute() / "outputs"
        if not self.base_path.exists():
            raise FileNotFoundError(f"No se encontró el directorio outputs en {base_path}")
            
    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y retorna las velocidades del jugador y los demás
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            times = []
            player_velocities = []
            others_velocities = []
            
            i = 0
            while i < len(lines):
                # Leer tiempo
                try:
                    time = float(lines[i].strip())
                    times.append(time)
                except ValueError:
                    i += 1
                    continue
                
                i += 1
                if i >= len(lines):
                    break
                    
                # Leer línea del jugador
                player_line = lines[i].strip().split(',')
                if len(player_line) >= 4:
                    vx = float(player_line[3])
                    vy = float(player_line[4])
                    player_vel = np.sqrt(vx**2 + vy**2)
                    player_velocities.append(player_vel)
                
                # Leer velocidades de los otros jugadores
                other_vels = []
                i += 1
                while i < len(lines) and ',' in lines[i]:
                    parts = lines[i].strip().split(',')
                    if len(parts) >= 4:
                        vx = float(parts[3])
                        vy = float(parts[4])
                        vel = np.sqrt(vx**2 + vy**2)
                        other_vels.append(vel)
                    i += 1
                
                if other_vels:
                    others_velocities.append(np.mean(other_vels))
            
            return {
                'times': np.array(times),
                'player_velocities': np.array(player_velocities),
                'others_velocities': np.array(others_velocities)
            }
            
        except Exception as e:
            logging.error(f"Error al parsear archivo {file_path}: {str(e)}")
            return None

    def analyze_velocities(self, ap_value, bp_value):
	    """
	    Analiza las velocidades para un ap y bp específicos
	    """
	    results = []
	    
	    # Buscar directorio específico
	    dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
	    param_dir = self.base_path / "heuristic_analysis" / dir_name
	    
	    if not param_dir.exists():
	        logging.error(f"No se encontró el directorio: {param_dir}")
	        return None
	        
	    try:
	        sim_velocities = []
	        
	        # Procesar cada simulación
	        for sim_dir in param_dir.glob("sim_*"):
	            dynamic_file = sim_dir / "dynamic.txt"
	            if not dynamic_file.exists():
	                continue
	                
	            vel_data = self.parse_dynamic_file(dynamic_file)
	            if vel_data is None or len(vel_data['times']) == 0:
	                continue
	            
	            # Normalizar tiempo a [0,1]
	            max_time = vel_data['times'][-1]
	            if max_time <= 0:
	                logging.warning(f"Tiempo máximo inválido ({max_time}) en {sim_dir}")
	                continue
	                
	            normalized_times = vel_data['times'] / max_time
	            
	            # Verificar que los datos son válidos
	            if len(normalized_times) != len(vel_data['player_velocities']) or \
	               len(normalized_times) != len(vel_data['others_velocities']):
	                logging.warning(f"Longitudes inconsistentes en {sim_dir}")
	                continue
	            
	            sim_velocities.append({
	                'times': normalized_times,
	                'player_velocities': vel_data['player_velocities'],
	                'others_velocities': vel_data['others_velocities']
	            })
	        
	        if not sim_velocities:
	            logging.error("No se encontraron simulaciones válidas")
	            return None
	            
	        # Calcular promedio en cada punto temporal
	        time_points = np.linspace(0, 1, 100)  # 100 puntos normalizados
	        avg_player = np.zeros(len(time_points))
	        avg_others = np.zeros(len(time_points))
	        std_player = np.zeros(len(time_points))
	        std_others = np.zeros(len(time_points))
	        
	        for t_idx, t in enumerate(time_points):
	            player_vels = []
	            others_vels = []
	            
	            for sim in sim_velocities:
	                try:
	                    # Interpolar valores para este punto temporal
	                    if len(sim['times']) > 1:  # Asegurar que hay suficientes puntos para interpolar
	                        player_vel = np.interp(t, sim['times'], sim['player_velocities'])
	                        others_vel = np.interp(t, sim['times'], sim['others_velocities'])
	                        
	                        player_vels.append(player_vel)
	                        others_vels.append(others_vel)
	                except Exception as e:
	                    logging.warning(f"Error en interpolación: {str(e)}")
	                    continue
	            
	            if player_vels and others_vels:  # Solo si hay datos válidos
	                avg_player[t_idx] = np.mean(player_vels)
	                avg_others[t_idx] = np.mean(others_vels)
	                std_player[t_idx] = np.std(player_vels)
	                std_others[t_idx] = np.std(others_vels)
	        
	        print(f"\nSimulaciones válidas procesadas: {len(sim_velocities)}")
	        
	        return {
	            'times': time_points,
	            'avg_player': avg_player,
	            'std_player': std_player,
	            'avg_others': avg_others,
	            'std_others': std_others
	        }
	                
	    except Exception as e:
	        logging.error(f"Error procesando directorio {param_dir}: {str(e)}")
	        return None

    def plot_velocities(self, data, ap_value, bp_value):
        """
        Genera gráfico de velocidades promedio a lo largo del tiempo
        """
        if data is None:
            logging.error("No hay datos para graficar")
            return
            
        plt.figure(figsize=(12, 8))
        
        # Graficar velocidad del jugador
        plt.plot(data['times'], data['avg_player'], 
                label='Jugador', color='blue', linewidth=2)
        plt.fill_between(data['times'], 
                        data['avg_player'] - data['std_player'],
                        data['avg_player'] + data['std_player'],
                        alpha=0.3, color='blue')
        
        # Graficar velocidad de los otros
        plt.plot(data['times'], data['avg_others'],
                label='Oponentes', color='red', linewidth=2)
        plt.fill_between(data['times'],
                        data['avg_others'] - data['std_others'],
                        data['avg_others'] + data['std_others'],
                        alpha=0.3, color='red')
        
        #plt.title(f'Evolución de velocidades (ap={ap_value}, bp={bp_value})')
        plt.xlabel('Tiempo normalizado (s)')
        plt.ylabel('Velocidad (m/s)')
        plt.grid(True)
        plt.legend()
        
        output_file = self.base_path / f'velocity_analysis_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\nGráfico guardado en: {output_file}")

if __name__ == "__main__":
    # Especificar los valores de ap y bp a analizar
    ap_value = 35.0  # Modifica este valor
    bp_value = 1.2   # Modifica este valor
    
    try:
        analyzer = VelocityAnalyzer()
        data = analyzer.analyze_velocities(ap_value, bp_value)
        
        if data is not None:
            print(f"\nEstadísticas de velocidad para ap={ap_value}, bp={bp_value}:")
            print("\nVelocidad del jugador:")
            print(f"Promedio global: {np.mean(data['avg_player']):.2f} ± "
                  f"{np.mean(data['std_player']):.2f} m/s")
            print(f"Máxima: {np.max(data['avg_player']):.2f} m/s")
            print(f"Mínima: {np.min(data['avg_player']):.2f} m/s")
            
            print("\nVelocidad de los otros jugadores:")
            print(f"Promedio global: {np.mean(data['avg_others']):.2f} ± "
                  f"{np.mean(data['std_others']):.2f} m/s")
            print(f"Máxima: {np.max(data['avg_others']):.2f} m/s")
            print(f"Mínima: {np.min(data['avg_others']):.2f} m/s")
            
            analyzer.plot_velocities(data, ap_value, bp_value)
        else:
            print("No se pudieron analizar las velocidades")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")
        print(f"Error: {str(e)}")