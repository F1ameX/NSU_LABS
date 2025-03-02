package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import org.apache.logging.log4j.Logger;
import lab_2.calculator.logger.CalculatorLogger;
import java.util.List;
import java.util.regex.Pattern;

public class DefineCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();
    private static final Pattern VALID_VARIABLE_PATTERN = Pattern.compile("^[a-zA-Z_][a-zA-Z0-9_]*$");

    @Override
    public void execute(ExecutionContext context, List<String> args) throws InvalidArgumentException {
        if (args.size() != 2) {
            logger.error("DEFINE operation failed: Incorrect number of arguments.");
            throw new InvalidArgumentException("DEFINE command requires exactly two arguments: a variable name and a numeric value.");
        }

        String variableName = args.get(0);
        String valueString = args.get(1);

        if (!VALID_VARIABLE_PATTERN.matcher(variableName).matches()) {
            logger.error("DEFINE operation failed: Invalid variable name '{}'.", variableName);
            throw new InvalidArgumentException("Invalid variable name: '" + variableName + "'. Variable names must start with a letter or underscore and contain only letters, numbers, and underscores.");
        }

        try {
            double value = Double.parseDouble(valueString);
            context.defineVariable(variableName, value);
            logger.info("DEFINE executed: {} = {}", variableName, value);
        } catch (NumberFormatException e) {
            logger.error("DEFINE operation failed: '{}' is not a valid number.", valueString);
            throw new InvalidArgumentException("Error: '" + valueString + "' is not a valid number.");
        }
    }
}