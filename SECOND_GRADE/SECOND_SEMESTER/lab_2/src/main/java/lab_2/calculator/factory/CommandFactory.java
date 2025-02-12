package lab_2.calculator.factory;

import lab_2.calculator.commands.Command;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;


public class CommandFactory {
    private final Map<String, String> commandMap = new HashMap<>();

    public CommandFactory() { loadConfig();}


    private void loadConfig() {
        try (InputStream input = getClass().getResourceAsStream("/commands.config")) {
            if (input == null) {
                throw new RuntimeException("Error: File commands.config is not found!");
            }
            Properties properties = new Properties();
            properties.load(input);

            for (String key : properties.stringPropertyNames()) {
                commandMap.put(key.toUpperCase(), properties.getProperty(key));
            }
        } catch (IOException e) {
            throw new RuntimeException("Error of uploading commands configuration: " + e.getMessage());
        }
    }


    public Command createCommand(String commandName) throws Exception {
        String className = commandMap.get(commandName.toUpperCase());

        if (className == null) {
            throw new IllegalArgumentException("Error: Command '" + commandName + "'is not found!");
        }

        Class<?> commandClass = Class.forName(className);
        return (Command) commandClass.getDeclaredConstructor().newInstance();
    }
}