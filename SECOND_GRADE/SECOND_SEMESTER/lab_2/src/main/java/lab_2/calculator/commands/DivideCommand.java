package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.DivisionByZeroException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class DivideCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException, DivisionByZeroException {
        if (context.getStackSize() < 2) {
            logger.error("Divide operation failed: Stack underflow. Not enough elements.");
            throw new StackUnderflowException("Error: Divide operation requires at least two elements on the stack.");
        }

        double divisor = context.pop();
        if (divisor == 0.0) {
            logger.error("Attempted division by zero. Operation aborted.");
            throw new DivisionByZeroException("Error: Division by zero is not allowed.");
        }

        double dividend = context.pop();
        double result = dividend / divisor;
        context.push(result);
        logger.info("DIVIDE executed: {} / {} = {}", dividend, divisor, result);
    }
}