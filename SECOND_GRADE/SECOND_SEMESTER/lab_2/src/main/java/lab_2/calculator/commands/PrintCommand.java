package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.util.List;

public class PrintCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() == 0) {
            logger.error("Error: Cannot execute PRINT - stack is empty.");
            throw new StackUnderflowException("Cannot execute PRINT - stack is empty.");
        }

        double topValue = context.getTop();
        System.out.println(topValue);
        logger.info("PRINT executed: Top value is {}", topValue);
    }
}
