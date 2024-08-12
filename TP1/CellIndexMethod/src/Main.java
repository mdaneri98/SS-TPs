import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class Configuration {
    private int L;
    private int N;

    private double maxParticleRadius;
    private List<Particle> particleList;

    public Configuration(int l, int n, double maxParticleRadius, List<Particle> particleList) {
        L = l;
        N = n;
        this.particleList = particleList;
        this.maxParticleRadius = maxParticleRadius;
    }

    public int getL() {
        return L;
    }

    public int getN() {
        return N;
    }

    public double getMaxParticleRadius() {
        return maxParticleRadius;
    }

    public List<Particle> getParticleList() {
        return particleList;
    }

    @Override
    public String toString() {
        return "Configuration{" +
                "L=" + L +
                ", N=" + N +
                ", maxParticleRadius=" + maxParticleRadius +
                '}';
    }

}

class ParticleLoader {

    public static Configuration loadParticlesFromFile(String filePathStatic, String fileDynamicPath) {
        List<Particle> particlesList = new ArrayList<>();
        int L = 0;
        int N = 0;
        double maxParticleRadius = 0;

        try {
            BufferedReader br = new BufferedReader(new FileReader(filePathStatic));
            String linea;

            // Leer las primeras 3 líneas y guardarlas en variables especiales
            N = Integer.parseInt(br.readLine().trim());
            L = Integer.parseInt(br.readLine().trim());

            // Leer y retornar solo el primer valor de cada par de valores
            int i = 0;
            while ((linea = br.readLine()) != null) {
                String[] valores = linea.trim().split(" ");
                double r = Double.parseDouble(valores[0]);

                if (r > maxParticleRadius){
                    maxParticleRadius = r;
                }

                Particle particle = new Particle(i, 0 , 0 , r);
                particlesList.add(particle);
                i++;
            }

            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(fileDynamicPath))) {
            //Salteamos la primer linea.
            reader.readLine();

            String line;
            int id = 0;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.trim().replace("   ", " ").split(" ");
                double posX = Double.parseDouble(parts[0]);
                double posY = Double.parseDouble(parts[1]);

                Particle p = particlesList.get(id);
                p.setXY(posX, posY);
                id++;
            }
        } catch (IOException e) {
            System.err.println("Error leyendo el archivo: " + e.getMessage());
        }

        return new Configuration(L, N, maxParticleRadius, particlesList);
    }
}

public class Main {
    public static void main(String[] args) {
        try {
            int M = 5;

            Configuration config = ParticleLoader.loadParticlesFromFile("/Users/matiasdaneri/Documents/ITBA/4to/Simulación de Sistemas/SS-TPs/TP1/CellIndexMethod/src/Static100.txt", "/Users/matiasdaneri/Documents/ITBA/4to/Simulación de Sistemas/SS-TPs/TP1/CellIndexMethod/src/Dynamic100.txt");

            // Crear una instancia de CIMImpl
            CIMImpl cim = new CIMImpl(M, config.getN(), config.getL(), config.getMaxParticleRadius(), config.getParticleList());

            cim.save("./test", 12, true);

            System.out.println("Configuración utilizada: " + config);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}