package lab_5.client;

import com.google.gson.*;
import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Client {
    private static final String SERVER_ADDRESS = "localhost";
    private static final int SERVER_PORT = 12345;
    private PrintWriter out;
    private BufferedReader in;

    public Client() {
        try {
            Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void login(String name) {
        JsonObject login = new JsonObject();
        login.addProperty("command", "login");
        login.addProperty("name", name);
        login.addProperty("type", "JSON_CLIENT");  // <-- добавлен тип клиента
        out.println(login.toString());
    }

    public void sendMessage(String message) {
        JsonObject jsonMessage = new JsonObject();
        jsonMessage.addProperty("command", "message");
        jsonMessage.addProperty("message", message);
        out.println(jsonMessage.toString());
    }

    public void logout() {
        JsonObject logout = new JsonObject();
        logout.addProperty("command", "logout");
        out.println(logout.toString());
    }

    public void listenForMessages() {
        new Thread(() -> {
            try {
                String response;
                while ((response = in.readLine()) != null) {
                    System.out.println("Received: " + response);
                }
            } catch (IOException e) {
                System.out.println("Disconnected from server.");
            }
        }).start();
    }

    public static void main(String[] args) {
        Client client = new Client();
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter your nickname: ");
        String nickname = scanner.nextLine();

        client.listenForMessages();
        client.login(nickname);

        while (true) {
            String input = scanner.nextLine();
            if (input.equalsIgnoreCase("/exit")) {
                client.logout();
                break;
            } else {
                client.sendMessage(input);
            }
        }

        System.out.println("You left the chat. Bye!");
        System.exit(0);
    }
}