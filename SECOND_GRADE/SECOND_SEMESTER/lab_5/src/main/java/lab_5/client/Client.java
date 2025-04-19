package lab_5.client;

import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {
    private static final String SERVER_ADDRESS = "localhost";
    private static final int SERVER_PORT = 12345;

    private DataInputStream in;
    private DataOutputStream out;
    private String nickname;
    private String sessionId;

    public static void main(String[] args) {new Client().start(); }

    public void start() {
        try (Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT)) {
            in = new DataInputStream(socket.getInputStream());
            out = new DataOutputStream(socket.getOutputStream());

            out.writeUTF("JSON");

            Scanner scanner = new Scanner(System.in);

            while (sessionId == null || sessionId.isEmpty()) {
                System.out.print("Enter your nickname: ");
                nickname = scanner.nextLine().trim();
                if (nickname.isEmpty()) continue;

                String login = "{\"command\":\"login\",\"name\":\"" + nickname + "\",\"type\":\"JSONClient\"}";
                out.writeUTF(login);

                String response = in.readUTF();
                if (response.contains("\"error\"")) {
                    String error = extractValue(response, "message");
                    System.out.println("[ERROR] " + error);
                } else if (response.contains("\"success\"")) {
                    sessionId = extractValue(response, "session");
                    System.out.println("[SUCCESS] login OK");
                }
            }

            Thread listener = new Thread(this::listenForMessages);
            listener.setDaemon(true);
            listener.start();

            System.out.println("Type your messages below. Use /list to see users, /logout to exit:");
            while (true) {
                String input = scanner.nextLine();
                if (input.equalsIgnoreCase("/logout")) {
                    sendLogout();
                    break;
                } else if (input.equalsIgnoreCase("/list")) {
                    sendListRequest();
                } else if (!input.isBlank()) {
                    sendMessage(input);
                    System.out.println("You: " + input);
                }
            }

            System.out.println("[SYSTEM] You left the chat. Bye!");

        } catch (IOException e) {
            System.err.println("[ERROR] Connection error: " + e.getMessage());
        }
    }

    private void listenForMessages() {
        try {
            while (true) {
                String message = in.readUTF();

                if (message.contains("\"event\"")) {
                    if (message.contains("\"event\":\"userlogin\"")) {
                        String user = extractValue(message, "name");
                        System.out.println("[SYSTEM] " + user + " joined the chat");
                    } else if (message.contains("\"event\":\"userlogout\"")) {
                        String user = extractValue(message, "name");
                        System.out.println("[SYSTEM] " + user + " left the chat");
                    } else if (message.contains("\"event\":\"message\"")) {
                        String from = extractValue(message, "name");
                        String text = extractValue(message, "message");
                        if (!from.equals(nickname)) {
                            System.out.println(from + ": " + text);
                        }
                    }
                } else if (message.contains("\"success\"") && message.contains("listusers")) {
                    System.out.println("Users online:");
                    String[] entries = message.split("\\{");
                    for (String entry : entries) {
                        if (entry.contains("name") && entry.contains("type")) {
                            String name = extractValue(entry, "name");
                            String type = extractValue(entry, "type");
                            System.out.println(" - " + name + " (" + type + ")");
                        }
                    }
                } else if (message.contains("\"error\"")) {
                    String error = extractValue(message, "message");
                    System.out.println("[ERROR] " + error);
                }
            }
        } catch (IOException e) {
            System.out.println("[SYSTEM] Disconnected from server.");
        }
    }

    private String extractValue(String json, String key) {
        int start = json.indexOf("\"" + key + "\":\"");
        if (start == -1) return "";
        start += key.length() + 4;
        int end = json.indexOf("\"", start);
        return end == -1 ? "" : json.substring(start, end);
    }

    private void sendMessage(String msg) throws IOException {
        String json = "{\"command\":\"message\",\"message\":\"" + msg + "\",\"session\":\"" + sessionId + "\"}";
        out.writeUTF(json);
    }

    private void sendLogout() throws IOException {
        String json = "{\"command\":\"logout\",\"session\":\"" + sessionId + "\"}";
        out.writeUTF(json);
    }

    private void sendListRequest() throws IOException {
        String json = "{\"command\":\"list\",\"session\":\"" + sessionId + "\"}";
        out.writeUTF(json);
    }
}