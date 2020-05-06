package ca.simonho.sensorrecord;

import android.app.Notification;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.SQLException;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.os.Process;
import android.os.RemoteException;
import android.util.Log;

import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;

import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class SensorService extends Service implements SensorEventListener {

    public static final String TAG = "SensorService";


    public static final int SCREEN_OFF_RECEIVER_DELAY = 100;
    public static final int WINDOW_SIZE_1_MIN = 60 * 10; // 1 minutes
    public static final int WINDOW_SIZE_6_MIN = 6* 60 * 10; // 6 minutes
    public static final int WINDOW_SIZE_10_MIN = 10 * 60 * 10; // 10 minutes
    public static final int WINDOW_SIZE_20_MIN = 20* 60 * 10; // 20 minutes
    public static final int WINDOW_SIZE_30_MIN = 30 * 60 * 10; // 20 minutes



    //This can't be set below 10ms due to Android/hardware limitations. Use 9 to get more accurate 10ms intervals
    final short POLL_FREQUENCY = 99; //in milliseconds

    private long lastUpdate = -1;
    long curTimeStamp;
    long curTime;

    private DescriptiveStatistics  accelX_1, accelY_1, accelZ_1;
    private DescriptiveStatistics  accelX_6, accelY_6, accelZ_6;
    private DescriptiveStatistics  accelX_10, accelY_10, accelZ_10;
    private DescriptiveStatistics  accelX_20, accelY_20, accelZ_20;
    private DescriptiveStatistics  accelX_30, accelY_30, accelZ_30;



    public ArrayList<Float> x_window;
    public ArrayList<Float> y_window;
    public ArrayList<Float> z_window;
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
            case "HIDE" :
                message.arg1 = 0;
                break;
            case "SHOW":
                message.arg1 = 1;
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
        double avg = sum/list.size();
        double asq = 0.0;
        for(float i:list){
            asq = asq + ((i - avg) * (i - avg));
        }
        double var = asq/(list.size()) ;
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

//        SensorManager.getRotationMatrix(rotationMatrix, null, gravityMatrix, magneticMatrix);

        curTime = event.timestamp; //in nanoseconds
        curTimeStamp = System.currentTimeMillis();

        // only allow one update every POLL_FREQUENCY (convert from ms to nano for comparison).
        if((curTime - lastUpdate) > POLL_FREQUENCY*1000000) {

            lastUpdate = curTime;

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

            }


            //insert into database in background thread

            try{
                Runnable insertHandler = new InsertHandler(curTimeStamp,curTime/1000000, accelerometerMatrix, accelerometerVarianceMatrix, gyroscopeMatrix,
                        gravityMatrix, magneticMatrix, rotationMatrix);
                executor.execute(insertHandler);
            } catch (SQLException e) {
                Log.e(TAG, "insertData: " + e.getMessage(), e);
            }
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();

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

        //Store the current sensor array values into THIS objects arrays, and db insert from this object
        public InsertHandler(long curTimeStamp, long curTime, float[] accelerometerMatrix, float[] accelerometerVarianceMatrix,
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
        }

        public void run() {
            dbHelper.insertDataTemp(Long.parseLong(dbHelper.getTempSubInfo("subNum")),
                    this.curTimeStamp,
                    this.curTime,
                    this.accelerometerMatrix,
                    this.accelerometerVarianceMatrix,
                    this.gyroscopeMatrix,
                    this.gravityMatrix,
                    this.magneticMatrix,
                    this.rotationMatrix);
        }
    }
}