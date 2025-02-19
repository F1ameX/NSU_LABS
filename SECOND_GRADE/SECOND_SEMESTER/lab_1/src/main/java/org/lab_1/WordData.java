package org.lab_1;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

public class WordData {
    private final Map<String, Integer> wordsMap = new HashMap<>();

    public Set<WordFrequency> getWordsSet() {
        int totalWords = wordsMap.values().stream().mapToInt(Integer::intValue).sum();
        return wordsMap.entrySet().stream()
                .map(e -> new WordFrequency(e.getKey(), e.getValue(), (float) e.getValue() / totalWords * 100))
                .collect(Collectors.toSet());
    }

    public void processFileData(String inputFileName) {
        try (BufferedReader fileReader = new BufferedReader(new InputStreamReader(new FileInputStream(inputFileName), StandardCharsets.UTF_8))) {
            String line;
            StringBuilder wordBuilder = new StringBuilder();

            while ((line = fileReader.readLine()) != null) {
                for (char ch : line.toCharArray()) {
                    if (Character.isLetterOrDigit(ch)) {
                        wordBuilder.append(ch);
                    } else if (!wordBuilder.isEmpty()) {
                        String word = wordBuilder.toString().toLowerCase();
                        wordsMap.merge(word, 1, Integer::sum);
                        wordBuilder.setLength(0);
                    }
                }
            }

            if (!wordBuilder.isEmpty()) {
                String word = wordBuilder.toString().toLowerCase();
                wordsMap.merge(word, 1, Integer::sum);
            }
        } catch (IOException e) {
            System.err.println("Unable to read from file: " + e.getLocalizedMessage());
        }
    }
}
