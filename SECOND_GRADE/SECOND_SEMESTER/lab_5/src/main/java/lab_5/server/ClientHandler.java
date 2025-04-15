package lab_5.server;

import java.io.*;
import java.net.*;
import com.google.gson.*;

public class ClientHandler implements Runnable {
    private final Socket socket;
    private PrintWriter out;

    public ClientHandler(Socket socket) {
        this.socket = socket;
    }

    @Override
    public void run() {
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            out = new PrintWriter(socket.getOutputStream(), true);

            String message;
            while ((message = in.readLine()) != null) {
                JsonObject jsonMessage = JsonParser.parseString(message).getAsJsonObject();
                String command = jsonMessage.get("command").getAsString();

                if ("message".equals(command)) {
                    String clientMessage = jsonMessage.get("message").getAsString();
                    System.out.println("Received message: " + clientMessage);

                    JsonObject response = new JsonObject();
                    response.addProperty("status", "success");
                    response.addProperty("receivedMessage", clientMessage); // Эхо-сообщение
                    sendResponse(response);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void sendResponse(JsonObject response) {
        out.println(response.toString());
    }
}