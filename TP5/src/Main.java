import models.Field;
import models.Position;

public class Main {

	public static void main(String args[]) {
		
		double blueVelocityMax = 3.8;
		double redVelocityMax = 1;
		
		double blueTau = 0.3;
		double redTau = 0.5;
		
		double rMin = 0.5;
		double rMax = 1.5;
		
		int N = 15;
		
		Field field = new Field(100, 70, new Position(0, 70/2.0));
		
		TryMaradoniano tm = new TryMaradoniano(N, field, blueVelocityMax, redVelocityMax, blueTau, redTau, rMin, rMax);
		
		tm.run();
		
		
	}
	
}
