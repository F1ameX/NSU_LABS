package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;
import lab_2.calculator.exceptions.DivisionByZeroException;

import java.util.List;
public class DivideCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args)
    {
        if (context.getStackSize() < 2) {
            throw new StackUnderflowException("Error: DIVIDE requires at least two elements on the stack.");
        }

        double b = context.pop();
        if (b == 0) {
            throw new DivisionByZeroException("Error: Division by zero is not allowed.");
        }

        double a = context.pop();
        context.push(a / b);
    }
}
