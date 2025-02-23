package lab_3.minesweeper.view.graphical;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.model.Cell;
import lab_3.minesweeper.model.GameBoard;
import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Objects;

public class GraphicalView extends JFrame {
    private final GameController controller;
    private final JButton[][] buttons;
    private final int rows;
    private final int cols;

    private final ImageIcon closedIcon = loadIcon("cell_closed.png");
    private final ImageIcon openIcon = loadIcon("cell_open.png");
    private final ImageIcon flagIcon = loadIcon("cell_flag.png");
    private final ImageIcon mineIcon = loadIcon("cell_mine.png");
    private final ImageIcon[] numberIcons = new ImageIcon[9];

    public GraphicalView(GameController controller) {
        this.controller = controller;
        this.rows = controller.getGameBoard().getRows();
        this.cols = controller.getGameBoard().getCols();
        this.buttons = new JButton[rows][cols];

        loadNumberIcons();

        setTitle("Minesweeper");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new GridLayout(rows, cols));
        setResizable(false);

        initializeBoard();
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    private ImageIcon loadIcon(String fileName) {
        return new ImageIcon(Objects.requireNonNull(getClass().getClassLoader().getResource("images/" + fileName)));
    }

    private void loadNumberIcons() {
        for (int i = 1; i <= 8; i++)
            numberIcons[i] = loadIcon("number_" + i + ".png");
    }

    private void initializeBoard() {
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                JButton button = new JButton();
                button.setIcon(closedIcon);
                button.setBorder(BorderFactory.createLineBorder(Color.DARK_GRAY));

                final int r = row, c = col;
                button.addMouseListener(new MouseAdapter() {
                    @Override
                    public void mousePressed(MouseEvent e) {
                        if (SwingUtilities.isLeftMouseButton(e)) controller.openCell(r, c);
                        else if (SwingUtilities.isRightMouseButton(e)) controller.toggleFlag(r, c);
                        updateBoard();
                    }
                });

                buttons[row][col] = button;
                add(button);
            }
        }
    }

    private void updateBoard() {
        GameBoard board = controller.getGameBoard();

        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                Cell cell = board.getCell(row, col);
                JButton button = buttons[row][col];

                if (cell.isOpen()) {
                    if (cell.isMine()) button.setIcon(mineIcon);
                    else if (cell.getSurroundingMines() > 0) button.setIcon(numberIcons[cell.getSurroundingMines()]);
                    else button.setIcon(openIcon);
                }
                else if (cell.isFlagged()) button.setIcon(flagIcon);
                else button.setIcon(closedIcon);

            }
        }

        if (controller.isGameOver()) showGameOver();
    }

    private void showGameOver() {
        int result = JOptionPane.showConfirmDialog(this,
                controller.isGameWon() ? "Congratulations, you won! Play again?" :
                        "Game Over! You lost. Play again?",
                "Game Over", JOptionPane.YES_NO_OPTION);

        if (result == JOptionPane.YES_OPTION) restartGame();
        else dispose();
    }

    private void restartGame() {
        dispose();
        new GraphicalView(new GameController(rows, cols, 10));
    }
}