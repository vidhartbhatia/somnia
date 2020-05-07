package ca.simonho.sensorrecord;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.SQLException;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.os.Handler;
import android.os.Message;
import android.util.Log;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import au.com.bytecode.opencsv.CSVWriter;

public class DBHelper extends SQLiteOpenHelper {
    public static final String TAG = "DBHelper";

    SQLiteDatabase db;
    CSVWriter csvWrite;
    Cursor curCSV;
    static Handler messageHandler;
    private static DBHelper sInstance;

    //Constants for db name and version
    public static final String DATABASE_NAME = "sensorRecord.db";
    private static final int DATABASE_VERSION = 1;
    public String databasePath = "";

    //Constants for identifying subject table and fields
    public static final String SUBJECTS_TABLE_NAME = "subjects";
    public static final String SUBJECTS_TABLE_NAME_TEMP = "subjects_temp";
    public static final String SUBJECTS_ID = "id";
    public static final String SUBJECTS_DATE = "date";
    public static final String SUBJECTS_START_TIME = "starttime";

    //Subject table structure
    private static final String SUBJECTS_TABLE_STRUCTURE =
            " (" + SUBJECTS_ID + " INTEGER PRIMARY KEY, " +
                    SUBJECTS_DATE + " TEXT default CURRENT_TIMESTAMP, " +
                    SUBJECTS_START_TIME + " INTEGER " +
                    ")";

    //SQL to create subject table
    private static final String SUBJECTS_TABLE_CREATE =
            "CREATE TABLE " + SUBJECTS_TABLE_NAME + SUBJECTS_TABLE_STRUCTURE;

    //SQL to create TEMP subject table
    private static final String SUBJECTS_TABLE_CREATE_TEMP =
            "CREATE TEMP TABLE " + SUBJECTS_TABLE_NAME_TEMP + SUBJECTS_TABLE_STRUCTURE;

    //Constants for identifying data table and fields
    public static final String DATA_TABLE_NAME = "data";
    public static final String DATA_TABLE_NAME_TEMP = "data_temp";
    public static final String DATA_SUBJECT = "id";
    public static final String DATA_TIME_STAMP = "time_stamp";
    public static final String DATA_TIME = "time";
    public static final String DATA_ACCX = "accX";
    public static final String DATA_ACCY = "accY";
    public static final String DATA_ACCZ = "accZ";
    public static final String DATA_ACCX_V = "accX_V";
    public static final String DATA_ACCY_V = "accY_V";
    public static final String DATA_ACCZ_V = "accZ_V";
    public static final String DATA_GYROX = "gyroX";
    public static final String DATA_GYROY = "gyroY";
    public static final String DATA_GYROZ = "gyroZ";
    public static final String DATA_GRAVX = "gravX";
    public static final String DATA_GRAVY = "gravY";
    public static final String DATA_GRAVZ = "gravZ";
    public static final String DATA_MAGX = "magX";
    public static final String DATA_MAGY = "magY";
    public static final String DATA_MAGZ = "magZ";
    public static final String DATA_PHASE = "phase";

    public static final String DATA_ROT1 = "rot1";
    public static final String DATA_ROT2 = "rot2";
    public static final String DATA_ROT3 = "rot3";
    public static final String DATA_ROT4 = "rot4";
    public static final String DATA_ROT5 = "rot5";
    public static final String DATA_ROT6 = "rot6";
    public static final String DATA_ROT7 = "rot7";
    public static final String DATA_ROT8 = "rot8";
    public static final String DATA_ROT9 = "rot9";

    //Data table structure
    private static final String DATA_TABLE_STRUCTURE =
            " (" + DATA_SUBJECT + " INTEGER, " +
                    DATA_TIME_STAMP + " INTEGER, " +
                    DATA_PHASE + " INTEGER, " +
                    DATA_TIME + " INTEGER, " +
                    DATA_ACCX + " REAL, " +
                    DATA_ACCY + " REAL, " +
                    DATA_ACCZ + " REAL, " +
                    DATA_ACCX_V + " REAL, " +
                    DATA_ACCY_V+ " REAL, " +
                    DATA_ACCZ_V+ " REAL, " +
                    DATA_GYROX + " REAL, " +
                    DATA_GYROY + " REAL, " +
                    DATA_GYROZ + " REAL, " +
                    DATA_GRAVX + " REAL, " +
                    DATA_GRAVY + " REAL, " +
                    DATA_GRAVZ + " REAL, " +
                    DATA_MAGX + " REAL, " +
                    DATA_MAGY + " REAL, " +
                    DATA_MAGZ + " REAL, " +

                    "FOREIGN KEY(" + DATA_SUBJECT + ") REFERENCES " + SUBJECTS_TABLE_NAME + "(" + SUBJECTS_ID + ")" +
                    ")";

//    DATA_ROT1 + " REAL, " +
//    DATA_ROT2 + " REAL, " +
//    DATA_ROT3 + " REAL, " +
//    DATA_ROT4 + " REAL, " +
//    DATA_ROT5 + " REAL, " +
//    DATA_ROT6 + " REAL, " +
//    DATA_ROT7 + " REAL, " +
//    DATA_ROT8 + " REAL, " +
//    DATA_ROT9 + " REAL, " +

    //SQL to create data table
    private static final String DATA_TABLE_CREATE =
            "CREATE TABLE " + DATA_TABLE_NAME + DATA_TABLE_STRUCTURE;

    //SQL to create TEMP data table
    private static final String DATA_TABLE_CREATE_TEMP =
            "CREATE TEMP TABLE " + DATA_TABLE_NAME_TEMP + DATA_TABLE_STRUCTURE;

    /**
     The static getInstance() method ensures that only one DatabaseHelper will ever exist at any given time.
     If the sInstance object has not been initialized, one will be created.
     If one has already been created then it will simply be returned.
     You should not initialize your helper object using with new DatabaseHelper(context)!
     Instead, always use DatabaseHelper.getInstance(context), as it guarantees that only
     one database helper will exist across the entire application’s lifecycle.
     */
    public static synchronized DBHelper getInstance(Context context) {

        // Use the application context, which will ensure that you
        // don't accidentally leak an Activity's context.
        // See this article for more information: http://bit.ly/6LRzfx
        if (sInstance == null) {
            sInstance = new DBHelper(context.getApplicationContext());
            Log.d(TAG, "New DBHelper created");
        }

        return sInstance;
    }

    public static synchronized DBHelper getInstance(Context context, Handler handler) {

        // Use the application context, which will ensure that you
        // don't accidentally leak an Activity's context.
        // See this article for more information: http://bit.ly/6LRzfx
        if (sInstance == null) {
            sInstance = new DBHelper(context.getApplicationContext());
            Log.d(TAG, "New DBHelper created");
        }

        messageHandler = handler;
        return sInstance;
    }

    /**
     * Constructor should be private to prevent direct instantiation.
     * make call to static method "getInstance()" instead.
     */
    private DBHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);

        databasePath = context.getDatabasePath(DATABASE_NAME).getPath();
        db = this.getWritableDatabase();
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        Log.d(TAG, "onCreate called");

        //Create persistent tables
        db.execSQL(SUBJECTS_TABLE_CREATE);
        db.execSQL(DATA_TABLE_CREATE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        Log.d(TAG, "onUpgrade called");

        //Drop persistent tables
        db.execSQL("DROP TABLE IF EXISTS " + SUBJECTS_TABLE_NAME);
        db.execSQL("DROP TABLE IF EXISTS " + DATA_TABLE_NAME);

        //Recreate tables
        onCreate(db);
    }

    @Override
    public void onOpen(SQLiteDatabase db) {
        super.onOpen(db);
        createTempTables(db);
    }

    public void closeDB(){
        if (db != null){
            Log.d(TAG, "closeDB: closing db");
            db.close();
            db = null;
        }

        if (sInstance != null){
            Log.d(TAG, "closeDB: closing DBHelper instance");
            sInstance.close();
            sInstance = null;
        }
    }

    public void createTempTables(SQLiteDatabase db){
        Log.d(TAG, "Creating Temp tables");

        //Create temp tables
        db.execSQL(SUBJECTS_TABLE_CREATE_TEMP);
        db.execSQL(DATA_TABLE_CREATE_TEMP);
    }

    public boolean checkSubjectExists(Long subNum) throws SQLException {
        //Check if subject exists in persistent subject table
        String query = "SELECT * FROM " + SUBJECTS_TABLE_NAME + " WHERE " + SUBJECTS_ID + "=" + subNum;

        Cursor c = db.rawQuery(query, null);
        boolean exists = (c.getCount() > 0);
        c.close();

        return exists;
    }

    public boolean checkSubjectDataExists(Long subNum) throws SQLException {
        //Check if sensor data, for this subject, exists in the temp data table
        String query = "SELECT * FROM " + DATA_TABLE_NAME_TEMP + " WHERE " + DATA_SUBJECT + "=" + subNum;

        Cursor c = db.rawQuery(query, null);
        boolean exists = (c.getCount() > 0);
        c.close();

        return exists;
    }

    public void insertSubjectTemp(Long subNum, String date, long time) throws SQLException {

        ContentValues subjectData = new ContentValues();
        subjectData.put(SUBJECTS_ID, subNum);
        subjectData.put(SUBJECTS_DATE, date);
        subjectData.put(SUBJECTS_START_TIME, time);

        db.insertOrThrow(SUBJECTS_TABLE_NAME_TEMP, null, subjectData);
    }

    public void setStartTime(Long subNum, long time) throws SQLException {
        ContentValues cv = new ContentValues();
        cv.put(SUBJECTS_START_TIME, time);
        db.update(SUBJECTS_TABLE_NAME_TEMP, cv, SUBJECTS_ID + " = " + subNum, null);
    }

    public String getTempSubInfo(String type) throws SQLException {
        String result = "";

        String query = "SELECT * FROM " + SUBJECTS_TABLE_NAME_TEMP;
        Cursor c = db.rawQuery(query, null);

        if(c.getCount() > 0){
            c.moveToFirst();
            switch(type){
                case "subNum":
                    result = c.getString(c.getColumnIndex(SUBJECTS_ID));
                    break;
                case "date":
                    result = c.getString(c.getColumnIndex(SUBJECTS_DATE));
                    break;
                case "time":
                    result = c.getString(c.getColumnIndex(SUBJECTS_START_TIME));
                    break;
            }
        }
        c.close();

        return result;
    }

    public void deleteSubject() throws SQLException {
        //Delete subject rows from temp subject and data tables. Table is not removed.
        db.delete(SUBJECTS_TABLE_NAME_TEMP, null, null);
        db.delete(DATA_TABLE_NAME_TEMP, null,null);
    }

    public void insertDataTemp(Long subNum, long time_stamp, long time, int phase,
                              float[] acc,
                               float[] acc_v,
                               float[] gyro,
                              float[] grav,
                              float[] mag,
                              float[] rot) throws SQLException {

        ContentValues sensorValues = new ContentValues();

        sensorValues.put(DATA_SUBJECT, subNum);
        sensorValues.put(DATA_TIME_STAMP, time_stamp);
        sensorValues.put(DATA_TIME, time);
        sensorValues.put(DATA_PHASE, phase);
        sensorValues.put(DATA_ACCX, acc[0]);
        sensorValues.put(DATA_ACCY, acc[1]);
        sensorValues.put(DATA_ACCZ, acc[2]);
        sensorValues.put(DATA_ACCX_V, acc_v[0]);
        sensorValues.put(DATA_ACCY_V, acc_v[1]);
        sensorValues.put(DATA_ACCZ_V, acc_v[2]);
        sensorValues.put(DATA_GYROX, gyro[0]);
        sensorValues.put(DATA_GYROY, gyro[1]);
        sensorValues.put(DATA_GYROZ, gyro[2]);
        sensorValues.put(DATA_GRAVX, grav[0]);
        sensorValues.put(DATA_GRAVY, grav[1]);
        sensorValues.put(DATA_GRAVZ, grav[2]);
        sensorValues.put(DATA_MAGX, mag[0]);
        sensorValues.put(DATA_MAGY, mag[1]);
        sensorValues.put(DATA_MAGZ, mag[2]);

        db.insertOrThrow(DATA_TABLE_NAME_TEMP, null, sensorValues);
    }

    public void copyTempData() throws SQLException{
        String copySubjectSQL = "INSERT INTO " + SUBJECTS_TABLE_NAME + " SELECT * FROM " + SUBJECTS_TABLE_NAME_TEMP;
        db.execSQL(copySubjectSQL);

        String copyDataSQL = "INSERT INTO " + DATA_TABLE_NAME + " SELECT * FROM " + DATA_TABLE_NAME_TEMP;
        db.execSQL(copyDataSQL);
    }

    public void exportTrackingSheet(File outputFile) throws SQLException, IOException {

        csvWrite = new CSVWriter(new FileWriter(outputFile));

        curCSV = db.rawQuery("SELECT * FROM " + SUBJECTS_TABLE_NAME, null);

        csvWrite.writeNext(curCSV.getColumnNames());

        while (curCSV.moveToNext()) {

            String arrStr[] = {curCSV.getString(0), curCSV.getString(1), curCSV.getString(2)};

            csvWrite.writeNext(arrStr);
        }

        csvWrite.close();
        curCSV.close();
    }

    public void exportSubjectData(File outputFile, String subNum) throws IOException, SQLException {

        csvWrite = new CSVWriter(new FileWriter(outputFile));

        curCSV = db.rawQuery("SELECT * FROM " + DATA_TABLE_NAME + " WHERE id = " + subNum, null);

        csvWrite.writeNext(curCSV.getColumnNames());

        Integer writeCounter = 0;
        Integer numRows = curCSV.getCount();

        while (curCSV.moveToNext()) {
            writeCounter++;


            String arrStr[] = {curCSV.getString(0), curCSV.getString(1), curCSV.getString(2),
                    curCSV.getString(3), curCSV.getString(4), curCSV.getString(5),
                    curCSV.getString(6), curCSV.getString(7), curCSV.getString(8),
                    curCSV.getString(9), curCSV.getString(10), curCSV.getString(11),
                    curCSV.getString(12), curCSV.getString(13), curCSV.getString(14),
                    curCSV.getString(15), curCSV.getString(16), curCSV.getString(17), curCSV.getString(18)};
            csvWrite.writeNext(arrStr);

            if ((writeCounter % 1000) == 0){
                csvWrite.flush();
            }

            Double progressPercent = Math.ceil(((float) writeCounter / (float) numRows)*100);
            Message msg = Message.obtain();
            msg.obj = progressPercent;
            msg.setTarget(messageHandler);
            msg.sendToTarget();
        }

        csvWrite.close();
        curCSV.close();
    }
}
