package lab_2.calculator.app;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.factory.CommandFactory;
import lab_2.calculator.commands.Command;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;
import java.io.*;
import java.util.List;

public class Calculator {
    private static final Logger logger = CalculatorLogger.getLogger();
    private ExecutionContext context;
    private CommandFactory factory;

    public Calculator() {
        this.context = new ExecutionContext();
        this.factory = new CommandFactory();
    }

    public void start(BufferedReader reader) {
        String line;
        try {
            while ((line = reader.readLine()) != null) {
                processCommand(line);
            }
        } catch (IOException e) {
            logger.error("Error reading input: {}", e.getMessage());
        }
    }

    private void processCommand(String line) {
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