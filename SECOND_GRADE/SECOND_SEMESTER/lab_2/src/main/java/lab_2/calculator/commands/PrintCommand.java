package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.logger.CalculatorLogger;
import lab_2.calculator.exceptions.StackUnderflowException;
import org.apache.logging.log4j.Logger;
import java.util.List;

public class PrintCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() < 1) {
            logger.error("PRINT operation failed: Stack is empty.");
            throw new StackUnderflowException("Error: Stack is empty, cannot perform PRINT.");
        }

        double value = context.getTop();
        System.out.println(value);
        logger.info("PRINT executed: Top value is {}", value);
    }
}