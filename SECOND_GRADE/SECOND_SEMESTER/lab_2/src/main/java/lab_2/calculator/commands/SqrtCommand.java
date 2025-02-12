package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.InvalidArgumentException;
import java.util.List;

public class SqrtCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException, InvalidArgumentException {
        if (context.getStackSize() < 1) {
            throw new StackUnderflowException("Error: SQRT requires at least one element on the stack.");
        }

        double a = context.pop();
        if (a < 0) {
            throw new InvalidArgumentException("Error: Cannot calculate the square root of a negative number.");
        }

        context.push(Math.sqrt(a));
    }
}
