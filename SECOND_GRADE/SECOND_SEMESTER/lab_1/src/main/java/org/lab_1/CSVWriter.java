package org.lab_1;
import java.io.*;
import java.util.*;


public class CSVWriter {
    public static void writeToFile(String outputFileName, Set<WordFrequency> wordsSet) {
        List<WordFrequency> sortedWords = wordsSet.stream()
                .sorted(Comparator.comparing(WordFrequency::frequencyPercent).reversed())
                .toList();

        try (BufferedWriter fileWriter = new BufferedWriter(new FileWriter(outputFileName))) {
            fileWriter.write("Слово,Частота,Частота(%)\n");
            for (WordFrequency wf : sortedWords) {
                fileWriter.write(wf.word() + "," + wf.count() + "," + String.format("%.2f", wf.frequencyPercent()) + "\n");
            }
        } catch (IOException e) {
            System.err.println("Ошибка при записи файла: " + e.getLocalizedMessage());
        }
    }
}