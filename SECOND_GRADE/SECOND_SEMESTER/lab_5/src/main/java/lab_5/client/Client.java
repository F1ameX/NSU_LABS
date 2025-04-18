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
    private String nickname;

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
        this.nickname = name;
        JsonObject login = new JsonObject();
        login.addProperty("command", "login");
        login.addProperty("name", name);
        login.addProperty("type", "JSON_CLIENT");
        out.println(login);
    }

    public void sendMessage(String message) {
        JsonObject jsonMessage = new JsonObject();
        jsonMessage.addProperty("command", "message");
        jsonMessage.addProperty("message", message);
        out.println(jsonMessage);

        System.out.print("\033[A");
        System.out.print("\033[2K");

        System.out.println("You: " + message);
    }

    public void logout() {
        JsonObject logout = new JsonObject();
        logout.addProperty("command", "logout");
        out.println(logout);
    }

    public void requestUserList() {
        JsonObject list = new JsonObject();
        list.addProperty("command", "list");
        out.println(list);
    }

    public void listenForMessages() {
        new Thread(() -> {
            try {
                String response;
                while ((response = in.readLine()) != null) {
                    JsonObject json = JsonParser.parseString(response).getAsJsonObject();
                    String type = json.get("type").getAsString();

                    switch (type) {
                        case "message":
                            String from = json.get("from").getAsString();
                            String text = json.get("text").getAsString();
                            if (!from.equals(nickname)) {
                                System.out.println(from + ": " + text);
                            }
                            break;

                        case "system":
                            System.out.println("[SYSTEM] " + json.get("text").getAsString());
                            break;

                        case "success":
                            System.out.println("[SUCCESS] " + json.get("message").getAsString());
                            break;

                        case "error":
                            System.out.println("[ERROR] " + json.get("message").getAsString());
                            break;

                        default:
                            System.out.println("[UNKNOWN TYPE] " + response);
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
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
            } else if (input.equalsIgnoreCase("/list")) {
                client.requestUserList();
            } else {
                client.sendMessage(input);
            }
        }

        System.out.println("You left the chat. Bye!");
        System.exit(0);
    }
}