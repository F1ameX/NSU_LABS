package lab_3.minesweeper.model;

public class Cell {
    private boolean isMine;
    private boolean isOpen;
    private boolean isFlagged;
    private int surroundingMines;

    public Cell() {
        this.isMine = false;
        this.isOpen = false;
        this.isFlagged = false;
        this.surroundingMines = 0;
    }

    public boolean isMine() { return isMine; }
    public boolean isOpen() { return isOpen; }
    public boolean isFlagged() { return isFlagged; }
    public int getSurroundingMines() { return surroundingMines; }

    public void setMine(boolean isMine) { this.isMine = isMine; }
    public void open() { this.isOpen = true; }
    public void flag() { this.isFlagged = true; }
    public void unflag() {this.isFlagged = false; }
    public void setSurroundingMines(int surroundingMines) { this.surroundingMines = surroundingMines; }
}