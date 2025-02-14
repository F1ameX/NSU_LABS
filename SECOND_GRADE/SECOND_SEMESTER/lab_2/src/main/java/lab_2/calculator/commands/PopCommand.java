package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.util.List;

public class PopCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() == 0) {
            logger.error("Error: Cannot execute POP - stack is empty.");
            throw new StackUnderflowException("Cannot execute POP - stack is empty.");
        }

        double removedValue = context.pop();
        logger.info("POP executed: Removed {}", removedValue);
    }
}