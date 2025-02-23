package lab_3.minesweeper.app;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.view.graphical.GraphicalView;

public class Main {
    public static void main(String[] args) {
        new GraphicalView(new GameController(15, 15, 25));
    }
}