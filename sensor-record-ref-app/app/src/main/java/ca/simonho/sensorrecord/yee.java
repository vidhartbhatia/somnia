package ca.simonho.sensorrecord;

import android.os.AsyncTask;
import android.util.Log;

import com.mollin.yapi.YeelightDevice;
import com.mollin.yapi.exception.YeelightResultErrorException;
import com.mollin.yapi.exception.YeelightSocketException;

class yee extends AsyncTask<String, Void, Void> {

    @Override
    protected Void doInBackground(String... strings) {
        YeelightDevice device = null;
        try {
            // Instantiate your device (with its IP)
            device = new YeelightDevice("192.168.43.108");
        } catch (YeelightSocketException e) {
            e.printStackTrace();
        }

        try {
            // Toggle the device power
            device.toggle();
        } catch (YeelightResultErrorException e) {
            e.printStackTrace();
        } catch (YeelightSocketException e) {
            e.printStackTrace();
        }

        return null;
    }
}