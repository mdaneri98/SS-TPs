//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.

import models.*;
import models.walls.Wall;
import models.walls.WallType;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main {


    public static void main(String[] args) {
        double L = 0.1;
        double staticRadius = 0.005;
        int N = 100;
        double radius = 0.001;
        double velocity = 1;
        double mass = 1;
        double staticMass = 1;
        double dt = 0.01;

        MolecularDynamicSystem molecularDynamic = new MolecularDynamicSystem(N, L, velocity, mass, radius, staticRadius, staticMass, dt);
        molecularDynamic.fixedSolution(5);

    }

}