import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='run_all_analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class AnalysisRunner:
    def __init__(self):
        # Lista de scripts a ejecutar en orden
        self.scripts = [
            # Análisis básicos de partículas
            "avg_radii_of_particles.py",
            "avg_va_of_particles.py",
            "avg_velocity_of_particles.py",
            "avg_distance_to_rugbier.py",
            
            # Análisis de proximidad y distancias
            "proximity.py",
            "mean_velocity.py",
            "mean_velocity_heatmap.py",
            
            # Gráficos y visualizaciones
            #"plot_trajectories.py",
            #"graph.py",
            #"graph_all.py",
            
            # Animación
            #"animation.py",
            
            # Análisis extra y best
            #"extras.py",
            "best.py",
            
            # Análisis final
            "analysis.py"
        ]

    def run_script(self, script_name):
        """Ejecuta un script individual y registra el resultado"""
        try:
            logging.info(f"Ejecutando {script_name}...")
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logging.info(f"✔ {script_name} ejecutado exitosamente")
                if result.stdout:
                    logging.debug(f"Salida de {script_name}:\n{result.stdout}")
            else:
                logging.error(f"✘ Error al ejecutar {script_name}")
                if result.stderr:
                    logging.error(f"Error:\n{result.stderr}")
                
            return result.returncode == 0
            
        except Exception as e:
            logging.error(f"✘ Error al intentar ejecutar {script_name}: {str(e)}")
            return False

    def run_all(self):
        """Ejecuta todos los scripts en orden"""
        logging.info("Iniciando ejecución de análisis")
        
        successful = 0
        failed = 0
        
        # Verificar que todos los scripts existen
        missing_scripts = [s for s in self.scripts if not Path(s).exists()]
        if missing_scripts:
            for script in missing_scripts:
                logging.error(f"No se encontró el script: {script}")
            raise FileNotFoundError(f"Faltan {len(missing_scripts)} scripts")
        
        # Ejecutar scripts
        for script in self.scripts:
            if self.run_script(script):
                successful += 1
            else:
                failed += 1
                
        # Resumen final
        logging.info("\nResumen de ejecución:")
        logging.info(f"✔ Scripts exitosos: {successful}")
        logging.info(f"✘ Scripts fallidos: {failed}")
        logging.info(f"Total scripts: {len(self.scripts)}")
        
        return successful, failed

if __name__ == "__main__":
    try:
        runner = AnalysisRunner()
        successful, failed = runner.run_all()
        
        if failed > 0:
            sys.exit(1)
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")
        sys.exit(1)