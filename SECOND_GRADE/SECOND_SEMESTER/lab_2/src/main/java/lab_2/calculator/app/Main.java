package lab_2.calculator.app;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.factory.CommandFactory;
import lab_2.calculator.commands.Command;

import java.io.*;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        ExecutionContext context = new ExecutionContext();
        CommandFactory factory = new CommandFactory();

        BufferedReader reader;
        if (args.length > 0) {
            try {
                reader = new BufferedReader(new FileReader(args[0]));
            } catch (FileNotFoundException e) {
                System.err.println("Error: File not found - " + args[0]);
                return;
            }
        } else {
            reader = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Enter commands (CTRL+D to stop):");
        }

        try {
            String line;
            while ((line = reader.readLine()) != null) {
                processCommand(line, factory, context);
            }
        } catch (IOException e) {
            System.err.println("Error reading input: " + e.getMessage());
        }
    }

    private static void processCommand(String line, CommandFactory factory, ExecutionContext context) {
        line = line.trim();
        if (line.isEmpty() || line.startsWith("#")) {
            return; // Ignore empty lines and comments
        }

        String[] parts = line.split("\\s+");
        String commandName = parts[0];
        List<String> args = List.of(parts).subList(1, parts.length);

        try {
            Command command = factory.createCommand(commandName);
            command.execute(context, args);
        } catch (Exception e) {
            System.err.println("Error executing command: " + line + " | " + e.getMessage());
        }
    }
}