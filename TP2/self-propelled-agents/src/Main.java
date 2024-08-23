import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        int M = 300;
        int N = 300;
        int L = 600;
        Map<Integer, List<Particle>> particlesPerTime;
        OffLattice offLattice = new OffLattice(M,N,L);
        particlesPerTime = offLattice.run(10);
        System.out.println();
    }
}