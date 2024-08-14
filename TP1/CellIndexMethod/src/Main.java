import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;



class ParticleLoader {


}

public class Main {
    public static void main(String[] args) {
        try {

            long start = System.currentTimeMillis();
            int M = 5;

            CIMConfig config = CIMConfig.loadFromFile("C:\\Users\\mdane\\Documents\\SS-TPs\\TP1\\CellIndexMethod\\src\\Static100.txt", "C:\\Users\\mdane\\Documents\\SS-TPs\\TP1\\CellIndexMethod\\src\\Dynamic100.txt");

            // Crear una instancia de CIMImpl
            CIMImpl cim = new CIMImpl(M, config.getN(), config.getL(), config.getMaxParticleRadius(), config.getParticleList());

            long finish = System.currentTimeMillis();

            cim.save("./test", 12, true);

            System.out.println("Configuración utilizada: " + config);

            System.out.println("Tiempo de ejecucion:" + (finish-start));


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}