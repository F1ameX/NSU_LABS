package org.lab_1;

public class Main {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Использование: java Main input.txt output.csv");
            return;
        }

        String inputFileName = args[0];
        String outputFileName = args[1];

        WordData wordData = new WordData();
        wordData.processFileData(inputFileName);

        CSVWriter.writeToFile(outputFileName, wordData.getWordsSet());
    }
}