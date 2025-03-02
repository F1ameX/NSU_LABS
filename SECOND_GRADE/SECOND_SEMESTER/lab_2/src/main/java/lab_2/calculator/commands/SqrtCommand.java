package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.InvalidArgumentException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class SqrtCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException, InvalidArgumentException {
        if (context.getStackSize() < 1) {
            logger.error("SQRT operation failed: Stack is empty.");
            throw new StackUnderflowException("Error: Stack is empty, cannot perform SQRT.");
        }
        double value = context.pop();

        if (value < 0) {
            logger.error("SQRT operation failed: Cannot calculate the square root of a negative number.");
            throw new InvalidArgumentException("Error: Cannot calculate the square root of a negative number.");
        }

        double result = Math.sqrt(value);
        context.push(result);
        logger.info("SQRT executed: sqrt({}) = {}", value, result);
    }
}