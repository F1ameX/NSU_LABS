package lab_5.clientxml;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;
import javax.xml.parsers.*;
import org.w3c.dom.*;

public class ClientXML {
    private static final String SERVER_HOST = "localhost";
    private static final int SERVER_PORT = 12345;

    private DataOutputStream out;
    private DataInputStream in;
    private String sessionId;
    private String nickname;
    private DocumentBuilder builder;

    public static void main(String[] args) {new ClientXML().start(); }
    private String buildXml(String content) {return content; }
    private String escape(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }

    public void start() {
        try (Socket socket = new Socket(SERVER_HOST, SERVER_PORT)) {
            out = new DataOutputStream(socket.getOutputStream());
            in = new DataInputStream(socket.getInputStream());

            out.writeUTF("XML");

            builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            Scanner scanner = new Scanner(System.in);

            while (sessionId == null || sessionId.isEmpty()) {
                System.out.print("Enter your nickname: ");
                nickname = scanner.nextLine().trim();
                if (nickname.isEmpty()) continue;

                sendXml(buildXml("<command name=\"login\"><name>" + escape(nickname) + "</name><type>XMLClient</type></command>"));

                Document response = receiveXml();
                if (response.getDocumentElement().getTagName().equals("error")) {
                    System.out.println("[ERROR] " + getText(response.getDocumentElement(), "message"));
                } else {
                    sessionId = getText(response.getDocumentElement(), "session");
                    System.out.println("[SUCCESS] login OK");
                }
            }

            Thread listener = new Thread(this::listen);
            listener.setDaemon(true);
            listener.start();

            System.out.println("Type your messages below. Use /list to see users, /logout to exit:");
            while (true) {
                String input = scanner.nextLine();
                if (input.equalsIgnoreCase("/logout")) {
                    sendXml(buildXml("<command name=\"logout\"><session>" + sessionId + "</session></command>"));
                    break;
                } else if (input.equalsIgnoreCase("/list")) {
                    sendXml(buildXml("<command name=\"list\"><session>" + sessionId + "</session></command>"));
                } else if (!input.isBlank()) {
                    sendXml(buildXml("<command name=\"message\"><message>" + escape(input) + "</message><session>" + sessionId + "</session></command>"));
                    System.out.println("You: " + input);
                }
            }

            System.out.println("[SYSTEM] You left the chat. Bye!");

        } catch (Exception e) {
            System.err.println("[ERROR] " + e.getMessage());
        }
    }

    private void listen() {
        try {
            while (true) {
                Document doc = receiveXml();
                if (doc == null) break;

                Element root = doc.getDocumentElement();
                switch (root.getTagName()) {
                    case "event" -> {
                        String type = root.getAttribute("name");
                        switch (type) {
                            case "message" -> {
                                String from = getText(root, "name");
                                String msg = getText(root, "message");
                                assert from != null;
                                if (!from.equals(nickname)) System.out.println(from + ": " + msg);
                            }
                            case "userlogin" -> System.out.println("[SYSTEM] " + getText(root, "name") + " joined the chat");
                            case "userlogout" -> System.out.println("[SYSTEM] " + getText(root, "name") + " left the chat");
                        }
                    }
                    case "success" -> {
                        if (root.getElementsByTagName("listusers").getLength() > 0) {
                            System.out.println("Users online:");
                            NodeList users = root.getElementsByTagName("user");
                            for (int i = 0; i < users.getLength(); i++) {
                                Element user = (Element) users.item(i);
                                String name = getText(user, "name");
                                String type = getText(user, "type");
                                System.out.println(" - " + name + " (" + type + ")");
                            }
                        }
                    }
                    case "error" -> System.out.println("[ERROR] " + getText(root, "message"));
                }
            }
        } catch (Exception e) {
            System.out.println("[SYSTEM] Disconnected from server.");
        }
    }

    private void sendXml(String xml) throws IOException {
        byte[] data = xml.getBytes(StandardCharsets.UTF_8);
        out.writeInt(data.length);
        out.write(data);
        out.flush();
    }

    private Document receiveXml() throws Exception {
        int len = in.readInt();
        byte[] data = new byte[len];
        in.readFully(data);
        return builder.parse(new ByteArrayInputStream(data));
    }

    private String getText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        if (list.getLength() == 0) return null;
        return list.item(0).getTextContent();
    }
}