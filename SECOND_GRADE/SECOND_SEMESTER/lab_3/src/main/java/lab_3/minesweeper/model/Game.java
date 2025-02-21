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
        cell.open();

        if (cell.isMine()) gameOver = true;
        else  checkWinCondition();
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