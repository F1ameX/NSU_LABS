package lab_2.calculator.app;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.factory.CommandFactory;
import lab_2.calculator.commands.Command;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;
import java.io.*;
import java.util.List;

public class Main {
    private static final Logger logger = CalculatorLogger.getLogger();

    public static void main(String[] args) {
        logger.info("Starting calculator...");

        ExecutionContext context = new ExecutionContext();
        CommandFactory factory = new CommandFactory();

        BufferedReader reader;
        if (args.length > 0) {
            try {
                reader = new BufferedReader(new FileReader(args[0]));
                logger.info("Reading commands from file: {}", args[0]);
            } catch (FileNotFoundException e) {
                logger.error("Error: File not found - {}", args[0]);
                return;
            }
        } else {
            reader = new BufferedReader(new InputStreamReader(System.in));
            logger.info("Reading commands from standard input...");
        }

        try {
            String line;
            while ((line = reader.readLine()) != null) { processCommand(line, factory, context); }
        } catch (IOException e) {
            logger.error("Error reading input: {}", e.getMessage());
        }
    }

    private static void processCommand(String line, CommandFactory factory, ExecutionContext context) {
        line = line.trim();
        if (line.isEmpty() || line.startsWith("#")) { return; }

        String[] parts = line.split("\\s+");
        String commandName = parts[0];
        List<String> args = List.of(parts).subList(1, parts.length);

        try {
            Command command = factory.createCommand(commandName);
            command.execute(context, args);
            logger.info("Executed command: {}", commandName);
        } catch (Exception e) {
            logger.error("Error executing command: {} | {}", commandName, e.getMessage());
        }
    }
}