package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class SubtractCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() < 2) {
            logger.error("SUBTRACT operation failed: Not enough elements in the stack.");
            throw new StackUnderflowException("Error: SUBTRACT requires at least two elements on the stack.");
        }

        double b = context.pop();
        double a = context.pop();

        double result = a - b;
        context.push(result);
        logger.info("SUBTRACT executed: {} - {} = {}", a, b, result);
    }
}