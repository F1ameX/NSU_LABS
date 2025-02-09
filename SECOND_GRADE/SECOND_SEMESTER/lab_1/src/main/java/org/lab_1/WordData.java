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
        try (Reader reader = new InputStreamReader(new FileInputStream(inputFileName), StandardCharsets.UTF_8);
             BufferedReader fileReader = new BufferedReader(reader)) {

            String line;
            StringBuilder wordBuilder = new StringBuilder();

            while ((line = fileReader.readLine()) != null) {
                for (char ch : line.toCharArray()) {
                    if (Character.isLetterOrDigit(ch)) {
                        wordBuilder.append(ch);
                    } else if (!wordBuilder.isEmpty()) {
                        String word = wordBuilder.toString().toLowerCase();
                        wordsMap.put(word, wordsMap.getOrDefault(word, 0) + 1);
                        wordBuilder.setLength(0);
                    }
                }
            }

            if (!wordBuilder.isEmpty()) {
                String word = wordBuilder.toString().toLowerCase();
                wordsMap.put(word, wordsMap.getOrDefault(word, 0) + 1);
            }

        } catch (IOException e) {
            System.err.println("Ошибка при чтении файла: " + e.getLocalizedMessage());
        }
    }
}