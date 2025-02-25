package lab_3.minesweeper.util;

import java.io.*;
import java.util.*;

public class HighScoresManager {
    private static final String FILE_NAME = "highscores.txt";
    private static final int MAX_SCORES = 5;

    public static void saveHighScore(String playerName, int time) {
        List<ScoreEntry> scores = loadHighScores();
        scores.add(new ScoreEntry(playerName, time));
        scores.sort(Comparator.comparingInt(s -> s.time));

        if (scores.size() > MAX_SCORES) scores = scores.subList(0, MAX_SCORES);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(FILE_NAME))) {
            for (ScoreEntry entry : scores) {
                writer.write(entry.playerName + "," + entry.time);
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error saving high scores: " + e.getMessage());
        }
    }

    public static List<ScoreEntry> loadHighScores() {
        List<ScoreEntry> scores = new ArrayList<>();
        File file = new File(FILE_NAME);

        if (!file.exists()) return scores;

        try (BufferedReader reader = new BufferedReader(new FileReader(FILE_NAME))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length == 2) scores.add(new ScoreEntry(parts[0], Integer.parseInt(parts[1])));
            }
        } catch (IOException e) {
            System.err.println("Error loading high scores: " + e.getMessage());
        }
        return scores;
    }
    public record ScoreEntry(String playerName, int time) {
    }
}