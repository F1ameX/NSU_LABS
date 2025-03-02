package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class MultiplyCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() < 2) {
            logger.error("MULTIPLY operation failed: Not enough elements in the stack.");
            throw new StackUnderflowException("Error: MULTIPLY requires at least two elements on the stack.");
        }

        double operand2 = context.pop();
        double operand1 = context.pop();

        double result = operand1 * operand2;
        context.push(result);
        logger.info("MULTIPLY executed: {} * {} = {}", operand1, operand2, result);
    }
}