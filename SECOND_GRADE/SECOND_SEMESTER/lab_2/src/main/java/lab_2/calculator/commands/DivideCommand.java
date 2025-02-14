package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.DivisionByZeroException;
import lab_2.calculator.logger.CalculatorLogger;
import org.apache.logging.log4j.Logger;

import java.util.List;


public class DivideCommand implements Command {
    private static final Logger logger = CalculatorLogger.getLogger();

    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException, DivisionByZeroException {
        if (context.getStackSize() < 2) {
            logger.error("Error: DIVIDE requires at least two elements on the stack.");
            throw new StackUnderflowException("DIVIDE requires at least two elements on the stack.");
        }

        double b = context.pop();
        if (b == 0) {
            logger.error("Error: Division by zero is not allowed.");
            throw new DivisionByZeroException("Division by zero is not allowed.");
        }

        double a = context.pop();
        double result = a / b;
        context.push(result);
        logger.info("DIVIDE executed: {} / {} = {}", a, b, result);
    }
}