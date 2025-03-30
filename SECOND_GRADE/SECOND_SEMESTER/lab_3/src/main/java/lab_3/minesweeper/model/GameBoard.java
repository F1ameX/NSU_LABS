package lab_3.minesweeper.model;
import lab_3.minesweeper.controller.CellState;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

public class GameBoard {
    private final int rows;
    private final int cols;
    private final int totalMines;
    private final Cell[][] board;

    public GameBoard(int rows, int cols, int totalMines) {
        this.rows = rows;
        this.cols = cols;
        this.totalMines = totalMines;
        this.board = new Cell[rows][cols];
        initializeBoard();
    }

    private void initializeBoard() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) board[i][j] = new Cell();
        }
    }

    public void placeMines(int firstRow, int firstCol) {
        Random random = new Random();
        Set<String> placedMines = new HashSet<>();

        while (placedMines.size() < totalMines) {
            int row = random.nextInt(rows);
            int col = random.nextInt(cols);
            String position = row + "," + col;

            if (!position.equals(firstRow + "," + firstCol) && !placedMines.contains(position)) {
                board[row][col].setMine(true);
                placedMines.add(position);
            }
        }
    }

    public void calculateSurroundingMines() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (board[i][j].isMine()) continue;
                int mineCount = 0;
                for (int rowOffset = -1; rowOffset <= 1; rowOffset++) {
                    for (int colOffset = -1; colOffset <= 1; colOffset++) {
                        int newRow = i + rowOffset;
                        int newCol = j + colOffset;
                        if (newRow >= 0 && newRow < rows && newCol >= 0 && newCol < cols) {
                            if (board[newRow][newCol].isMine()) mineCount++;
                        }
                    }
                }
                board[i][j].setSurroundingMines(mineCount);
            }
        }
    }

    public CellState getCellState(int row, int col, boolean isOver) {
        Cell cell = getCell(row, col);
        if (cell.isOpen()) {
            return cell.isMine() ? CellState.MINE : CellState.OPEN;
        }
        if (cell.isFlagged()) {
            return CellState.FLAGGED;
        }
        if (!cell.isOpen() && cell.isMine()) return CellState.MINE;
        return CellState.CLOSED;
    }

    public Cell getCell(int row, int col) {
        if (row < 0 || row >= rows || col < 0 || col >= cols)
            throw new IllegalArgumentException("Coordinates (" + row + ", " + col + ") are out of bounds!");
        return board[row][col];
    }

    public int getRows() { return rows; }
    public int getCols() { return cols; }
    public int getTotalMines() { return totalMines; }
}