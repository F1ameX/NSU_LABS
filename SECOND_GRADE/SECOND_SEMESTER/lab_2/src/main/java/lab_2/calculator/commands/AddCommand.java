package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class AddCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() < 2) {
            logger.error("Error: ADD requires at least two elements on the stack.");
            throw new StackUnderflowException("ADD requires at least two elements on the stack.");
        }

        double b = context.pop();
        double a = context.pop();
        double result = a + b;

        context.push(result);
        logger.info("ADD executed: {} + {} = {}", a, b, result);
    }
}