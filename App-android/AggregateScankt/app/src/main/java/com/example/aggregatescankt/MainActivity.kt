package com.example.aggregatescankt

import androidx.appcompat.app.AppCompatActivity

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothSocket
import android.content.ContentValues
import android.content.DialogInterface
import android.content.Intent
import android.content.pm.PackageManager
import android.os.*
import android.provider.MediaStore
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import androidx.camera.lifecycle.ProcessCameraProvider
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.activity.result.ActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.RequiresApi
import androidx.camera.core.*
import androidx.camera.view.PreviewView
import com.example.aggregatescankt.databinding.ActivityMainBinding
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*
import kotlin.collections.ArrayList

class MainActivity : AppCompatActivity() {

    private lateinit var viewBinding: ActivityMainBinding

    lateinit var bluetoothManager: BluetoothManager
    lateinit var bluetoothAdapter: BluetoothAdapter

    var deviceName = ArrayList<String>()
    var deviceHardwareAddress = ArrayList<String>()
    var position_list: Int = 0
    var save_name: String = "Default"
    var messageToArduino = ""

    val MY_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805f9b34fb") //For HC-06 is this

    lateinit var b_connect: Button
    lateinit var b_folder: Button
    lateinit var b_about: Button
    lateinit var list_view: ListView
    lateinit var save_view: EditText
    lateinit var t_folder: TextView

    lateinit var listView: View
    lateinit var saveView: View

    lateinit var mDevice: BluetoothDevice
    lateinit var mSocket: BluetoothSocket

    val handlerThread = HandlerThread("MyHandlerThread")

    private var imageCapture: ImageCapture? = null
    private lateinit var cameraExecutor: ExecutorService

    @SuppressLint("InflateParams")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewBinding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(viewBinding.root)

        if (allPermissionsGranted()) {
            startBluetooth()
            startCamera()

            handlerThread.start()

            b_connect = findViewById(R.id.btn_connect)
            b_folder = findViewById(R.id.btn_folder)
            b_about = findViewById(R.id.btn_about)
            t_folder = findViewById(R.id.tv_folder)

                saveView = layoutInflater.inflate(R.layout.folder_name, null)
            save_view = saveView.findViewById(R.id.edt_name_folder)
            listView = layoutInflater.inflate(R.layout.paired_devices, null)
            list_view = listView.findViewById(R.id.list_view_dialog)

            list_view.setOnItemClickListener { parent, view, position, id ->
                position_list = position
            }


            b_connect.setOnClickListener { paired_devices() }
            b_folder.setOnClickListener { show_save_path() }
            b_about.setOnClickListener {  }

        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS.toTypedArray(), REQUEST_CODE_PERMISSIONS)
        }

        // Set up the listeners for take photo and video capture buttons


        cameraExecutor = Executors.newSingleThreadExecutor()

        packageManager.takeIf { it.missingSystemFeature(PackageManager.FEATURE_BLUETOOTH) }?.also {
            Toast.makeText(this, "Bluetooth not supported", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    //==============BLUETOOTH====================
    private fun PackageManager.missingSystemFeature(name: String): Boolean = !hasSystemFeature(name)

    fun startBluetooth() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            bluetoothManager = getSystemService(BluetoothManager::class.java)
        }
        bluetoothAdapter = bluetoothManager.adapter

        if (!bluetoothAdapter.isEnabled) { //if false, ask for enable the bluetooth
            val enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            resultLauncher.launch(enableBtIntent)
        }
    }

    var resultLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result: ActivityResult ->
        if (result.resultCode == Activity.RESULT_OK) { //if answer is Allow, enable the bluetooth, if deny, close the app
            val intent = result.data
            Toast.makeText(this, intent.toString(), Toast.LENGTH_LONG).show()
        } else {
            finish()
        }
    }

    @SuppressLint("MissingPermission")
    fun paired_devices() {
        if (allPermissionsGranted()) {
            val pairedDevices: Set<BluetoothDevice>? = bluetoothAdapter.bondedDevices
            pairedDevices?.forEach {
                deviceName.add(it.name)
                deviceHardwareAddress.add(it.address) //MAC Address
            }
            if (pairedDevices != null) {
                show_paired(pairedDevices)
            } else {
                Toast.makeText(this@MainActivity, "No paired Devices", Toast.LENGTH_SHORT).show()
            }
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS.toTypedArray(), REQUEST_CODE_PERMISSIONS)
        }
    }

    fun show_paired(paireds: Set<BluetoothDevice>) {

        val builder = AlertDialog.Builder(this@MainActivity)

        val parentView = listView.parent as? ViewGroup
        parentView?.removeView(listView)

        val adapter = ArrayAdapter(this@MainActivity, android.R.layout.simple_list_item_1, deviceName)

        list_view.adapter = adapter


        builder.setView(listView)
            .setTitle("Paired Devices")
            .setPositiveButton("Select", DialogInterface.OnClickListener { dialogInterface, i ->
//                val device_choosed = paireds.elementAt(position_list)
//                val uuids: Array<ParcelUuid>? = device_choosed.uuids
//                if (uuids != null) {
//                    for (uuid in uuids) {
//                        Log.d("UUID", uuid.toString())
//                    }
//                }
//                Toast.makeText(this@MainActivity, device_choosed, Toast.LENGTH_SHORT).show()
                mDevice = paireds.elementAt(position_list)
                ConnectThread(mDevice).start()
                dialogInterface.dismiss()
            })
            .setNegativeButton("Cancel", DialogInterface.OnClickListener { dialogInterface, i ->
                Toast.makeText(this@MainActivity, "canceled", Toast.LENGTH_SHORT).show()
                dialogInterface.dismiss()
            })

        builder.create().show()
    }

    fun start_receiving(myBluetoothSocket: BluetoothSocket){

        val handler = MyHandler()

        val myBluetoothService = MyBluetoothService(handler)

        val connectedThread = myBluetoothService.ConnectedThread(myBluetoothSocket)

        connectedThread.start()

    }

    fun start_sending(myBluetoothSocket: BluetoothSocket){

        val handler = MyHandler()

        val myBluetoothService = MyBluetoothService(handler)

        val connectedThread = myBluetoothService.ConnectedThread(myBluetoothSocket)

        val message = messageToArduino.toByteArray()

//        Log.i("Test_info: ", message.toString(Charsets.UTF_8))

        connectedThread.write(message)
    }

    fun show_save_path() {

        val parentView = saveView.parent as? ViewGroup
        parentView?.removeView(saveView)

        val builder = AlertDialog.Builder(this@MainActivity)

        builder.setView(saveView)
            .setTitle("Folder to save")
            .setPositiveButton("Choose", DialogInterface.OnClickListener { dialogInterface, i ->
                save_name = save_view.text.toString().trim()
                t_folder.text = save_name
                Toast.makeText(this@MainActivity, "Changed to: $save_name", Toast.LENGTH_LONG).show()
                dialogInterface.dismiss()
            })
            .setNegativeButton("Cancel", DialogInterface.OnClickListener { dialogInterface, i ->
                dialogInterface.dismiss()
            })

        builder.create().show()

    }

    //==============CAMERA====================
    private fun takePhoto() {
        // Get a stable reference of the modifiable image capture use case
        val imageCapture = imageCapture ?: return

        // Create time stamped name and MediaStore entry.
        val name = save_name + SimpleDateFormat(FILENAME_FORMAT, Locale.US)
            .format(System.currentTimeMillis())
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            if(Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
                put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Aggregate_Scan/$save_name")
            }
        }

        // Create output options object which contains file + metadata
        val outputOptions = ImageCapture.OutputFileOptions
            .Builder(contentResolver,
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                contentValues)
            .build()

        // Set up image capture listener, which is triggered after photo has
        // been taken
        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onError(exc: ImageCaptureException) {
                    Log.e(TAG, "Photo capture failed: ${exc.message}", exc)
                }

                override fun onImageSaved(output: ImageCapture.OutputFileResults){
                    val msg = "Photo capture succeeded: ${output.savedUri}"
                    Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                    Log.d(TAG, msg)
                    messageToArduino = "taken"
                    start_sending(mSocket)
                }
            }
        )
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            // Used to bind the lifecycle of cameras to the lifecycle owner
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            //resize and place in center of previwView
            viewBinding.viewFinder.scaleType = PreviewView.ScaleType.FIT_CENTER

            // Preview
            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
                }

            imageCapture = ImageCapture.Builder()
                .build()

            // Select back camera as a default
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                // Unbind use cases before rebinding
                cameraProvider.unbindAll()

                // Bind use cases to camera
                val camera = cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageCapture)

                //camera focus centered
                val cameraControl = camera.cameraControl
                val factory = SurfaceOrientedMeteringPointFactory(
                    viewBinding.viewFinder.width.toFloat(),
                    viewBinding.viewFinder.height.toFloat()
                )
                val point = factory.createPoint(
                    viewBinding.viewFinder.width.toFloat()/2,
                    viewBinding.viewFinder.height.toFloat()/2,
                    0.05F
                )
                val action = FocusMeteringAction.Builder(point).build()
                cameraControl.startFocusAndMetering(action)

                //Toast.makeText(this, point.size.toString(), Toast.LENGTH_LONG).show()

            } catch(exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
            }

        }, ContextCompat.getMainExecutor(this))
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }

    companion object {
        private const val TAG = "CameraXApp"
        private const val FILENAME_FORMAT = "yyyy-MM-dd-HH-mm-ss-SSS"
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS =
            mutableListOf (
                Manifest.permission.CAMERA,
                Manifest.permission.BLUETOOTH
            ).apply {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    add(Manifest.permission.BLUETOOTH_CONNECT)
                    add(Manifest.permission.BLUETOOTH_SCAN)
                }
                if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                    add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }

    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startCamera()
            } else {
                ActivityCompat.requestPermissions(this@MainActivity,
                    REQUIRED_PERMISSIONS.filter { ContextCompat.checkSelfPermission(
                                                this@MainActivity,
                                                        it) != PackageManager.PERMISSION_GRANTED }.toTypedArray(),
                    REQUEST_CODE_PERMISSIONS)
            }
        }
    }

    @SuppressLint("MissingPermission")
    private inner class ConnectThread(device: BluetoothDevice) : Thread() {

        private val mmSocket: BluetoothSocket? by lazy(LazyThreadSafetyMode.NONE) {
            device.createRfcommSocketToServiceRecord(MY_UUID)
        }

        override fun run() {
//            Toast.makeText(this@MainActivity, "entrou",Toast.LENGTH_SHORT).show()
            bluetoothAdapter.cancelDiscovery()

            try {
                mmSocket?.let {
                    it.connect()
                    mSocket = it

                    val h = Handler(Looper.getMainLooper())
                    h.post{
                        Toast.makeText(this@MainActivity, "Connection was done", Toast.LENGTH_SHORT).show()
                    }

                    start_receiving(mSocket)
                }
            } catch (e: IOException) {
                Log.e("Could not connect", e.toString())

                val h = Handler(Looper.getMainLooper())
                h.post{
                    Toast.makeText(this@MainActivity, "Connection failed", Toast.LENGTH_SHORT).show()
                }
            }
        }

        fun send(){
            start_sending(mSocket)
        }

        fun cancel() {
            try {
                mmSocket?.close()
            } catch (e: IOException) {
                Log.e("Could not close", e.toString())
            }
        }

    }

    @SuppressLint("HandlerLeak")
    inner class MyHandler : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MESSAGE_READ -> {
                    // Handle message of type MESSAGE_READ
                    val bytes = msg.obj as ByteArray
                    val numBytes = msg.arg1
                    // Process the received data
                    val message = String(bytes, 0, numBytes, Charsets.UTF_8)
                    Log.i("Test_info: Receive ", message)
                    if (message.contains("xis")){
                        takePhoto()
                    }else if (message.contains("status")){
                        messageToArduino = "Connected"
                        start_sending(mSocket)
                    }else if(message.contains("connected")){
                        Toast.makeText(this@MainActivity, "Connected", Toast.LENGTH_SHORT).show()
                    }
                }
                MESSAGE_WRITE -> {
                    // Handle message of type MESSAGE_WRITE
                    val bytes = msg.obj as ByteArray
                    val numBytes = msg.arg1
                    // Process the sent data
//                    val s = bytes.joinToString(":") { String.format("%02X", it) }
//                    Log.i("Test_info: Send ", bytes[1].toInt().toString())
//                    folder_name.text = numBytes.toString()
//                    Toast.makeText(this@MainActivity, "Message: $bytes", Toast.LENGTH_LONG).show()

                }
                MESSAGE_TOAST -> {
                    // Handle message of type MESSAGE_TOAST
                    val bundle = msg.data
                    val message = bundle.getString("toast")
                    // Display the error message
                }
                // Handle other message types here
            }
        }
    }

}