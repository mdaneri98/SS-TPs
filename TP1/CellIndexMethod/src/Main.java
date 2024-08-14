import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;






public class Main {


    public static Map<Integer, List<Particle>> findInteractionsBruteForce(double rc, List<Particle> particles) {
        Map<Integer, List<Particle>> interactions = new HashMap<>();

        for (Particle p1 : particles) {
            for (Particle p2 : particles) {
                if (p1 != p2) {
                    double dx = p1.getPosX() - p2.getPosX();
                    double dy = p1.getPosY() - p2.getPosY();
                    double centerDistance = Math.sqrt(dx * dx + dy * dy);

                    // Si el borde está dentro de rc => Verdadero.
                    double distance = centerDistance - p1.getRadius() - p2.getRadius();
                    if ( distance <= 0 || distance <= (rc - p1.getRadius()) ) {
                        interactions.putIfAbsent(p1.getId(), new ArrayList<>());
                        interactions.get(p1.getId()).add(p2);

                        // Se puede optimizar si no volvemos a recorrer las particulas que ya agregamos de p2.
                        interactions.putIfAbsent(p2.getId(), new ArrayList<>());
                        interactions.get(p2.getId()).add(p1);
                    }
                }
            }
        }
        return interactions;
    }


    public static void main(String[] args) {
        try {

            double rc = 1;
            int L = 20;
            double pr = 0.5;
            int M = 5;

            CIMConfig config = CIMConfig.loadFromFile("C:\\Users\\mdane\\Documents\\SS-TPs\\TP1\\CellIndexMethod\\src\\Static100.txt", "C:\\Users\\mdane\\Documents\\SS-TPs\\TP1\\CellIndexMethod\\src\\Dynamic100.txt");
            System.out.println("Configuración utilizada: " + config);

            // Crear una instancia de CIMImpl
            //CIMImpl cim = new CIMImpl(M, config.getN(), config.getL(), config.getMaxParticleRadius(), config.getParticleList());

            // Ej2.
            CIMImpl cim = new CIMImpl(M, 100000, L, pr, null);
            config.setParticleList(cim.getParticlesList());

            long start = System.currentTimeMillis();
            Main.findInteractionsBruteForce(rc, config.getParticleList());
            long finish = System.currentTimeMillis();
            System.out.println("Tiempo de ejecucion por fuerza bruta:" + (finish-start) + " milisegundos");

            start = System.currentTimeMillis();
            Map<Integer, List<Particle>> interactions = cim.findInteractions(rc, true);
            finish = System.currentTimeMillis();
            cim.save("./test", interactions);

            System.out.println("Tiempo de ejecucion por CIM:" + (finish-start) + " milisegundos");


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}