package lab_3.minesweeper.app;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.view.text.TextView;

public class Main {
    public static void main(String[] args) {
        GameController controller = new GameController(9, 9, 10);
        TextView textView = new TextView(controller);
        textView.start();
    }
}