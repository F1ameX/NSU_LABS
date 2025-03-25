package lab_3.minesweeper.controller;
import lab_3.minesweeper.model.Game;
import lab_3.minesweeper.model.GameBoard;
import lab_3.minesweeper.model.Cell;

public class GameController {
    private Game game;
    private boolean gameOver;

    public GameController(int rows, int cols, int mines) {
        this.game = new Game(rows, cols, mines);
        this.gameOver = false;
    }

    public CellState getCellState(int row, int col) {
        Cell cell = game.getGameBoard().getCell(row, col);
        if (cell.isOpen()) return cell.isMine() ? CellState.CLOSED : CellState.OPEN;
        if (cell.isFlagged()) return CellState.FLAGGED;
        return CellState.CLOSED;
    }

    public void openCell(int row, int col) {
        if (gameOver) return;
        game.openCell(row, col);
        if (game.isGameOver()) gameOver = true;
    }

    public void toggleFlag(int row, int col) {
        if (gameOver) return;
        game.toggleFlag(row, col);
    }

    public void resetGame(int rows, int cols, int mines) {this.game = new Game(rows, cols, mines); }

    public GameBoard getGameBoard() {return game.getGameBoard(); }
    public boolean isGameOver() {return gameOver; }
    public boolean isGameWon() {return game.isGameWon(); }
    public int getMineCount() {return game.getGameBoard().getTotalMines(); }
}