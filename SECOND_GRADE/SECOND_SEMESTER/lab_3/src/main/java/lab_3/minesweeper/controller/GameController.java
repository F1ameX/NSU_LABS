package lab_3.minesweeper.controller;

import lab_3.minesweeper.model.Game;
import lab_3.minesweeper.model.GameBoard;

public class GameController {
    private final Game game;

    public GameController(int rows, int cols, int mines) { this.game = new Game(rows, cols, mines); }

    public boolean isGameOver() { return game.isGameOver(); }
    public boolean isGameWon() { return game.isGameWon(); }
    public GameBoard getGameBoard() { return game.getGameBoard();}

    public void openCell(int row, int col) {
        if (!game.isGameOver()) game.openCell(row, col);
    }

    public void toggleFlag(int row, int col) {
        if (!game.isGameOver()) game.toggleFlag(row, col);
    }
}