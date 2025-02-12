package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.StackUnderflowException;

import java.util.List;

public class PrintCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args) throws StackUnderflowException {
        if (context.getStackSize() == 0) {
            throw new StackUnderflowException("Error: Cannot execute PRINT - stack is empty!");
        }
        System.out.println(context.getTop());
    }
}
