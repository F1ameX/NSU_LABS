package lab_3.minesweeper.model;

public class Game {
    private final GameBoard gameBoard;
    private boolean gameOver;
    private boolean gameWon;

    public Game(int rows, int cols, int mines) {
        this.gameBoard = new GameBoard(rows, cols, mines);
        this.gameOver = false;
        this.gameWon = false;
    }

    public void openCell(int row, int col) {
        if (gameOver) return;
        Cell cell = gameBoard.getCell(row, col);
        if (cell.isOpen() || cell.isFlagged()) return;
        if (cell.isMine()) {
            gameOver = true;
            return;
        }
        floodFill(row, col);
        checkWinCondition();
    }

    private void floodFill(int row, int col) {
        if (row < 0 || row >= gameBoard.getRows() || col < 0 || col >= gameBoard.getCols()) return;
        Cell cell = gameBoard.getCell(row, col);
        if (cell.isOpen() || cell.isMine() || cell.isFlagged()) return;
        cell.open();
        if (cell.getSurroundingMines() == 0) { // Continue opening adjacent cells if no mines around
            for (int dr = -1; dr <= 1; dr++) {
                for (int dc = -1; dc <= 1; dc++) {
                    if (dr != 0 || dc != 0)  floodFill(row + dr, col + dc);
                }
            }
        }
    }

    public void toggleFlag(int row, int col) {
        if (gameOver) return;
        Cell cell = gameBoard.getCell(row, col);
        if (!cell.isOpen()) {
            if (cell.isFlagged()) cell.unflag();
            else cell.flag();
        }
    }

    private void checkWinCondition() {
        for (int i = 0; i < gameBoard.getRows(); i++) {
            for (int j = 0; j < gameBoard.getCols(); j++) {
                Cell cell = gameBoard.getCell(i, j);
                if (!cell.isMine() && !cell.isOpen()) return;
            }
        }
        gameWon = true;
        gameOver = true;
    }

    public boolean isGameOver() { return gameOver; }
    public boolean isGameWon() { return gameWon; }
    public GameBoard getGameBoard() { return gameBoard; }
}