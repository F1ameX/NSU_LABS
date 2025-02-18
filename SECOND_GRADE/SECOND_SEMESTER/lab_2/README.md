# Calculator

This project is a simple calculator application that supports various commands, including arithmetic operations, variable storage, and command execution based on a configuration file.

## Project Structure
- `Main.java` – Entry point of the application, initializes the calculator and processes input commands.
- `CommandFactory.java` – Creates commands based on configuration and command input.
- `Command.java` – Interface for all command classes.
- `AddCommand.java`, `SubtractCommand.java`, `MultiplyCommand.java`, `DivideCommand.java`, etc. – Implementations of arithmetic operations.
- `CommandFactoryTest.java` – Unit tests for the `CommandFactory` class.
- `CalculatorLogger.java` – Logger for logging commands execution.
- `commands.config` – Configuration file for mapping commands to their respective classes.
- `ExecutionContext.java` – Maintains the stack of values and history of operations.
- `exceptions/` – Custom exceptions for error handling (e.g., `DivisionByZeroException`, `StackUnderflowException`).

## Build & Run

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd calculator
```
### 2. Build the Project with Maven
```bash
mvn clean package
```
### 3. Run the Program:
```bash
mvn exec:java -Dexec.args="input.txt"
```
### 4. Configuration

Commands are defined in the `commands.config` file, where each command (e.g., `ADD`, `SUBTRACT`) is mapped to its corresponding class name.

Example of `commands.config`:
```properties
ADD=lab_2.calculator.commands.AddCommand
SUBTRACT=lab_2.calculator.commands.SubtractCommand
```

##### Features
• Arithmetic operations: Supports basic operations like addition, subtraction, multiplication, and division.
• Error handling: Includes custom exceptions like division by zero and stack underflow errors.
• Logging: Command execution and errors are logged for better traceability.

##### Tests

The project includes unit tests using JUnit for command execution and error handling. The tests are located in the src/test/java folder.

Run tests using:
```bash
mvn test
```

##### Requirements
• Java 17+
• Maven 3.8+
• JUnit for unit testing
