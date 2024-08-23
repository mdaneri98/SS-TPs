import java.util.*;

public class OffLattice {

    private Map<Integer, List<Particle>> particlesPerTime = new HashMap<>();

    private static double VELOCITY = 10;

    private int M; //Dimension de la matriz

    private int N; //Cantidad de particulas
    private int L; //Longitud de la matriz
    private List<Particle> particlesList;

    public OffLattice(int m, int n, int l) {
        M = m;
        N = n;
        L = l;
        this.particlesList = new ArrayList<>();
    }

    private void generateRandomParticles() {
        Random random = new Random();

        for (int i = 0; i < N; i++) {
            // Posición x aleatoria dentro del área L x L
            double x = random.nextDouble() * L;
            double y = random.nextDouble() * L;
            double radius = 0;
            double angle = random.nextDouble() * Math.PI * 2;
            this.particlesList.add(new Particle(i, x, y, radius,VELOCITY,angle));
        }
        particlesPerTime.putIfAbsent(0,particlesList);
    }

    public double calculateAngle(Particle p,List<Particle> neighbours){

        double sinSum = 0;
        double cosSum = 0;

        for ( Particle particle :neighbours) {
            sinSum += Math.sin(particle.getAngle());
            cosSum += Math.cos(particle.getAngle());
        }

        double avgSin = sinSum/neighbours.size();
        double avgCos = cosSum/neighbours.size();

        return Math.atan2(avgSin,avgCos);
    }

    public Map<Integer,List<Particle>> run(int maxTime) throws Exception {
        int time = 0;

        generateRandomParticles();
        time++;
        for (; time < maxTime ; time++) {
            CIMImpl cim = new CIMImpl(M,N,L,0,particlesList);
            Map<Integer,List<Particle>> neighboursByParticle = cim.findInteractions(1,false);
            List<Particle> newParticles = new ArrayList<>();
            for (Particle p : this.particlesList){
                List<Particle> neighbours = neighboursByParticle.getOrDefault(p.getId(),new ArrayList<>());
                neighbours.add(p);
               double newAngle = calculateAngle(p,neighbours);

              Pair<Double,Double> position = calculatePosition(p,newAngle);
              newParticles.add(new Particle(p.getId(), position.first, position.second, 0,VELOCITY,newAngle));
            }
            particlesPerTime.putIfAbsent(time,newParticles);
        }
        return particlesPerTime;
    }

    private Pair<Double,Double> calculatePosition(Particle p , double newAngle){
        double dt = 1;
        double vx = VELOCITY * Math.cos(newAngle);
        double vy = VELOCITY * Math.sin(newAngle);

        double newX = p.getPosX() + vx * dt;
        double newY = p.getPosY() + vy * dt;

        return new Pair<>(newX,newY);
    }

    class Pair<U,T> {
        private U first;
        private T second;

        public Pair(U first, T second){
            this.first = first;
            this.second = second;
        }

        public U getFirst() {
            return first;
        }

        public T getSecond() {
            return second;
        }
    }


}
