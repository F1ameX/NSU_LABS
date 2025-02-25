package lab_3.minesweeper.view.text;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.model.Cell;
import lab_3.minesweeper.model.GameBoard;

import java.util.Scanner;

public class TextView {
    private final GameController controller;
    private final Scanner scanner;

    public TextView(GameController controller) {
        this.controller = controller;
        this.scanner = new Scanner(System.in);
    }

    public void start() {
        while (!controller.isGameOver()) {
            printBoard();
            System.out.print("Enter command (o x y - open, f x y - flag, q - quit): ");

            String command = scanner.next();

            if (command.equals("q")) {
                System.out.println("Game exited.");
                return;
            }

            if (!command.equals("o") && !command.equals("f")) {
                System.out.println("Error: Unknown command! Use 'o' (open), 'f' (flag), or 'q' (quit).");
                scanner.nextLine();
                continue;
            }

            if (!scanner.hasNextInt()) {
                System.out.println("Error: Invalid input! Expected two numbers for coordinates.");
                scanner.nextLine();
                continue;
            }
            int row = scanner.nextInt();

            if (!scanner.hasNextInt()) {
                System.out.println("Error: Invalid input! Expected two numbers for coordinates.");
                scanner.nextLine();
                continue;
            }
            int col = scanner.nextInt();

            if (row < 0 || row >= controller.getGameBoard().getRows() ||
                    col < 0 || col >= controller.getGameBoard().getCols()) {
                System.out.println("Error: Coordinates are out of bounds! Try again.");
                continue;
            }


            if (command.equals("o")) controller.openCell(row, col);
            else controller.toggleFlag(row, col);
        }

        printBoard();
        System.out.println(controller.isGameWon() ? "Congratulations, you won!" : "Game over, you lost!");
    }

    private void printBoard() {
        GameBoard board = controller.getGameBoard();
        System.out.println("  Y: 0 1 2 3 4 5 6 7 8");
        System.out.println("X:");
        for (int i = 0; i < board.getRows(); i++) {
            System.out.print(i + "  ");
            for (int j = 0; j < board.getCols(); j++) {
                Cell cell = board.getCell(i, j);

                if (cell.isOpen()) {
                    if (cell.isMine()) System.out.print("* ");
                    else System.out.print(cell.getSurroundingMines() + " ");
                }
                else if (cell.isFlagged()) System.out.print("F ");
                else System.out.print(". ");
            }
            System.out.println();
        }
    }
}