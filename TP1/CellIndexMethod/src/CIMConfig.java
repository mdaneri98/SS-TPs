import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class CIMConfig {
    private int L;
    private int N;

    private double maxParticleRadius;
    private List<Particle> particleList;

    public CIMConfig(int l, int n, double maxParticleRadius, List<Particle> particleList) {
        L = l;
        N = n;
        this.particleList = particleList;
        this.maxParticleRadius = maxParticleRadius;
    }

    public static CIMConfig loadFromFile(String filePathStatic, String fileDynamicPath) {
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
                String[] valores = linea.trim().split("\t");
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
            while ((line = reader.readLine()) != null) {
                String[] parts = line.trim().split("\t");

                int idx = Integer.parseInt(parts[0]);
                double posX = Double.parseDouble(parts[1]);
                double posY = Double.parseDouble(parts[2]);

                Particle p = particlesList.get(idx);
                p.setXY(posX, posY);
            }
        } catch (IOException e) {
            System.err.println("Error leyendo el archivo: " + e.getMessage());
        }

        return new CIMConfig(L, N, maxParticleRadius, particlesList);
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

    public void setParticleList(List<Particle> p) {
        this.particleList = p;
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
