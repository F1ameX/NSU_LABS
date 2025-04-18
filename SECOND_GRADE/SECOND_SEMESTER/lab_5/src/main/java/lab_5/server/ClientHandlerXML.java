package lab_5.server;

import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.net.Socket;

public class ClientHandlerXML extends ClientHandler {
    private final DataInputStream in;
    private final DataOutputStream out;

    public ClientHandlerXML(Socket socket, InputStream inStream) throws IOException {
        super(socket);
        this.in = new DataInputStream(inStream);
        this.out = new DataOutputStream(socket.getOutputStream());
    }

    @Override
    public void run() {
        try {
            while (true) {
                int len = in.readInt();
                byte[] buffer = new byte[len];
                in.readFully(buffer);

                Document doc;
                try {
                    doc = DocumentBuilderFactory.newInstance()
                            .newDocumentBuilder()
                            .parse(new ByteArrayInputStream(buffer));
                } catch (Exception e) {
                    sendXml(buildError("Invalid XML format"));
                    System.err.println("[ERROR] Invalid XML: " + e.getMessage());
                    continue;
                }

                Element root = doc.getDocumentElement();
                if (!root.getTagName().equals("command") || !root.hasAttribute("name")) {
                    sendXml(buildError("Invalid <command> structure"));
                    continue;
                }

                String command = root.getAttribute("name");

                switch (command) {
                    case "login":
                        String name = getText(root, "name");
                        if (name == null || name.isEmpty()) {
                            sendXml(buildError("Missing <name> for login"));
                            continue;
                        }

                        if (Server.isNameTaken(name)) {
                            sendXml(buildError("Name already taken"));
                            continue;
                        }

                        clientName = name;
                        clientType = getText(root, "type");
                        System.out.println("[LOGIN] " + clientName + " (" + clientType + ")");

                        sendXml(buildSuccess("login OK"));
                        Server.broadcastSystemMessage(clientName + " joined the chat");
                        break;

                    case "message":
                        String text = getText(root, "message");
                        if (text == null || text.isEmpty()) {
                            sendXml(buildError("Missing <message> content"));
                            continue;
                        }
                        Server.broadcastUserMessage(clientName, text);
                        sendXml(buildSuccess("message delivered"));
                        break;

                    case "list":
                        sendXml(Server.buildUserListXml());
                        break;

                    case "logout":
                        sendXml(buildSuccess("bye"));
                        return;

                    default:
                        sendXml(buildError("Unknown command: " + command));
                }
            }
        } catch (Exception e) {
            System.err.println("[ERROR] XML client crashed: " + e.getMessage());
        } finally {
            Server.getClients().remove(this);
            Server.broadcastSystemMessage(clientName + " left the chat");
        }
    }

    private String getText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagName(tag);
        if (list.getLength() == 0) return null;
        return list.item(0).getTextContent();
    }

    private Document buildSuccess(String msg) throws Exception {
        Document doc = newDocument();
        Element success = doc.createElement("success");
        Element message = doc.createElement("message");
        message.setTextContent(msg);
        success.appendChild(message);
        doc.appendChild(success);
        return doc;
    }

    private Document buildError(String msg) throws Exception {
        Document doc = newDocument();
        Element error = doc.createElement("error");
        Element message = doc.createElement("message");
        message.setTextContent(msg);
        error.appendChild(message);
        doc.appendChild(error);
        return doc;
    }

    private Document newDocument() throws Exception {
        return DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
    }

    public void sendXml(Document doc) {
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            Transformer transformer = TransformerFactory.newInstance().newTransformer();
            transformer.transform(new DOMSource(doc), new StreamResult(baos));
            byte[] bytes = baos.toByteArray();
            out.writeInt(bytes.length);
            out.write(bytes);
        } catch (Exception e) {
            System.err.println("[ERROR] Failed to send XML: " + e.getMessage());
        }
    }

    @Override
    public boolean isXml() {
        return true;
    }
}