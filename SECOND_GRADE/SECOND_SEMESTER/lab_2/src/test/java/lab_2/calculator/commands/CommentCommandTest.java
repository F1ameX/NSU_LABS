package lab_2.calculator.commands;

import lab_2.calculator.context.ExecutionContext;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class CommentCommandTest {
    private ExecutionContext context;
    private CommentCommand commentCommand;

    @BeforeEach
    void setUp() {
        context = new ExecutionContext();
        commentCommand = new CommentCommand();
    }

    @Test
    void testCommentDoesNothing() {
        assertDoesNotThrow(() -> commentCommand.execute(context, List.of("This is a comment")),
                "Comment should be ignored without errors.");
    }

    @Test
    void testEmptyCommentDoesNothing() {
        assertDoesNotThrow(() -> commentCommand.execute(context, List.of()),
                "Empty comment should be ignored without errors.");
    }
}
