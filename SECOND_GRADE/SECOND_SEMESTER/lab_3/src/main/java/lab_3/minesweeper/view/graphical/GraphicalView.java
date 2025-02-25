package lab_3.minesweeper.view.graphical;

import lab_3.minesweeper.controller.GameController;
import lab_3.minesweeper.model.Cell;
import lab_3.minesweeper.model.GameBoard;
import lab_3.minesweeper.util.HighScoresManager;
import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Objects;
import java.util.List;

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

    private final JLabel timerLabel;
    private Timer gameTimer;
    private int elapsedTime;

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

        timerLabel = new JLabel("Time: 0s", SwingConstants.CENTER);
        timerLabel.setFont(new Font("Arial", Font.BOLD, 16));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 4;
        add(timerLabel, gbc);

        JPanel boardPanel = createBoardPanel();
        gbc.gridx = 0;
        gbc.gridy = 1;
        gbc.gridwidth = 4;
        add(boardPanel, gbc);

        JPanel buttonPanel = getJPanel();

        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 4;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        add(buttonPanel, gbc);

        startTimer();

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    private JPanel getJPanel() {
        JPanel buttonPanel = new JPanel(new GridLayout(1, 4, 5, 5));

        JButton newGameButton = new JButton("New Game");
        newGameButton.addActionListener(e -> restartGame());
        buttonPanel.add(newGameButton);

        JButton highScoresButton = new JButton("High Scores");
        highScoresButton.addActionListener(e -> showHighScores());
        buttonPanel.add(highScoresButton);

        JButton aboutButton = new JButton("About");
        aboutButton.addActionListener(e -> showAbout());
        buttonPanel.add(aboutButton);

        JButton exitButton = new JButton("Exit");
        exitButton.addActionListener(e -> System.exit(0));
        buttonPanel.add(exitButton);
        return buttonPanel;
    }

    private JPanel createBoardPanel() {
        JPanel panel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.NONE;
        gbc.insets = new Insets(0, 0, 0, 0);

        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                JButton button = getJButton(row, col);

                buttons[row][col] = button;

                gbc.gridx = col;
                gbc.gridy = row;
                panel.add(button, gbc);
            }
        }
        return panel;
    }

    private JButton getJButton(int row, int col) {
        JButton button = new JButton();

        button.setPreferredSize(new Dimension(32, 32));
        button.setMinimumSize(new Dimension(32, 32));
        button.setMaximumSize(new Dimension(32, 32));
        button.setIcon(closedIcon);

        final int r = row, c = col;
        button.addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                if (SwingUtilities.isLeftMouseButton(e)) controller.openCell(r, c);
                else if (SwingUtilities.isRightMouseButton(e)) controller.toggleFlag(r, c);
                updateBoard();
            }
        });
        return button;
    }

    private void startTimer() {
        elapsedTime = 0;
        gameTimer = new Timer(1000, e -> {
            elapsedTime++;
            timerLabel.setText("Time: " + elapsedTime + "s");
        });
        gameTimer.start();
    }

    private void stopTimer() {
        if (gameTimer != null) gameTimer.stop();
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

        if (controller.isGameOver()) {
            stopTimer();
            revealAllMines();
        }
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
        stopTimer();

        if (controller.isGameWon()) {
            String playerName = JOptionPane.showInputDialog(this,
                    "Congratulations! You won in " + elapsedTime + " seconds!\nEnter your name for the leaderboard:");
            if (playerName != null && !playerName.trim().isEmpty()) HighScoresManager.saveHighScore(playerName.trim(), elapsedTime);
        }

        int result = JOptionPane.showConfirmDialog(this,
                controller.isGameWon() ? "Play again?" : "Game Over! Play again?",
                "Game Over", JOptionPane.YES_NO_OPTION);

        if (result == JOptionPane.YES_OPTION) restartGame();
        else dispose();
    }

    private void restartGame() {
        dispose();
        new GraphicalView(new GameController(rows, cols, 10));
    }

    private void showHighScores() {
        List<HighScoresManager.ScoreEntry> scores = HighScoresManager.loadHighScores();

        if (scores.isEmpty()) {
            JOptionPane.showMessageDialog(this, "No high scores yet!", "High Scores", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        StringBuilder scoreText = new StringBuilder("<html><h2>High Scores</h2><br>");
        int rank = 1;
        for (HighScoresManager.ScoreEntry entry : scores) {
            scoreText.append(rank++).append(". ").append(entry.playerName()).append(" - ")
                    .append(entry.time()).append("s<br>");
        }
        scoreText.append("</html>");

        JOptionPane.showMessageDialog(this, scoreText.toString(), "High Scores", JOptionPane.INFORMATION_MESSAGE);
    }

    private void showAbout() {
        String aboutText = """
        <html>
        <h2>Minesweeper</h2>
        <p><b>Objective:</b> Uncover all safe cells without triggering a mine.</p>
        <p><b>Controls:</b></p>
        <ul>
            <li><b>Left Click</b> - Open a cell</li>
            <li><b>Right Click</b> - Place/Remove a flag</li>
        </ul>
        <p><b>Rules:</b></p>
        <ul>
            <li>The number in a cell shows how many mines are in the surrounding 8 cells.</li>
            <li>If you click on a mine, the game is over.</li>
            <li>If an empty cell is clicked, all adjacent empty cells will open automatically.</li>
            <li>To win, all non-mine cells must be revealed.</li>
        </ul>
        <p><i>Good luck and have fun!</i></p>
        </html>
        """;
        JOptionPane.showMessageDialog(this, aboutText, "About Minesweeper", JOptionPane.INFORMATION_MESSAGE);
    }

    private ImageIcon loadIcon(String fileName) {
        return new ImageIcon(Objects.requireNonNull(getClass().getClassLoader().getResource("images/" + fileName)));
    }

    private void loadNumberIcons() {
        for (int i = 1; i <= 8; i++)
            numberIcons[i] = loadIcon("number_" + i + ".png");
    }
}