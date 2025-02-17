package lab_2.calculator.factory;

import lab_2.calculator.commands.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CommandFactoryTest {

    @Test
    void testCreateDefineCommand() throws Exception {
        CommandFactory factory = new CommandFactory();
        Command command = factory.createCommand("DEFINE");
        assertInstanceOf(DefineCommand.class, command, "Command should be of type DEFINECommand.");
    }

    @Test
    void testCreatePushCommand() throws Exception {
        CommandFactory factory = new CommandFactory();
        Command command = factory.createCommand("PUSH");
        assertInstanceOf(PushCommand.class, command, "Command should be of type PUSHCommand.");
    }

    @Test
    void testCreateAddCommand() throws Exception {
        CommandFactory factory = new CommandFactory();
        Command command = factory.createCommand("ADD");
        assertInstanceOf(AddCommand.class, command, "Command should be of type ADDCommand.");
    }

    @Test
    void testCreateMultiplyCommand() throws Exception {
        CommandFactory factory = new CommandFactory();
        Command command = factory.createCommand("MULTIPLY");
        assertInstanceOf(MultiplyCommand.class, command, "Command should be of type MULTIPLYCommand.");
    }

    @Test
    void testCreateCommandWithEmptyNameThrowsException() {
        CommandFactory factory = new CommandFactory();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> factory.createCommand(""));
        assertTrue(exception.getMessage().contains("Error: Command '' is not found!"),
                "Should throw an exception for empty command name.");
    }

    @Test
    void testCreateCommandWithWhitespaceNameThrowsException() {
        CommandFactory factory = new CommandFactory();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> factory.createCommand("   "));
        assertTrue(exception.getMessage().contains("Error: Command '   ' is not found!"),
                "Should throw an exception for command name with whitespace.");
    }

    @Test
    void testInvalidCommandThrowsException() {
        CommandFactory factory = new CommandFactory();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> factory.createCommand("INVALID"));
        assertTrue(exception.getMessage().contains("Error: Command 'INVALID' is not found"),
                "Should throw an exception for an invalid command.");
    }

   @Test
    void testConfigFileNotFoundThrowsException() {
        Exception exception = assertThrows(RuntimeException.class, CommandFactory::new);
        assertTrue(exception.getMessage().contains("Error: File commands.config is not found!"),
                "Should throw an exception when the configuration file is missing.");
    }

    /*@Test
    void testInvalidClassInConfigThrowsException() {
        Exception exception = assertThrows(RuntimeException.class, CommandFactory::new);
        assertTrue(exception.getMessage().contains("Error of uploading commands configuration"),
                "Should throw an exception if a class is invalid in the configuration.");
    }*/
}