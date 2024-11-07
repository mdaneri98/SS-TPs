import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='velocity_analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class VelocityAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute()
        logging.info(f"Ruta base inicial: {self.base_path}")
        
        if not (self.base_path / "outputs").exists():
            logging.error(f"No se encontró el directorio outputs en {self.base_path}")
            raise FileNotFoundError(f"No se encontró el directorio outputs en {self.base_path}")
            
        self.base_path = self.base_path / "outputs"
        logging.info(f"Ruta base final: {self.base_path}")

    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y calcula la velocidad media del sistema
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                logging.warning(f"Archivo vacío: {file_path}")
                return None
                
            mean_velocities = []
            i = 0
            
            while i < len(lines):
                # Saltar el tiempo
                i += 1
                if i >= len(lines):
                    break
                
                # Leer velocidades de todas las partículas en este timestep
                velocities = []
                while i < len(lines) and ',' in lines[i]:
                    try:
                        parts = lines[i].strip().split(',')
                        if len(parts) >= 5:
                            vx = float(parts[3])
                            vy = float(parts[4])
                            if np.isfinite(vx) and np.isfinite(vy):  # Verificar valores finitos
                                v = np.sqrt(vx**2 + vy**2)
                                if np.isfinite(v):  # Verificar que la magnitud sea finita
                                    velocities.append(v)
                            else:
                                logging.debug(f"Valores no finitos en línea: vx={vx}, vy={vy}")
                    except (ValueError, IndexError) as e:
                        logging.debug(f"Error al procesar línea {i}: {e}")
                    i += 1
                
                if velocities:
                    mean_v = np.mean(velocities)
                    if np.isfinite(mean_v):  # Verificar que el promedio sea finito
                        mean_velocities.append(mean_v)
                    else:
                        logging.debug(f"Velocidad media no finita: {mean_v}")
            
            if not mean_velocities:
                logging.warning(f"No se encontraron velocidades válidas en {file_path}")
                return None
                
            final_mean = np.mean(mean_velocities)
            if not np.isfinite(final_mean):
                logging.warning(f"Promedio final no finito: {final_mean}")
                return None
                
            return final_mean
            
        except Exception as e:
            logging.error(f"Error al parsear archivo {file_path}: {str(e)}")
            return None

    def load_velocity_data(self):
        """
        Carga y analiza los datos de velocidad para todos los parámetros
        """
        results = []
        heuristic_path = self.base_path / "heuristic_analysis"
        
        if not heuristic_path.exists():
            logging.error(f"No se encontró el directorio: {heuristic_path}")
            return pd.DataFrame()
        
        logging.info(f"Buscando datos en: {heuristic_path}")
        
        param_dirs = [d for d in heuristic_path.iterdir() 
                    if d.is_dir() and d.name.startswith("ap_")]
        
        if not param_dirs:
            logging.error("No se encontraron directorios de parámetros")
            return pd.DataFrame()
        
        for param_dir in param_dirs:
            logging.info(f"Procesando directorio: {param_dir}")
            
            try:
                dir_parts = param_dir.name.split('_')
                ap_val = float(dir_parts[1])
                bp_val = float(dir_parts[3])
                
                velocities = []
                valid_sims = 0
                total_sims = 0
                
                for sim_dir in param_dir.glob("sim_*"):
                    total_sims += 1
                    dynamic_file = sim_dir / "dynamic.txt"
                    
                    if not dynamic_file.exists():
                        logging.debug(f"Archivo no encontrado: {dynamic_file}")
                        continue
                    
                    if dynamic_file.stat().st_size == 0:
                        logging.debug(f"Archivo vacío: {dynamic_file}")
                        continue
                        
                    mean_vel = self.parse_dynamic_file(dynamic_file)
                    if mean_vel is not None and np.isfinite(mean_vel):
                        velocities.append(mean_vel)
                        valid_sims += 1
                
                if valid_sims > 0:
                    mean_vel = np.mean(velocities)
                    std_vel = np.std(velocities)
                    
                    if np.isfinite(mean_vel) and np.isfinite(std_vel):
                        results.append({
                            'ap': ap_val,
                            'bp': bp_val,
                            'mean_velocity': mean_vel,
                            'std_velocity': std_vel,
                            'valid_sims': valid_sims,
                            'total_sims': total_sims
                        })
                        logging.info(f"Procesado: ap={ap_val}, bp={bp_val}, "
                                f"velocidad media={mean_vel:.2f} ± {std_vel:.2f} "
                                f"({valid_sims}/{total_sims} simulaciones válidas)")
                    else:
                        logging.warning(f"Estadísticas no finitas para ap={ap_val}, bp={bp_val}")
                else:
                    logging.warning(f"No hay simulaciones válidas para ap={ap_val}, bp={bp_val}")
            
            except Exception as e:
                logging.error(f"Error al procesar directorio {param_dir}: {str(e)}")
                continue
        
        return pd.DataFrame(results)

    def plot_velocity_heatmap(self):
        """
        Genera heatmap de velocidad media
        """
        logging.info("Iniciando análisis de velocidad media")
        df = self.load_velocity_data()
        
        if df.empty:
            logging.error("No hay datos para analizar")
            return None
        
        try:
            plt.figure(figsize=(10, 8))
            
            # Crear pivot table y ordenar índices
            pivot_vel = df.pivot(index='ap', columns='bp', values='mean_velocity')
            pivot_vel = pivot_vel.sort_index(ascending=False)  # Ordenar ap de mayor a menor
            pivot_vel = pivot_vel.sort_index(axis=1)  # Ordenar bp de menor a mayor
            
            # Crear heatmap
            sns.heatmap(pivot_vel, cmap='viridis', 
                       annot=False,
                       cbar_kws={'label': 'Velocidad media (m/s)'})
            
            #plt.title('Velocidad Media del Sistema')
            plt.xlabel(r'$B_p$')
            plt.ylabel(r'$A_p$')
            
            plt.tight_layout()
            plt.savefig(self.base_path / 'velocity_heatmap.png', dpi=300)
            plt.close()
            
            # Guardar resultados en CSV
            df.to_csv(self.base_path / 'velocity_analysis.csv', index=False)
            
            # Encontrar mejores parámetros
            best_velocity = df.loc[df['mean_velocity'].idxmax()]
            
            return {
                'best_params': {
                    'ap': best_velocity['ap'],
                    'bp': best_velocity['bp'],
                    'velocity': best_velocity['mean_velocity'],
                    'std': best_velocity['std_velocity']
                }
            }
            
        except Exception as e:
            logging.error(f"Error durante el análisis: {str(e)}")
            return None

if __name__ == "__main__":
    try:
        analyzer = VelocityAnalyzer()
        results = analyzer.plot_velocity_heatmap()
        
        if results:
            print("\nMejores parámetros encontrados:")
            print(f"ap={results['best_params']['ap']}, "
                  f"bp={results['best_params']['bp']}")
            print(f"Velocidad media: {results['best_params']['velocity']:.2f} "
                  f"± {results['best_params']['std']:.2f} m/s")
        else:
            print("\nNo se pudieron determinar los mejores parámetros")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")