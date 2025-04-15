package lab_5.client;

import com.google.gson.*;
import java.io.*;
import java.net.*;

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

    public void sendMessage(String message) {
        JsonObject jsonMessage = new JsonObject();
        jsonMessage.addProperty("command", "message");
        jsonMessage.addProperty("message", message);
        out.println(jsonMessage);
    }

    public void listenForMessages() {
        new Thread(() -> {
            try {
                String response;
                while ((response = in.readLine()) != null) {
                    System.out.println("Received: " + response);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();
    }

    public static void main(String[] args) {
        Client client = new Client();
        client.listenForMessages();
        client.sendMessage("Hello, Server!");
    }
}
