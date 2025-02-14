package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.util.List;

public class PushCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws InvalidArgumentException {
        if (args.isEmpty()) {
            logger.error("Error: PUSH requires one argument.");
            throw new InvalidArgumentException("PUSH requires one argument.");
        }

        String arg = args.get(0);
        try {
            double value = Double.parseDouble(arg);
            context.push(value);
            logger.info("PUSH executed: Pushed {}", value);
        } catch (NumberFormatException e) {
            if (context.hasVariable(arg)) {
                double value = context.getVariable(arg);
                context.push(value);
                logger.info("PUSH executed: Pushed variable {} with value {}", arg, value);
            } else {
                logger.error("Error: '{}' is not a number or a defined variable.", arg);
                throw new InvalidArgumentException("'" + arg + "' is not a number or a defined variable.");
            }
        }
    }
}