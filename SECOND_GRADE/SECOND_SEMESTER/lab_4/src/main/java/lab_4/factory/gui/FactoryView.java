package lab_4.factory.gui;

import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.List;
import java.util.Hashtable;
import javax.swing.*;

import lab_4.factory.controller.FactoryController;
import lab_4.factory.dealers.Dealer;
import lab_4.factory.model.*;
import lab_4.factory.storage.Storage;
import lab_4.factory.suppliers.Supplier;
import lab_4.factory.workers.ThreadPool;

public class FactoryView extends JFrame {
    private final Storage<Body> bodyStorage;
    private final Storage<Motor> motorStorage;
    private final Storage<Accessory> accessoryStorage;
    private final Storage<Car> carStorage;
    private final Supplier<Body> bodySupplier;
    private final Supplier<Motor> motorSupplier;
    private final Supplier<Accessory> accessorySupplier;
    private final List<Dealer> dealers;
    private final ThreadPool threadPool;

    private final JLabel bodyCountLabel;
    private final JLabel motorCountLabel;
    private final JLabel accessoryCountLabel;
    private final JLabel carCountLabel;
    private final JLabel soldCarsLabel;
    private final JLabel queueSizeLabel;
    private final JLabel bodySuppliedLabel;
    private final JLabel motorSuppliedLabel;
    private final JLabel accessorySuppliedLabel;

    private final JSlider bodySpeedSlider;
    private final JSlider motorSpeedSlider;
    private final JSlider accessorySpeedSlider;
    private final JSlider dealerSpeedSlider;
    private final JTextField workerCountField;

    public FactoryView(Storage<Body> bodyStorage, Storage<Motor> motorStorage, Storage<Accessory> accessoryStorage,
                       Storage<Car> carStorage, Supplier<Body> bodySupplier, Supplier<Motor> motorSupplier,
                       Supplier<Accessory> accessorySupplier, List<Dealer> dealers, ThreadPool threadPool,
                       FactoryController factoryController) {
        this.bodyStorage = bodyStorage;
        this.motorStorage = motorStorage;
        this.accessoryStorage = accessoryStorage;
        this.carStorage = carStorage;
        this.bodySupplier = bodySupplier;
        this.motorSupplier = motorSupplier;
        this.accessorySupplier = accessorySupplier;
        this.dealers = dealers;
        this.threadPool = threadPool;

        setTitle("Factory Simulator");
        setSize(700, 450);
        setResizable(false);
        setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        setLayout(new BorderLayout());

        JPanel suppliersPanel = new JPanel(new GridLayout(3, 3));
        suppliersPanel.setBorder(BorderFactory.createTitledBorder("Suppliers"));

        bodySpeedSlider = createSlider(bodySupplier.getDelay());
        motorSpeedSlider = createSlider(motorSupplier.getDelay());
        accessorySpeedSlider = createSlider(accessorySupplier.getDelay());

        bodySpeedSlider.addChangeListener(e -> bodySupplier.setDelay(bodySpeedSlider.getValue()));
        motorSpeedSlider.addChangeListener(e -> motorSupplier.setDelay(motorSpeedSlider.getValue()));
        accessorySpeedSlider.addChangeListener(e -> accessorySupplier.setDelay(accessorySpeedSlider.getValue()));

        bodySuppliedLabel = new JLabel("Supplied: 0");
        motorSuppliedLabel = new JLabel("Supplied: 0");
        accessorySuppliedLabel = new JLabel("Supplied: 0");

        suppliersPanel.add(new JLabel("Body Supplier Speed (ms):"));
        suppliersPanel.add(bodySpeedSlider);
        suppliersPanel.add(bodySuppliedLabel);

        suppliersPanel.add(new JLabel("Motor Supplier Speed (ms):"));
        suppliersPanel.add(motorSpeedSlider);
        suppliersPanel.add(motorSuppliedLabel);

        suppliersPanel.add(new JLabel("Accessory Supplier Speed (ms):"));
        suppliersPanel.add(accessorySpeedSlider);
        suppliersPanel.add(accessorySuppliedLabel);

        JPanel storagesPanel = new JPanel(new GridLayout(3, 5));
        storagesPanel.setBorder(BorderFactory.createTitledBorder("Storages"));

        storagesPanel.add(new JLabel(""));
        storagesPanel.add(new JLabel("Bodies"));
        storagesPanel.add(new JLabel("Motors"));
        storagesPanel.add(new JLabel("Accessories"));
        storagesPanel.add(new JLabel("Cars"));

        storagesPanel.add(new JLabel("Capacity:"));
        JTextField bodyCapacityField = createCapacityField(bodyStorage);
        JTextField motorCapacityField = createCapacityField(motorStorage);
        JTextField accessoryCapacityField = createCapacityField(accessoryStorage);
        JTextField carCapacityField = createCapacityField(carStorage);

        storagesPanel.add(bodyCapacityField);
        storagesPanel.add(motorCapacityField);
        storagesPanel.add(accessoryCapacityField);
        storagesPanel.add(carCapacityField);

        storagesPanel.add(new JLabel("Stored:"));
        bodyCountLabel = new JLabel();
        motorCountLabel = new JLabel();
        accessoryCountLabel = new JLabel();
        carCountLabel = new JLabel();

        storagesPanel.add(bodyCountLabel);
        storagesPanel.add(motorCountLabel);
        storagesPanel.add(accessoryCountLabel);
        storagesPanel.add(carCountLabel);

        JPanel workersPanel = new JPanel();
        workersPanel.setBorder(BorderFactory.createTitledBorder("Workers"));

        workerCountField = new JTextField(String.valueOf(threadPool.getWorkerCount()), 5);
        workerCountField.addActionListener(e -> threadPool.setWorkerCount(Integer.parseInt(workerCountField.getText())));

        workersPanel.add(new JLabel("Number of Workers:"));
        workersPanel.add(workerCountField);

        JPanel dealersPanel = new JPanel();
        dealersPanel.setLayout(new BoxLayout(dealersPanel, BoxLayout.X_AXIS));
        dealersPanel.setBorder(BorderFactory.createTitledBorder("Dealers"));

        soldCarsLabel = new JLabel();
        queueSizeLabel = new JLabel();

        dealerSpeedSlider = createSlider(dealers.get(0).getDelay());
        dealerSpeedSlider.addChangeListener(e -> {
            for (Dealer dealer : dealers) {
                dealer.setDelay(dealerSpeedSlider.getValue());
            }
        });

        JPanel queuePanel = new JPanel(new GridLayout(1, 2));
        queuePanel.add(new JLabel("Sold Cars:"));
        queuePanel.add(soldCarsLabel);
        queuePanel.add(new JLabel("Queue Size:"));
        queuePanel.add(queueSizeLabel);

        dealersPanel.add(queuePanel);

        dealersPanel.add(new JLabel("Dealer Speed (ms):"));
        dealersPanel.add(dealerSpeedSlider);

        add(suppliersPanel, BorderLayout.NORTH);
        add(storagesPanel, BorderLayout.EAST);
        add(workersPanel, BorderLayout.WEST);
        add(dealersPanel, BorderLayout.SOUTH);

        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                factoryController.stop();
                System.out.println("Exiting...");
                System.exit(0);
            }
        });

        new Timer(500, e -> updateLabels()).start();
    }

    private JSlider createSlider(int initialValue) {
        JSlider slider = new JSlider(0, 5000, initialValue);
        slider.setMajorTickSpacing(1000);
        slider.setMinorTickSpacing(500);
        slider.setPaintTicks(true);
        slider.setPaintLabels(true);

        Hashtable<Integer, JLabel> labelTable = new Hashtable<>();
        for (int i = 0; i <= 5000; i += 1000)
            labelTable.put(i, new JLabel(String.valueOf(i)));

        slider.setLabelTable(labelTable);

        return slider;
    }

    private JTextField createCapacityField(Storage<?> storage) {
        JTextField field = new JTextField(String.valueOf(storage.getCapacity()), 5);
        field.addActionListener(e -> storage.setCapacity(Integer.parseInt(field.getText())));
        return field;
    }

    private void updateLabels() {
        bodyCountLabel.setText(String.valueOf(bodyStorage.getSize()));
        motorCountLabel.setText(String.valueOf(motorStorage.getSize()));
        accessoryCountLabel.setText(String.valueOf(accessoryStorage.getSize()));
        carCountLabel.setText(String.valueOf(carStorage.getSize()));

        int totalSoldCars = dealers.stream().mapToInt(Dealer::getSoldCarsCount).sum();
        soldCarsLabel.setText(String.valueOf(totalSoldCars));
        queueSizeLabel.setText(String.valueOf(threadPool.getQueueSize()));

        bodySuppliedLabel.setText("Supplied: " + bodySupplier.getSuppliedCount());
        motorSuppliedLabel.setText("Supplied: " + motorSupplier.getSuppliedCount());
        accessorySuppliedLabel.setText("Supplied: " + accessorySupplier.getSuppliedCount());
    }
}