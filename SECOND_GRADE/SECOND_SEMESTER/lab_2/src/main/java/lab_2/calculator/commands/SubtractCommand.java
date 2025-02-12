package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import java.util.List;

public class SubtractCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() < 2) {
            throw new StackUnderflowException("Error: SUBTRACT requires at least two elements on the stack.");
        }

        double b = context.pop();
        double a = context.pop();
        context.push(a - b);
    }
}