package lab_3.minesweeper.app;

import lab_3.minesweeper.model.Game;
import lab_3.minesweeper.model.GameBoard;
import lab_3.minesweeper.model.Cell;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Game game = new Game(9, 9, 10);

        while (!game.isGameOver()) {
            printBoard(game.getGameBoard());
            System.out.print("Choose action (o x y - open cell, f x y - set flag): ");
            String command = scanner.next();
            int row = scanner.nextInt();
            int col = scanner.nextInt();

            if (command.equals("o")) game.openCell(row, col);
            else if (command.equals("f")) game.toggleFlag(row, col);
        }

        printBoard(game.getGameBoard());
        System.out.println(game.isGameWon() ? "You won!" : "You lost!!");
    }

    private static void printBoard(GameBoard board) {
        for (int i = 0; i < board.getRows(); i++) {
            for (int j = 0; j < board.getCols(); j++) {
                Cell cell = board.getCell(i, j);
                if (cell.isOpen()) {
                    if (cell.isMine()) System.out.print(" * ");
                    else System.out.print(" " + cell.getSurroundingMines() + " ");
                }
                else if (cell.isFlagged()) System.out.print(" F ");
                else System.out.print(" . ");
            }
            System.out.println();
        }
    }
}