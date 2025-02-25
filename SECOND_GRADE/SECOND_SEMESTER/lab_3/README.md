# Minesweeper

This project is an implementation of the classic Minesweeper game in Java using the MVC architecture. It supports both graphical (Swing) and text-based (CLI) interfaces with customizable board size and mine count.

## Project Structure

- `Main.java` – Entry point, processes command-line arguments for selecting UI mode.
- `GameController.java` – Manages game logic and user interactions.
- `Game.java`, `GameBoard.java`, `Cell.java` – Core model classes handling Minesweeper logic.
- `GraphicalView.java` – GUI implementation using Swing.
- `TextView.java` – Console-based interface.
- `HighScoresManager.java` – Handles high score storage.
- `resources/images/` – Stores game assets (32x32 pixel icons).
- `highscores.txt` – Stores the top 5 best scores.

## Build & Run

### Clone the Repository
```bash
git clone https://github.com/F1ameX/NSU_LABS/new/main/SECOND_GRADE/SECOND_SEMESTER/lab_3
cd minesweeper
```

### Build with Maven 
```bash
mvn clean package
```

## Run the Game

### Graphical Mode (default)
```bash
mvn exec:java -Dexec.mainClass="lab_3.minesweeper.app.Main"
```
### Text Mode
```bash
mvn exec:java -Dexec.mainClass="lab_3.minesweeper.app.Main" -Dexec.args="--text"
```

### Custom Board Size & Mines
```bash
mvn exec:java -Dexec.mainClass="lab_3.minesweeper.app.Main" -Dexec.args="--size 25x25 --mines 30"
```

### Text Mode with Custom Size
```bash
mvn exec:java -Dexec.mainClass="lab_3.minesweeper.app.Main" -Dexec.args="--text --size 25x25 --mines 30"
```

## Features

- Supports both GUI and CLI modes.
- Adjustable board size and mine count.
- Automatic opening of empty cells.
- Timer to track game completion time.
- High score tracking.
- Mouse and keyboard controls:
  - **Left Click / `o x y`** – Open a cell
  - **Right Click / `f x y`** – Flag/Unflag a mine

## Configuration

- Board size and mine count are set using command-line arguments (`--size WxH --mines N`).
- High scores are saved in `highscores.txt`.

### Requirements
• Java 17+
• Maven 3.8+
