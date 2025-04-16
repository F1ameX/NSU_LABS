package lab_5.clientxml;

import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class ClientXML {
    private static final String SERVER_HOST = "localhost";
    private static final int SERVER_PORT = 12345;

    private DataOutputStream out;
    private DataInputStream in;

    public static void main(String[] args) {new ClientXML().start(); }
    private Document newDocument() throws Exception {
        return DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
    }

    public void start() {
        try (Socket socket = new Socket(SERVER_HOST, SERVER_PORT)) {
            out = new DataOutputStream(socket.getOutputStream());
            in = new DataInputStream(socket.getInputStream());

            Scanner scanner = new Scanner(System.in);
            System.out.print("Enter your nickname: ");
            String sessionName = scanner.nextLine();

            sendXML(buildLoginCommand(sessionName));

            Thread listener = new Thread(this::listen);
            listener.setDaemon(true);
            listener.start();

            while (true) {
                String line = scanner.nextLine();
                if (line.equalsIgnoreCase("/exit")) {
                    sendXML(buildLogoutCommand(sessionName));
                    break;
                } else {
                    sendXML(buildMessageCommand(sessionName, line));
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void listen() {
        try {
            while (true) {
                int length = in.readInt();
                byte[] data = new byte[length];
                in.readFully(data);

                Document doc = DocumentBuilderFactory.newInstance()
                        .newDocumentBuilder()
                        .parse(new ByteArrayInputStream(data));
                doc.getDocumentElement().normalize();

                printXML(doc);
            }
        } catch (Exception e) {
            System.out.println("Disconnected from server.");
        }
    }

    private void printXML(Document doc) {
        try {
            Transformer transformer = TransformerFactory.newInstance().newTransformer();
            transformer.transform(new DOMSource(doc), new StreamResult(System.out));
            System.out.println();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void sendXML(Document doc) {
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            Transformer transformer = TransformerFactory.newInstance().newTransformer();
            transformer.transform(new DOMSource(doc), new StreamResult(baos));

            byte[] xmlBytes = baos.toByteArray();
            out.writeInt(xmlBytes.length);
            out.write(xmlBytes);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private Document buildLoginCommand(String name) throws Exception {
        Document doc = newDocument();
        Element command = doc.createElement("command");
        command.setAttribute("name", "login");

        Element nameElement = doc.createElement("name");
        nameElement.setTextContent(name);

        Element type = doc.createElement("type");
        type.setTextContent("XML_CLIENT");

        command.appendChild(nameElement);
        command.appendChild(type);
        doc.appendChild(command);
        return doc;
    }

    private Document buildMessageCommand(String name, String message) throws Exception {
        Document doc = newDocument();
        Element command = doc.createElement("command");
        command.setAttribute("name", "message");

        Element msg = doc.createElement("message");
        msg.setTextContent(message);

        Element session = doc.createElement("session");
        session.setTextContent(name);

        command.appendChild(msg);
        command.appendChild(session);
        doc.appendChild(command);
        return doc;
    }

    private Document buildLogoutCommand(String name) throws Exception {
        Document doc = newDocument();
        Element command = doc.createElement("command");
        command.setAttribute("name", "logout");

        Element session = doc.createElement("session");
        session.setTextContent(name);

        command.appendChild(session);
        doc.appendChild(command);
        return doc;
    }
}