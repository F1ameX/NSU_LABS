package lab_5.client;

import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {
    private static final String SERVER_ADDRESS = "localhost";
    private static final int SERVER_PORT = 12345;

    private DataInputStream in;
    private DataOutputStream out;
    private Socket socket;
    private String sessionId;
    private volatile boolean running = true;

    public static void main(String[] args) {new Client().start();}

    public void start() {
        try {
            socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
            in = new DataInputStream(socket.getInputStream());
            out = new DataOutputStream(socket.getOutputStream());
            out.writeUTF("JSON");

            Scanner scanner = new Scanner(System.in);
            while (sessionId == null || sessionId.isEmpty()) {
                System.out.print("Enter your nickname: ");
                String nickname = scanner.nextLine().trim();
                if (nickname.isEmpty()) continue;

                String login = "{\"command\":\"login\",\"name\":\"" + nickname + "\",\"type\":\"JSONClient\"}";
                out.writeUTF(login);
                String response = in.readUTF();
                if (response.contains("\"error\"")) System.out.println("[ERROR] " + extractValue(response, "message"));
                else if (response.contains("\"success\"")) {
                    sessionId = extractValue(response, "session");
                    System.out.println("[SUCCESS] login OK");
                }
            }

            Thread listener = new Thread(this::listenForMessages);
            Thread pinger = new Thread(this::startPinger);
            Thread inputThread = new Thread(this::handleUserInput);

            listener.start();
            pinger.start();
            inputThread.start();

            listener.join();
            inputThread.join();
            pinger.interrupt();

        } catch (IOException | InterruptedException e) {
            exitWithError("Disconnected or error: " + e.getMessage());
        } finally {
            closeResources();
            System.out.println("[SYSTEM] You left the chat. Bye!");
        }
    }

    private void listenForMessages() {
        try {
            while (running) {
                String message = in.readUTF();

                if (message.contains("\"event\"")) {
                    if (message.contains("\"event\":\"userlogin\""))
                        System.out.println("[SYSTEM] " + extractValue(message, "name") + " joined the chat");
                    else if (message.contains("\"event\":\"userlogout\""))
                        System.out.println("[SYSTEM] " + extractValue(message, "name") + " left the chat");
                    else if (message.contains("\"event\":\"message\"")) {
                        String from = extractValue(message, "name");
                        String text = extractValue(message, "message");

                        if (from.equals("You")) System.out.println("You: " + text);
                        else System.out.println(from + ": " + text);
                    }
                }
                else if (message.contains("\"success\"") && message.contains("listusers")) {
                    System.out.println("Users online:");
                    String[] entries = message.split("\\{");
                    for (String entry : entries) {
                        if (entry.contains("name") && entry.contains("type")) {
                            String name = extractValue(entry, "name");
                            String type = extractValue(entry, "type");
                            System.out.println(" - " + name + " (" + type + ")");
                        }
                    }
                }
                else if (message.contains("\"error\"")) exitWithError(extractValue(message, "message"));
            }
        } catch (IOException e) {
            exitWithError("Disconnected by server.");
        }
    }

    private void handleUserInput() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Type your messages below. Use /list to see users, /logout to exit:");
        while (running) {
            String input = scanner.nextLine();
            if (!running || socket.isClosed()) break;

            try {
                if (input.equalsIgnoreCase("/logout")) {
                    sendLogout();
                    running = false;
                    break;
                }
                else if (input.equalsIgnoreCase("/list"))
                    sendListRequest();
                else if (!input.isBlank())
                    sendMessage(input);
            } catch (IOException e) {
                exitWithError("Failed to send message: " + e.getMessage());
            }
        }
    }

    private void startPinger() {
        while (running) {
            try {
                Thread.sleep(1000);
                out.writeUTF("{\"command\":\"ping\"}");
            } catch (Exception e) {
                exitWithError("Ping failed, server probably unreachable.");
                break;
            }
        }
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

    private String extractValue(String json, String key) {
        int start = json.indexOf("\"" + key + "\":\"");
        if (start == -1) return "";
        start += key.length() + 4;
        int end = json.indexOf("\"", start);
        return end == -1 ? "" : json.substring(start, end);
    }

    private void exitWithError(String msg) {
        System.out.println("[ERROR] " + msg);
        running = false;
        closeResources();
        System.exit(0);
    }

    private void closeResources() {
        try {
            if (socket != null && !socket.isClosed()) socket.close();
        } catch (IOException ignored) {}
    }
}