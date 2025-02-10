# Word Frequency Counter

This project analyzes a text file, counts word occurrences, calculates their percentage, and saves the results in a CSV file.

## Project Structure
- `Main.java` – Entry point, manages file input and output.
- `WordData.java` – Reads text, extracts words, counts occurrences using `merge()`.
- `CSVWriter.java` – Sorts and writes data to a CSV file.
- `WordFrequency.java` – Immutable record storing word frequency data.

## Build & Run

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd word-counter
```

### 2. Build the Project with Maven
```bash
mvn clean package
```

### 3. Run the program:
```bash
mvn exec:java -Dexec.args="input.txt output.csv"
```

## Requirements
- Java 17+
- Maven 3.8+
