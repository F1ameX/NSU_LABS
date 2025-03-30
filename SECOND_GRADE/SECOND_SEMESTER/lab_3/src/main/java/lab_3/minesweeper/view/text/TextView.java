package lab_3.minesweeper.view.text;
import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.controller.CellState;
import java.util.Scanner;

public class TextView {
    private final GameController controller;

    public TextView(GameController controller) {
        this.controller = controller;
    }

    public void start() {
        Scanner scanner = new Scanner(System.in);

        while (!controller.isGameOver()) {
            printBoard();

            System.out.print("Choose action (o x y - open, f x y - flag): ");
            String input = scanner.nextLine();
            String[] parts = input.split(" ");

            if (parts.length == 3) {
                try {
                    int row = Integer.parseInt(parts[1]);
                    int col = Integer.parseInt(parts[2]);

                    if (parts[0].equals("o")) {
                        controller.openCell(row, col);
                    } else if (parts[0].equals("f")) {
                        controller.toggleFlag(row, col);
                    }

                    if (controller.isGameOver()) showGameOver();

                } catch (NumberFormatException e) {
                    System.out.println("Invalid input. Please try again.");
                }
            }
        }
    }

    private void printBoard() {
        System.out.print("  ");
        for (int col = 0; col < controller.getGameBoard().getCols(); col++) System.out.print(col + " ");
        System.out.println();

        for (int row = 0; row < controller.getGameBoard().getRows(); row++) {
            System.out.print(row + " ");
            for (int col = 0; col < controller.getGameBoard().getCols(); col++) {
                CellState state = controller.getCellState(row, col);

                switch (state) {
                    case OPEN:
                        int surroundingMines = controller.getSurroundingMines(row, col);
                        if (surroundingMines > 0) {
                            System.out.print(surroundingMines + " ");
                        } else {
                            System.out.print("  ");
                        }
                        break;
                    case FLAGGED:
                        System.out.print("F ");
                        break;
                    case CLOSED:
                        System.out.print("# ");
                        break;
                    case MINE:
                        System.out.print("M ");
                        break;
                }
            }
            System.out.println();
        }
    }

    private void showGameOver() {
        if (controller.isGameWon()) {
            System.out.println("Congratulations! You won the game!");
        } else {
            System.out.println("Game Over! You hit a mine!");
        }

        System.out.println("Would you like to play again? (y/n): ");
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        if (input.equalsIgnoreCase("y")) {
            restartGame();
        }
    }

    private void restartGame() {
        int rows = controller.getGameBoard().getRows();
        int cols = controller.getGameBoard().getCols();
        int mines = controller.getMineCount();
        controller.resetGame(rows, cols, mines);
        start();
    }
}