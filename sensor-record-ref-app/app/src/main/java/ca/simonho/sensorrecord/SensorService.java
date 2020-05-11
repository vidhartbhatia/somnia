package ca.simonho.sensorrecord;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.res.AssetManager;
import android.database.SQLException;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.os.Process;
import android.os.RemoteException;
import android.support.v4.app.NotificationCompat;
import android.support.v4.app.NotificationManagerCompat;
import android.util.Log;
import android.widget.Toast;

import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import weka.classifiers.Classifier;
import weka.core.Attribute;
import weka.core.DenseInstance;
import weka.core.Instances;
import weka.core.Utils;

public class SensorService extends Service implements SensorEventListener {

    public static final String TAG = "SensorService";
    public static final String SLEEP_TAG = "SLEEP";
    private static final String CHANNEL_ID = "hello";

    private Classifier mClassifier = null;


    public static final int SCREEN_OFF_RECEIVER_DELAY = 100;

    public static final int WINDOW_SIZE_1_MIN = 60 * 10; // 1 minutes
    public static final int WINDOW_SIZE_6_MIN = 5 * 60 * 10; // 5 minutes
    public static final int WINDOW_SIZE_10_MIN = 10 * 60 * 10; // 10 minutes
    public static final int WINDOW_SIZE_20_MIN = 20 * 60 * 10; // 20 minutes
    public static final int WINDOW_SIZE_30_MIN = 30 * 60 * 10; // 20 minutes
    public static final int PREDICTED_WINDOW_SIZE = 7; // 7 minutes


    //This can't be set below 10ms due to Android/hardware limitations. Use 9 to get more accurate 10ms intervals
    final short POLL_FREQUENCY = 99; //in milliseconds

    private long lastUpdate = -1;
    private long lastUpdateMin = -1;
    long counter = 0;
    long sleep_time = 0;
    Calendar alarm;

    File sleep_file;


    long curTimeStamp;
    long curTime;

    private DescriptiveStatistics accelX_1, accelY_1, accelZ_1;
    private DescriptiveStatistics accelX_6, accelY_6, accelZ_6;
    private DescriptiveStatistics accelX_10, accelY_10, accelZ_10;
    private DescriptiveStatistics accelX_20, accelY_20, accelZ_20;
    private DescriptiveStatistics accelX_30, accelY_30, accelZ_30;


    public ArrayList<Float> x_window;
    public ArrayList<Float> y_window;
    public ArrayList<Float> z_window;
    public ArrayList<Integer> predicted_window;

    double x_sum = 0.0;
    double y_sum = 0.0;
    double z_sum = 0.0;

    private Messenger messageHandler;

    private SensorManager sensorManager = null;
    private WakeLock wakeLock = null;
    ExecutorService executor;
    DBHelper dbHelper;
    Sensor sensor;
    Sensor accelerometer;
    Sensor gyroscope;
    Sensor gravity;
    Sensor magnetic;

    float[] accelerometerMatrix = new float[3];
    float[] accelerometerVarianceMatrix = new float[3];
    float[] gyroscopeMatrix = new float[3];
    float[] gravityMatrix = new float[3];
    float[] magneticMatrix = new float[3];
    float[] rotationMatrix = new float[9];

    private void registerListener() {
        sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST);
        sensorManager.registerListener(this, gyroscope, SensorManager.SENSOR_DELAY_FASTEST);
        sensorManager.registerListener(this, gravity, SensorManager.SENSOR_DELAY_FASTEST);
        sensorManager.registerListener(this, magnetic, SensorManager.SENSOR_DELAY_FASTEST);
    }

    private void unregisterListener() {
        sensorManager.unregisterListener(this);
    }

    public BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            Log.i(TAG, "onReceive(" + intent + ")");

            if (!intent.getAction().equals(Intent.ACTION_SCREEN_OFF)) {
                return;
            }

            Runnable runnable = new Runnable() {
                public void run() {
                    Log.i(TAG, "Runnable executing...");
                    unregisterListener();
                    registerListener();
                }
            };

            new Handler().postDelayed(runnable, SCREEN_OFF_RECEIVER_DELAY);
        }
    };

    public void sendMessage(String state) {
        Message message = Message.obtain();
        switch (state) {
            case "HIDE":
                message.arg1 = 0;
                break;
            case "SHOW":
                message.arg1 = 1;
                break;
            case "UPDATE":
                message.arg1 = 2;
                break;
        }
        try {
            messageHandler.send(message);
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }

    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        //Safe not to implement
    }

//    public static double average(ArrayList<Float> list) {
//        double size = list.size();
//        double sum = 0.0;
//        for (Float l : list){
//            sum += l;
//        }
//        return(sum/size);

//    }

    public static double variance(ArrayList<Float> list, double sum) {
        // write code here
        double avg = sum / list.size();
        double asq = 0.0;
        for (float i : list) {
            asq = asq + ((i - avg) * (i - avg));
        }
        double var = asq / (list.size());
        return var;
    }

    public void onSensorChanged(SensorEvent event) {
        sensor = event.sensor;

        //Store sensor data
        int i = sensor.getType();
        if (i == MainActivity.TYPE_ACCELEROMETER) {
            accelerometerMatrix = event.values;
        } else if (i == MainActivity.TYPE_GYROSCOPE) {
            gyroscopeMatrix = event.values;
        } else if (i == MainActivity.TYPE_GRAVITY) {
            gravityMatrix = event.values;
        } else if (i == MainActivity.TYPE_MAGNETIC) {
            magneticMatrix = event.values;
        }

        // add to windows
        if (i == MainActivity.TYPE_ACCELEROMETER) {

            accelX_1.addValue(accelerometerMatrix[0]);
            accelY_1.addValue(accelerometerMatrix[1]);
            accelZ_1.addValue(accelerometerMatrix[2]);

            accelX_6.addValue(accelerometerMatrix[0]);
            accelY_6.addValue(accelerometerMatrix[1]);
            accelZ_6.addValue(accelerometerMatrix[2]);

            accelX_10.addValue(accelerometerMatrix[0]);
            accelY_10.addValue(accelerometerMatrix[1]);
            accelZ_10.addValue(accelerometerMatrix[2]);

            accelX_20.addValue(accelerometerMatrix[0]);
            accelY_20.addValue(accelerometerMatrix[1]);
            accelZ_20.addValue(accelerometerMatrix[2]);

            accelX_30.addValue(accelerometerMatrix[0]);
            accelY_30.addValue(accelerometerMatrix[1]);
            accelZ_30.addValue(accelerometerMatrix[2]);

            accelerometerVarianceMatrix[0] = (float) accelX_1.getVariance();
            accelerometerVarianceMatrix[1] = (float) accelY_1.getVariance();
            accelerometerVarianceMatrix[2] = (float) accelZ_1.getVariance();
        }

        curTime = event.timestamp; //in nanoseconds
        curTimeStamp = System.currentTimeMillis();


        // only allow one update every POLL_FREQUENCY (convert from ms to nano for comparison).
        if ((curTime - lastUpdate) > POLL_FREQUENCY * 1000000) {

            lastUpdate = curTime;
            counter++;


            if (counter > (60 * 10)) { // every minute


                counter = 0;

                // now spawn the model thread

                try {
                    Runnable modelHandler = new ModelTestHandler(curTimeStamp, curTime / 1000000, accelerometerMatrix, accelerometerVarianceMatrix, accelX_1,
                            accelY_1, accelZ_1, accelX_6, accelY_6, accelZ_6, accelX_10, accelY_10, accelZ_10, accelX_20, accelY_20, accelZ_20, accelX_30, accelY_30, accelZ_30);
                    executor.execute(modelHandler);
                } catch (SQLException e) {
                    Log.e(TAG, "modelTestError: " + e.getMessage(), e);
                }

            } else {

                //insert into database in background thread

                try {
                    Runnable insertHandler = new InsertHandler(curTimeStamp, curTime / 1000000, -1, accelerometerMatrix, accelerometerVarianceMatrix, gyroscopeMatrix,
                            gravityMatrix, magneticMatrix, rotationMatrix);
                    executor.execute(insertHandler);
                } catch (SQLException e) {
                    Log.e(TAG, "insertData: " + e.getMessage(), e);
                }
            }
        }
    }


    @Override
    public void onCreate() {
        super.onCreate();

        AssetManager assetManager = getAssets();
        try {
            mClassifier = (Classifier) weka.core.SerializationHelper.read(assetManager.open("somnia_final_sunday_model.model"));
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            // Weka "catch'em all!"
            e.printStackTrace();
        }
        Toast.makeText(this, "Model loaded, started logging", Toast.LENGTH_SHORT).show();
        Log.d(SLEEP_TAG, "loaded model: ");
        MainActivity.fallenAsleep = false;
        MainActivity.wokenUp = false;


        dbHelper = DBHelper.getInstance(getApplicationContext());
        accelX_1 = new DescriptiveStatistics();
        accelY_1 = new DescriptiveStatistics();
        accelZ_1 = new DescriptiveStatistics();

        accelX_6 = new DescriptiveStatistics();
        accelY_6 = new DescriptiveStatistics();
        accelZ_6 = new DescriptiveStatistics();

        accelX_10 = new DescriptiveStatistics();
        accelY_10 = new DescriptiveStatistics();
        accelZ_10 = new DescriptiveStatistics();

        accelX_20 = new DescriptiveStatistics();
        accelY_20 = new DescriptiveStatistics();
        accelZ_20 = new DescriptiveStatistics();

        accelX_30 = new DescriptiveStatistics();
        accelY_30 = new DescriptiveStatistics();
        accelZ_30 = new DescriptiveStatistics();


        accelX_1.setWindowSize(WINDOW_SIZE_1_MIN);
        accelY_1.setWindowSize(WINDOW_SIZE_1_MIN);
        accelZ_1.setWindowSize(WINDOW_SIZE_1_MIN);

        accelX_6.setWindowSize(WINDOW_SIZE_6_MIN);
        accelY_6.setWindowSize(WINDOW_SIZE_6_MIN);
        accelZ_6.setWindowSize(WINDOW_SIZE_6_MIN);

        accelX_10.setWindowSize(WINDOW_SIZE_10_MIN);
        accelY_10.setWindowSize(WINDOW_SIZE_10_MIN);
        accelZ_10.setWindowSize(WINDOW_SIZE_10_MIN);

        accelX_20.setWindowSize(WINDOW_SIZE_20_MIN);
        accelY_20.setWindowSize(WINDOW_SIZE_20_MIN);
        accelZ_20.setWindowSize(WINDOW_SIZE_20_MIN);

        accelX_30.setWindowSize(WINDOW_SIZE_30_MIN);
        accelY_30.setWindowSize(WINDOW_SIZE_30_MIN);
        accelZ_30.setWindowSize(WINDOW_SIZE_30_MIN);

        alarm = Calendar.getInstance();
        alarm.set(Calendar.HOUR_OF_DAY, 4);
        alarm.set(Calendar.MINUTE, 20);
        alarm.set(Calendar.SECOND, 0);

        String pathToExternalStorage = Environment.getExternalStorageDirectory().toString();
        File exportDir = new File(pathToExternalStorage, "/SensorRecord");
        sleep_file = new File(exportDir, "sleep_data.txt");

        if (!sleep_file.exists()) {
            try {
                sleep_file.createNewFile();
            } catch (IOException ioe) {
                ioe.printStackTrace();
            }
        }


        sensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        accelerometer = sensorManager.getDefaultSensor(MainActivity.TYPE_ACCELEROMETER);
        gyroscope = sensorManager.getDefaultSensor(MainActivity.TYPE_GYROSCOPE);
        gravity = sensorManager.getDefaultSensor(MainActivity.TYPE_GRAVITY);
        magnetic = sensorManager.getDefaultSensor(MainActivity.TYPE_MAGNETIC);

        PowerManager manager = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wakeLock = manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, TAG);

        registerReceiver(receiver, new IntentFilter(Intent.ACTION_SCREEN_OFF));

        //Executor service for DB inserts
        executor = Executors.newSingleThreadExecutor();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        // init windows
        x_window = new ArrayList<>();
        y_window = new ArrayList<>();
        z_window = new ArrayList<>();
        predicted_window = new ArrayList<>();
        startForeground(Process.myPid(), new Notification());


        registerListener();
        wakeLock.acquire();

        //Message handler for progress dialog
        Bundle extras = intent.getExtras();
        messageHandler = (Messenger) extras.get("MESSENGER");

        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        //Show dialog
        sendMessage("SHOW");

        //Unregister receiver and listener prior to executor shutdown
        unregisterReceiver(receiver);
        unregisterListener();

        //Prevent new tasks from being added to thread
        executor.shutdown();
        Log.d(TAG, "Executor shutdown is called");

        //Create new thread to wait for executor to clear queue and wait for termination
        new Thread(new Runnable() {

            public void run() {
                try {
                    //Wait for all tasks to finish before we proceed
                    while (!executor.awaitTermination(1, TimeUnit.SECONDS)) {
                        Log.i(TAG, "Waiting for current tasks to finish");
                    }
                    Log.i(TAG, "No queue to clear");
                } catch (InterruptedException e) {
                    Log.e(TAG, "Exception caught while waiting for finishing executor tasks");
                    executor.shutdownNow();
                    Thread.currentThread().interrupt();
                }

                if (executor.isTerminated()) {
                    //Stop everything else once the task queue is clear
                    wakeLock.release();
                    stopForeground(true);

                    //Dismiss progress dialog
                    sendMessage("HIDE");
                }
            }
        }).start();
    }

    class InsertHandler implements Runnable {
        final long curTimeStamp;
        final long curTime;
        final float[] accelerometerMatrix;
        final float[] accelerometerVarianceMatrix;
        final float[] gyroscopeMatrix;
        final float[] gravityMatrix;
        final float[] magneticMatrix;
        final float[] rotationMatrix;
        final int phase;

        //Store the current sensor array values into THIS objects arrays, and db insert from this object
        public InsertHandler(long curTimeStamp, long curTime, int phase, float[] accelerometerMatrix, float[] accelerometerVarianceMatrix,
                             float[] gyroscopeMatrix, float[] gravityMatrix,
                             float[] magneticMatrix, float[] rotationMatrix) {
            this.curTimeStamp = curTimeStamp;
            this.curTime = curTime;
            this.accelerometerMatrix = accelerometerMatrix;
            this.accelerometerVarianceMatrix = accelerometerVarianceMatrix;
            this.gyroscopeMatrix = gyroscopeMatrix;
            this.gravityMatrix = gravityMatrix;
            this.magneticMatrix = magneticMatrix;
            this.rotationMatrix = rotationMatrix;
            this.phase = phase;
        }

        public void run() {

            // do the weka stuff here then insert into DB


            dbHelper.insertDataTemp(Long.parseLong(dbHelper.getTempSubInfo("subNum")),
                    this.curTimeStamp,
                    this.curTime,
                    this.phase,
                    this.accelerometerMatrix,
                    this.accelerometerVarianceMatrix,
                    this.gyroscopeMatrix,
                    this.gravityMatrix,
                    this.magneticMatrix,
                    this.rotationMatrix);
        }
    }


    class ModelTestHandler implements Runnable {
        final long curTimeStamp;
        final long curTime;
        final float[] accelerometerVarianceMatrix;
        final float[] accelerometerMatrix;
        final DescriptiveStatistics accelX_1;
        final DescriptiveStatistics accelY_1;
        final DescriptiveStatistics accelZ_1;
        final DescriptiveStatistics accelX_6, accelY_6, accelZ_6;
        final DescriptiveStatistics accelX_10, accelY_10, accelZ_10;
        final DescriptiveStatistics accelX_20, accelY_20, accelZ_20;
        final DescriptiveStatistics accelX_30, accelY_30, accelZ_30;


        //Store the current sensor array values into THIS objects arrays, and db insert from this object
        public ModelTestHandler(long curTimeStamp, long curTime, float[] accelerometerMatrix, float[] accelerometerVarianceMatrix,
                                DescriptiveStatistics accelX_1,
                                DescriptiveStatistics accelY_1,
                                DescriptiveStatistics accelZ_1,
                                DescriptiveStatistics accelX_6, DescriptiveStatistics accelY_6, DescriptiveStatistics accelZ_6,
                                DescriptiveStatistics accelX_10, DescriptiveStatistics accelY_10, DescriptiveStatistics accelZ_10,
                                DescriptiveStatistics accelX_20, DescriptiveStatistics accelY_20, DescriptiveStatistics accelZ_20,
                                DescriptiveStatistics accelX_30, DescriptiveStatistics accelY_30, DescriptiveStatistics accelZ_30
        ) {
            this.curTimeStamp = curTimeStamp;
            this.curTime = curTime;
            this.accelerometerMatrix = accelerometerMatrix;

            this.accelerometerVarianceMatrix = accelerometerVarianceMatrix;
            this.accelX_1 = accelX_1;
            this.accelY_1 = accelY_1;
            this.accelZ_1 = accelZ_1;

            this.accelX_6 = accelX_6;
            this.accelY_6 = accelY_6;
            this.accelZ_6 = accelZ_6;

            this.accelX_10 = accelX_10;
            this.accelY_10 = accelY_10;
            this.accelZ_10 = accelZ_10;

            this.accelX_20 = accelX_20;
            this.accelY_20 = accelY_20;
            this.accelZ_20 = accelZ_20;

            this.accelX_30 = accelX_30;
            this.accelY_30 = accelY_30;
            this.accelZ_30 = accelZ_30;


        }

        public void run() {

            // do the weka stuff here then insert into DB?

            // create instances
            final List<String> classes = new ArrayList<String>() {
                {
                    add("Deep"); // cls nr 1
                    add("Light"); // cls nr 2
//                    add("REM"); // cls nr 3
//                    add("Awake"); // cls nr 4

                }
            };
//            Attribute attr1 = new Attribute("accX_means1");
//            Attribute attr2 = new Attribute("accY_means1");
//            Attribute attr3 = new Attribute("accZ_means1");
//            Attribute attr4 = new Attribute("accX_medians1");
//            Attribute attr5 = new Attribute("accY_medians1");
//            Attribute attr6 = new Attribute("accZ_medians1");
//            Attribute attr7 = new Attribute("accX_maxes1");
//            Attribute attr8 = new Attribute("accY_maxes1");
//            Attribute attr9 = new Attribute("accZ_maxes1");
//            Attribute attr10 = new Attribute("accX_mins1");
//            Attribute attr11 = new Attribute("accY_mins1");
//            Attribute attr12 = new Attribute("accZ_mins1");
//            Attribute attr13 = new Attribute("accX_variances1");
//            Attribute attr14 = new Attribute("accY_variances1");
//            Attribute attr15 = new Attribute("accZ_variances1");

//            Attribute attr16 = new Attribute("accX_means5");
//            Attribute attr17 = new Attribute("accY_means5");
//            Attribute attr18 = new Attribute("accZ_means5");
//            Attribute attr19 = new Attribute("accX_medians5");
//            Attribute attr20 = new Attribute("accY_medians5");
//            Attribute attr21 = new Attribute("accZ_medians5");
//            Attribute attr22 = new Attribute("accX_maxes5");
//            Attribute attr23 = new Attribute("accY_maxes5");
//            Attribute attr24 = new Attribute("accZ_maxes5");
//            Attribute attr25 = new Attribute("accX_mins5");
//            Attribute attr26 = new Attribute("accY_mins5");
//            Attribute attr27 = new Attribute("accZ_mins5");
            Attribute attr28 = new Attribute("accX_variances5");
            Attribute attr29 = new Attribute("accY_variances5");
            Attribute attr30 = new Attribute("accZ_variances5");

            Attribute attr31 = new Attribute("aggregate5");
//            Attribute attr32 = new Attribute("accY_means10");
//            Attribute attr33 = new Attribute("accZ_means10");
//            Attribute attr34 = new Attribute("accX_medians10");
//            Attribute attr35 = new Attribute("accY_medians10");
//            Attribute attr36 = new Attribute("accZ_medians10");
//            Attribute attr37 = new Attribute("accX_maxes10");
//            Attribute attr38 = new Attribute("accY_maxes10");
//            Attribute attr39 = new Attribute("accZ_maxes10");
//            Attribute attr40 = new Attribute("accX_mins10");
//            Attribute attr41 = new Attribute("accY_mins10");
//            Attribute attr42 = new Attribute("accZ_mins10");
            Attribute attr43 = new Attribute("accX_variances10");
            Attribute attr44 = new Attribute("accY_variances10");
            Attribute attr45 = new Attribute("accZ_variances10");


            Attribute attr46 = new Attribute("aggregate10");
//            Attribute attr47 = new Attribute("accY_means20");
//            Attribute attr48 = new Attribute("accZ_means20");
//            Attribute attr49 = new Attribute("accX_medians20");
//            Attribute attr50 = new Attribute("accY_medians20");
//            Attribute attr51 = new Attribute("accZ_medians20");
//            Attribute attr52 = new Attribute("accX_maxes20");
//            Attribute attr53 = new Attribute("accY_maxes20");
//            Attribute attr54 = new Attribute("accZ_maxes20");
//            Attribute attr55 = new Attribute("accX_mins20");
//            Attribute attr56 = new Attribute("accY_mins20");
//            Attribute attr57 = new Attribute("accZ_mins20");
            Attribute attr58 = new Attribute("accX_variances20");
            Attribute attr59 = new Attribute("accY_variances20");
            Attribute attr60 = new Attribute("accZ_variances20");


            Attribute attr61 = new Attribute("aggregate20");
//            Attribute attr62 = new Attribute("accY_means30");
//            Attribute attr63 = new Attribute("accZ_means30");
//            Attribute attr64 = new Attribute("accX_medians30");
//            Attribute attr65 = new Attribute("accY_medians30");
//            Attribute attr66 = new Attribute("accZ_medians30");
//            Attribute attr67 = new Attribute("accX_maxes30");
//            Attribute attr68 = new Attribute("accY_maxes30");
//            Attribute attr69 = new Attribute("accZ_maxes30");
//            Attribute attr70 = new Attribute("accX_mins30");
//            Attribute attr71 = new Attribute("accY_mins30");
            Attribute attr72 = new Attribute("aggregate30");
            Attribute attr73 = new Attribute("accX_variances30");
            Attribute attr74 = new Attribute("accY_variances30");
            Attribute attr75 = new Attribute("accZ_variances30");


            // at the end
            Attribute attributeClass = new Attribute("@@class@@", classes);
            Attribute attr76 = attributeClass;

            ArrayList<Attribute> attributes = new ArrayList<Attribute>();
//            attributes.add(attr1);
//            attributes.add(attr2);
//            attributes.add(attr3);
//            attributes.add(attr4);
//            attributes.add(attr5);
//            attributes.add(attr6);
//            attributes.add(attr7);
//            attributes.add(attr8);
//            attributes.add(attr9);
//            attributes.add(attr10);
//            attributes.add(attr11);
//            attributes.add(attr12);
//            attributes.add(attr13);
//            attributes.add(attr14);
//            attributes.add(attr15);
//            attributes.add(attr16);
//            attributes.add(attr17);
//            attributes.add(attr18);
//            attributes.add(attr19);
//            attributes.add(attr20);
//            attributes.add(attr21);
//            attributes.add(attr22);
//            attributes.add(attr23);
//            attributes.add(attr24);
//            attributes.add(attr25);
//            attributes.add(attr26);
//            attributes.add(attr27);
            attributes.add(attr28);
            attributes.add(attr29);
            attributes.add(attr30);
            attributes.add(attr31);
//            attributes.add(attr32);
//            attributes.add(attr33);
//            attributes.add(attr34);
//            attributes.add(attr35);
//            attributes.add(attr36);
//            attributes.add(attr37);
//            attributes.add(attr38);
//            attributes.add(attr39);
//            attributes.add(attr40);
//            attributes.add(attr41);
//            attributes.add(attr42);
            attributes.add(attr43);
            attributes.add(attr44);
            attributes.add(attr45);
            attributes.add(attr46);
//            attributes.add(attr47);
//            attributes.add(attr48);
//            attributes.add(attr49);
//            attributes.add(attr50);
//            attributes.add(attr51);
//            attributes.add(attr52);
//            attributes.add(attr53);
//            attributes.add(attr54);
//            attributes.add(attr55);
//            attributes.add(attr56);
//            attributes.add(attr57);
            attributes.add(attr58);
            attributes.add(attr59);
            attributes.add(attr60);
            attributes.add(attr61);
//            attributes.add(attr62);
//            attributes.add(attr63);
//            attributes.add(attr64);
//            attributes.add(attr65);
//            attributes.add(attr66);
//            attributes.add(attr67);
//            attributes.add(attr68);
//            attributes.add(attr69);
//            attributes.add(attr70);
//            attributes.add(attr71);
            attributes.add(attr73);
            attributes.add(attr74);
            attributes.add(attr75);
            attributes.add(attr72);


            // the clases
            attributes.add(attr76);


            // unpredicted data sets (reference to sample structure for new instances)
            Instances dataUnpredicted = new Instances("TestInstances",
                    attributes, 1);
            // last feature is target variable
            dataUnpredicted.setClassIndex(dataUnpredicted.numAttributes() - 1);


            // add data

            DenseInstance newInstance = new DenseInstance(dataUnpredicted.numAttributes()) {
                {
//                    setValue(attr1, accelX_1.getMean());
//                    setValue(attr2, accelY_1.getMean());
//                    setValue(attr3, accelZ_1.getMean());
//                    setValue(attr4, accelX_1.getPercentile(50));
//                    setValue(attr5, accelY_1.getPercentile(50));
//                    setValue(attr6, accelZ_1.getPercentile(50));
//                    setValue(attr7, accelX_1.getMax());
//                    setValue(attr8, accelY_1.getMax());
//                    setValue(attr9, accelZ_1.getMax());
//                    setValue(attr10, accelX_1.getMin());
//                    setValue(attr11, accelY_1.getMin());
//                    setValue(attr12, accelZ_1.getMin());
//                    setValue(attr13, accelX_1.getVariance());
//                    setValue(attr14, accelY_1.getVariance());
//                    setValue(attr15, accelZ_1.getVariance());

//                    setValue(attr16, accelX_6.getMean());
//                    setValue(attr17, accelY_6.getMean());
//                    setValue(attr18, accelZ_6.getMean());
//                    setValue(attr19, accelX_6.getPercentile(50));
//                    setValue(attr20, accelY_6.getPercentile(50));
//                    setValue(attr21, accelZ_6.getPercentile(50));
//                    setValue(attr22, accelX_6.getMax());
//                    setValue(attr23, accelY_6.getMax());
//                    setValue(attr24, accelZ_6.getMax());
//                    setValue(attr25, accelX_6.getMin());
//                    setValue(attr26, accelY_6.getMin());
//                    setValue(attr27, accelZ_6.getMin());
                    setValue(attr28, accelX_6.getVariance());
                    setValue(attr29, accelY_6.getVariance());
                    setValue(attr30, accelZ_6.getVariance());

                    setValue(attr31, accelX_6.getVariance() + accelY_6.getVariance() + accelZ_6.getVariance());
//                    setValue(attr32, accelY_10.getMean());
//                    setValue(attr33, accelZ_10.getMean());
//                    setValue(attr34, accelX_10.getPercentile(50));
//                    setValue(attr35, accelY_10.getPercentile(50));
//                    setValue(attr36, accelZ_10.getPercentile(50));
//                    setValue(attr37, accelX_10.getMax());
//                    setValue(attr38, accelY_10.getMax());
//                    setValue(attr39, accelZ_10.getMax());
//                    setValue(attr40, accelX_10.getMin());
//                    setValue(attr41, accelY_10.getMin());
//                    setValue(attr42, accelZ_10.getMin());
                    setValue(attr43, accelX_10.getVariance());
                    setValue(attr44, accelY_10.getVariance());
                    setValue(attr45, accelZ_10.getVariance());

                    setValue(attr46, accelX_10.getVariance() + accelY_10.getVariance() + accelZ_10.getVariance());
//                    setValue(attr47, accelY_20.getMean());
//                    setValue(attr48, accelZ_20.getMean());
//                    setValue(attr49, accelX_20.getPercentile(50));
//                    setValue(attr50, accelY_20.getPercentile(50));
//                    setValue(attr51, accelZ_20.getPercentile(50));
//                    setValue(attr52, accelX_20.getMax());
//                    setValue(attr53, accelY_20.getMax());
//                    setValue(attr54, accelZ_20.getMax());
//                    setValue(attr55, accelX_20.getMin());
//                    setValue(attr56, accelY_20.getMin());
//                    setValue(attr57, accelZ_20.getMin());
                    setValue(attr58, accelX_20.getVariance());
                    setValue(attr59, accelY_20.getVariance());
                    setValue(attr60, accelZ_20.getVariance());

                    setValue(attr61, accelX_20.getVariance() + accelY_20.getVariance() + accelZ_20.getVariance());
//                    setValue(attr62, accelY_30.getMean());
//                    setValue(attr63, accelZ_30.getMean());
//                    setValue(attr64, accelX_30.getPercentile(50));
//                    setValue(attr65, accelY_30.getPercentile(50));
//                    setValue(attr66, accelZ_30.getPercentile(50));
//                    setValue(attr67, accelX_30.getMax());
//                    setValue(attr68, accelY_30.getMax());
//                    setValue(attr69, accelZ_30.getMax());
//                    setValue(attr70, accelX_30.getMin());
//                    setValue(attr71, accelY_30.getMin());
                    setValue(attr72, accelX_30.getVariance() + accelY_30.getVariance() + accelZ_30.getVariance());
                    setValue(attr73, accelX_30.getVariance());
                    setValue(attr74, accelY_30.getVariance());
                    setValue(attr75, accelZ_30.getVariance());

                }
            };

            // reference to dataset
            newInstance.setDataset(dataUnpredicted);

            // predict new sample
            try {
                double result = mClassifier.classifyInstance(newInstance);
                int phase = new Double(result).intValue();
                String className = classes.get(phase);
                String msg = "predicted: " + className + " int:" + phase;


                String time = new SimpleDateFormat("HH:mm:ss yyyy-MM-dd ", Locale.US).format(new Date(curTimeStamp));
                predicted_window.add(phase);
                if (predicted_window.size() >= PREDICTED_WINDOW_SIZE) {
                    predicted_window.remove(0);

                    if (!MainActivity.fallenAsleep) {
                        // hasnt fallen asleep yet
                        int num_light = 0;
                        int num_deep = 0;
                        for (int sleep : predicted_window) {
                            if (sleep == 1) {
                                num_light++;
                            } else {
                                num_deep++;
                            }
                        }
                        if (num_deep > num_light) {
                            // FALLEN asleep
                            MainActivity.fallenAsleep = true;
                            sleep_time = curTimeStamp;
                            Log.d(SLEEP_TAG, "Fallen asleep at: " + time);

                            FileOutputStream fileOutputStream = new FileOutputStream(sleep_file, true);
                            OutputStreamWriter writer = new OutputStreamWriter(fileOutputStream);
                            writer.append("Time went to sleep: " + time +" \n");
                            writer.close();
                            fileOutputStream.close();


                        }


                    }
                    if (!MainActivity.wokenUp) {
                        Calendar cur = Calendar.getInstance();
                        if (cur.after(alarm)) {
                            Log.d(SLEEP_TAG, "Forced alarm at " + time);
                            FileOutputStream fileOutputStream = new FileOutputStream(sleep_file, true);
                            OutputStreamWriter writer = new OutputStreamWriter(fileOutputStream);
                            writer.append("FOrced alarm Will try to wake your ass at: " + time +" \n");
                            writer.close();
                            fileOutputStream.close();
                            MainActivity.wokenUp = true;
                        }
                        cur.add(Calendar.MINUTE, 30);
                        if (alarm.before(cur)) {

                            int num_light = 0;
                            int num_deep = 0;
                            for (int sleep : predicted_window) {
                                if (sleep == 1) {
                                    num_light++;
                                } else {
                                    num_deep++;
                                }
                            }
                            if (num_light > num_deep) {
                                // Light sleep in alarm rang;
                                Log.d(SLEEP_TAG, "Wake up alarm at " + time);
                                FileOutputStream fileOutputStream = new FileOutputStream(sleep_file, true);
                                OutputStreamWriter writer = new OutputStreamWriter(fileOutputStream);
                                writer.append("smart alarm Will try to wake your ass at: " + time +" \n");
                                writer.close();
                                fileOutputStream.close();

                                MainActivity.wokenUp = true;


                            }
                        }

                    }

                }


                Log.d(SLEEP_TAG, msg);
                //insert into database in background thread
                try {
                    Runnable insertHandler = new InsertHandler(curTimeStamp, curTime, phase, accelerometerMatrix, accelerometerVarianceMatrix, gyroscopeMatrix,
                            gravityMatrix, magneticMatrix, rotationMatrix);
                    executor.execute(insertHandler);
                } catch (SQLException e) {
                    Log.e(TAG, "insertData: " + e.getMessage(), e);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void createNotificationChannel() {
        // Create the NotificationChannel, but only on API 26+ because
        // the NotificationChannel class is new and not in the support library
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            CharSequence name = "notifications";
            String description = "Notify";
            int importance = NotificationManager.IMPORTANCE_DEFAULT;
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, name, importance);
            channel.setDescription(description);
            // Register the channel with the system; you can't change the importance
            // or other notification behaviors after this
            NotificationManager notificationManager = getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);
        }
    }
}


// mean median min max variance
// window sizes 1 6 10 20 30 minutes


//                x_window.add(accelerometerMatrix[0]);
//                x_sum += accelerometerMatrix[0];
//                y_window.add(accelerometerMatrix[1]);
//                y_sum += accelerometerMatrix[1];
//                z_window.add(accelerometerMatrix[2]);
//                z_sum += accelerometerMatrix[2];
//
//                if (x_window.size() >= WINDOW_SIZE) {
//                    x_sum -= x_window.get(0);
//                    y_sum -= y_window.get(0);
//                    z_sum -= z_window.get(0);
//
//                    x_window.remove(0);
//                    y_window.remove(0);
//                    z_window.remove(0);
//                }
//
//                accelerometerVarianceMatrix[0] = (float)(variance(x_window, x_sum));
//                accelerometerVarianceMatrix[1] = (float)(variance(y_window, y_sum));
//                accelerometerVarianceMatrix[2] = (float)(variance(z_window, z_sum));