package lab_3.minesweeper.app;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.view.graphical.GraphicalView;
import lab_3.minesweeper.view.text.TextView;

public class Main {
    public static void main(String[] args) {
        int width = 10, height = 10, mines = 10;
        boolean useTextMode = false;

        for (int i = 0; i < args.length; i++) {
            switch (args[i].toLowerCase()) {
                case "--text":
                    useTextMode = true;
                    break;
                case "--size":
                    if (i + 1 < args.length) {
                        String[] dimensions = args[i + 1].split("x");
                        if (dimensions.length == 2) {
                            try {
                                width = Math.max(5, Integer.parseInt(dimensions[0]));
                                height = Math.max(5, Integer.parseInt(dimensions[1]));
                            } catch (NumberFormatException e) {
                                System.out.println("⚠ Invalid size format! Using default 9x9.");
                            }
                        }
                        i++;
                    }
                    break;
                case "--mines":
                    if (i + 1 < args.length) {
                        try {
                            mines = Math.max(1, Integer.parseInt(args[i + 1]));
                        } catch (NumberFormatException e) {
                            System.out.println("⚠ Invalid mines count! Using default 10.");
                        }
                        i++;
                    }
                    break;
            }
        }
        System.out.printf("Starting Minesweeper (%dx%d, %d mines) in %s mode...%n",
                width, height, mines, useTextMode ? "TEXT" : "GRAPHICAL");

        GameController controller = new GameController(width, height, mines);

        if (useTextMode) new TextView(controller).start();
        else new GraphicalView(controller);
    }
}