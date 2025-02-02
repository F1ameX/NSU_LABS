package org.lab_1;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class WordData {
    private final Map<String, Integer> wordsMap = new HashMap<>();

    public Map<String, Integer> getWordsMap() {
        return wordsMap;
    }

    public void processFileData(String inputFileName) {
        String filePath = "/Users/andrewf1amex/Programming/oop_java/lab_1/" + inputFileName;

        try (BufferedReader fileReader = new BufferedReader(new FileReader(filePath))) {
            String line;
            Pattern wordPattern = Pattern.compile("\\w+");

            while ((line = fileReader.readLine()) != null) {
                Matcher matcher = wordPattern.matcher(line);

                while (matcher.find()) {
                    String word = matcher.group().toLowerCase();
                    wordsMap.put(word, wordsMap.getOrDefault(word, 0) + 1);
                }
            }
        } catch (IOException e) {
            System.err.println("Ошибка при чтении файла. Проверьте путь и имя файла!");
        }
    }
}