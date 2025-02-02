package org.lab_1;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class CSVWriter {
    public static void writeToFile(String outputFileName, Map<String, Integer> wordsMap) {
        String filePath = "/Users/andrewf1amex/Programming/oop_java/lab_1/" + outputFileName;
        try (BufferedWriter fileWriter = new BufferedWriter(new FileWriter(filePath))) {
            List<WordFrequency> wordsFrequency = new ArrayList<>();

            for (Map.Entry<String, Integer> entry : wordsMap.entrySet()) {
                String word = entry.getKey();
                int count = entry.getValue();
                float percent = (float) count / wordsMap.size() * 100;
                wordsFrequency.add(new WordFrequency(word, count, percent));
            }

            wordsFrequency.sort((a, b) -> Float.compare(b.frequencyPercent(), a.frequencyPercent()));
            fileWriter.write("Слово,Частота,Частота(%)\n");

            for (WordFrequency wf : wordsFrequency) {
                fileWriter.write(wf.word() + "," + wf.count() + "," + String.format("%.2f", wf.frequencyPercent()) + "\n");
            }
        } catch (IOException e) {
            System.err.println("Ошибка при записи файла. Проверьте путь и имя файла!");
        }
    }
}

record WordFrequency(String word, int count, float frequencyPercent) {}