package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import lab_2.calculator.exceptions.InvalidArgumentException;

import java.util.List;

public class DefineCommand implements Command {
    @Override
    public void execute(ExecutionContext context, List<String> args) throws InvalidArgumentException {
        if (args.size() != 2) {
            throw new InvalidArgumentException("Error: DEFINE requires exactly two arguments (name and value).");
        }

        String variableName = args.get(0);
        String valueStr = args.get(1);

        try {
            double value = Double.parseDouble(valueStr);
            context.defineVariable(variableName, value);
        } catch (NumberFormatException e) {
            throw new InvalidArgumentException("Error: '" + valueStr + "' is not a valid number.");
        }
    }
}