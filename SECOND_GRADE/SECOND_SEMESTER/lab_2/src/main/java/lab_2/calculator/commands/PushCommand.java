package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;
import java.util.List;

public class PushCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args) throws InvalidArgumentException {
        if (args.isEmpty()) {
            throw new InvalidArgumentException("Error: PUSH accepts only one argument");
        }

        String arg = args.getFirst();
        try {
            double value = Double.parseDouble(arg);
            context.push(value);
        } catch (NumberFormatException e) {
            if (context.hasVariable(arg)) {
                context.push(context.getVariable(arg));
            } else {
                throw new InvalidArgumentException("Error: '" + arg + "'is not number or defined operation.");
            }
        }
    }
}