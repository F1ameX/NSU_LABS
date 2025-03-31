package lab_4.factory.gui;

import lab_4.factory.controller.FactoryController;

import javax.swing.*;
import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class FactoryView {
    private final FactoryController controller;
    private final JLabel producedCarsLabel;
    private final JLabel storageStatusLabel;
    private final JSlider supplierBodySpeedSlider;
    private final JSlider supplierMotorSpeedSlider;
    private final JSlider supplierAccessorySpeedSlider;
    private final JSlider dealerSpeedSlider;
    private SwingWorker<Void, Void> updateProducedCarsWorker;
    private SwingWorker<Void, Void> updateStorageStatusWorker;
    private boolean running = false;

    public FactoryView(String configPath) {
        controller = new FactoryController(configPath);

        JFrame frame = new JFrame("Factory Simulator");
        frame.setSize(500, 400);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new GridLayout(6, 1));

        supplierBodySpeedSlider = createSlider(100, 2000, controller.getSupplierBodyDelay());
        supplierMotorSpeedSlider = createSlider(100, 2000, controller.getSupplierMotorDelay());
        supplierAccessorySpeedSlider = createSlider(100, 2000, controller.getSupplierAccessoryDelay());
        dealerSpeedSlider = createSlider(100, 2000, controller.getDealerDelay());

        JPanel supplierBodyPanel = new JPanel();
        supplierBodyPanel.add(new JLabel("Body Supplier Speed:"));
        supplierBodyPanel.add(supplierBodySpeedSlider);

        JPanel supplierMotorPanel = new JPanel();
        supplierMotorPanel.add(new JLabel("Motor Supplier Speed:"));
        supplierMotorPanel.add(supplierMotorSpeedSlider);

        JPanel supplierAccessoryPanel = new JPanel();
        supplierAccessoryPanel.add(new JLabel("Accessory Supplier Speed:"));
        supplierAccessoryPanel.add(supplierAccessorySpeedSlider);

        JPanel dealerPanel = new JPanel();
        dealerPanel.add(new JLabel("Dealer Speed:"));
        dealerPanel.add(dealerSpeedSlider);

        producedCarsLabel = new JLabel("Produced Cars: 0");
        storageStatusLabel = new JLabel("Storage Status: Loading...");

        JButton startButton = new JButton("Start");
        JButton stopButton = new JButton("Stop");

        startButton.addActionListener(e -> startFactory());
        stopButton.addActionListener(e -> stopFactory());

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(startButton);
        buttonPanel.add(stopButton);

        frame.add(supplierBodyPanel);
        frame.add(supplierMotorPanel);
        frame.add(supplierAccessoryPanel);
        frame.add(dealerPanel);
        frame.add(producedCarsLabel);
        frame.add(storageStatusLabel);
        frame.add(buttonPanel);

        supplierBodySpeedSlider.addChangeListener(e -> {
            int newDelay = supplierBodySpeedSlider.getValue();
            controller.setSupplierBodyDelay(newDelay);
        });

        supplierMotorSpeedSlider.addChangeListener(e -> {
            int newDelay = supplierMotorSpeedSlider.getValue();
            controller.setSupplierMotorDelay(newDelay);
        });

        supplierAccessorySpeedSlider.addChangeListener(e -> {
            int newDelay = supplierAccessorySpeedSlider.getValue();
            controller.setSupplierAccessoryDelay(newDelay);
        });

        dealerSpeedSlider.addChangeListener(e -> {
            int newDelay = dealerSpeedSlider.getValue();
            controller.setDealerDelay(newDelay);
        });

        frame.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                stopFactory();
            }
        });

        frame.setVisible(true);
    }

    private JSlider createSlider(int min, int max, int initial) {
        JSlider slider = new JSlider(min, max, initial);
        slider.setMajorTickSpacing((max - min) / 5);
        slider.setMinorTickSpacing((max - min) / 10);
        slider.setPaintTicks(true);
        slider.setPaintLabels(true);
        return slider;
    }

    private void startFactory() {
        if (!running) {
            running = true;
            controller.start();

            updateProducedCarsWorker = new SwingWorker<>() {
                @Override
                protected Void doInBackground() {
                    while (running) {
                        SwingUtilities.invokeLater(() ->
                                producedCarsLabel.setText("Produced Cars: " + controller.getProducedCars()));
                        try {
                            Thread.sleep(1000); // 1 секунда
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    return null;
                }
            };

            updateStorageStatusWorker = new SwingWorker<>() {
                @Override
                protected Void doInBackground() {
                    while (running) {
                        SwingUtilities.invokeLater(() ->
                                storageStatusLabel.setText("Storage Status: " + controller.getStorageStatus()));
                        try {
                            Thread.sleep(100); // 100 мс
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    return null;
                }
            };

            updateProducedCarsWorker.execute();
            updateStorageStatusWorker.execute();
        }
    }

    private void stopFactory() {
        if (running) {
            running = false;
            controller.stop();
            if (updateProducedCarsWorker != null) updateProducedCarsWorker.cancel(true);
            if (updateStorageStatusWorker != null) updateStorageStatusWorker.cancel(true);
        }
    }
}