package lab_2.calculator.commands;
import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class PopCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() == 0) {
            logger.error("Pop operation failed: Stack is empty.");
            throw new StackUnderflowException("Error: Cannot pop from an empty stack.");
        }

        double removedValue = context.pop();
        logger.info("POP executed: Removed {}", removedValue);
    }
}