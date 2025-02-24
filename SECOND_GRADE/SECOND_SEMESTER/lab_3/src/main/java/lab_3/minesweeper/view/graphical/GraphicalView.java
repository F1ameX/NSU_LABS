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
        setLayout(new GridBagLayout());
        setResizable(false);

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.BOTH;
        gbc.insets = new Insets(5, 5, 5, 5);

        JPanel boardPanel = createBoardPanel();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        add(boardPanel, gbc);

        JButton newGameButton = new JButton("New Game");
        newGameButton.addActionListener(e -> restartGame());
        gbc.gridx = 0;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        add(newGameButton, gbc);

        JButton exitButton = new JButton("Exit");
        exitButton.addActionListener(e -> System.exit(0));
        gbc.gridx = 1;
        gbc.gridy = 1;
        add(exitButton, gbc);

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    private JPanel createBoardPanel() {
        JPanel panel = new JPanel(new GridLayout(rows, cols));
        GameBoard board = controller.getGameBoard();

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
                panel.add(button);
            }
        }
        return panel;
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
        if (controller.isGameOver()) revealAllMines();
    }

    private void revealAllMines() {
        GameBoard board = controller.getGameBoard();
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                Cell cell = board.getCell(row, col);
                if (cell.isMine()) buttons[row][col].setIcon(mineIcon);
            }
        }
        this.revalidate();
        this.repaint();
        Toolkit.getDefaultToolkit().sync();
        SwingUtilities.invokeLater(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException ignored) {}

            showGameOver();
        });
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

    private ImageIcon loadIcon(String fileName) {
        return new ImageIcon(Objects.requireNonNull(getClass().getClassLoader().getResource("images/" + fileName)));
    }

    private void loadNumberIcons() {
        for (int i = 1; i <= 8; i++) numberIcons[i] = loadIcon("number_" + i + ".png");
    }
}