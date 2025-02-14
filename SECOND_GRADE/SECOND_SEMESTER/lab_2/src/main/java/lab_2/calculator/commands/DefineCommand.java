package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.util.List;

public class DefineCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws InvalidArgumentException {
        if (args.size() != 2) {
            logger.error("Error: DEFINE requires exactly two arguments (name and value).");
            throw new InvalidArgumentException("DEFINE requires exactly two arguments (name and value).");
        }

        String variableName = args.get(0);
        String valueStr = args.get(1);

        try {
            double value = Double.parseDouble(valueStr);
            context.defineVariable(variableName, value);
            logger.info("DEFINE executed: {} = {}", variableName, value);
        } catch (NumberFormatException e) {
            logger.error("Error: '{}' is not a valid number.", valueStr);
            throw new InvalidArgumentException("'" + valueStr + "' is not a valid number.");
        }
    }
}