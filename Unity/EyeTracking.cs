using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.XR;
using Varjo.XR;

public enum GazeSource
{
    InputSubsystem,
    GazeAPI
}

public class EyeTracking : MonoBehaviour
{
    [Header("Gaze data")]
    public GazeSource gazeSource = GazeSource.InputSubsystem;

    [Header("Gaze calibration settings")]
    public VarjoEyeTracking.GazeCalibrationMode gazeCalibrationMode = VarjoEyeTracking.GazeCalibrationMode.Fast;
    public KeyCode calibrationRequestKey = KeyCode.Space;
    public bool LogAfterCalibration = true;

    [Header("Gaze output frequency setting (if available)")]
    public VarjoEyeTracking.GazeOutputFrequency gazeOutputFrequency = VarjoEyeTracking.GazeOutputFrequency.MaximumSupported;

    [Header("Toggle gaze target visibility")]
    public bool showGazeTarget = false;
    public KeyCode toggleGazeTarget = KeyCode.Return;
    
    [Header("Debug Gaze")]
    public KeyCode checkGazeAllowed = KeyCode.PageUp;
    public KeyCode checkGazeCalibrated = KeyCode.PageDown;

    [Header("Toggle fixation point indicator visibility")]
    public bool showFixationPoint = false;

    [Header("Visualization Transforms")]
    public Transform fixationPointTransform;
    public Transform leftEyeTransform;
    public Transform rightEyeTransform;

    [Header("XR camera")]
    public Camera xrCamera;

    [Header("Gaze point indicator")]
    public GameObject gazeTarget;

    [Header("Gaze ray radius")]
    public float gazeRadius = 0.01f;

    [Header("Gaze point distance if not hit anything")]
    public float floatingGazeTargetDistance = 5f;

    [Header("Gaze target offset towards viewer")]
    public float targetOffset = 0.2f;

    [Header("Gaze data logging")]
    public KeyCode loggingToggleKey = KeyCode.RightControl;

    [Header("Default path is Logs under application data path.")]
    public bool useCustomLogPath = false;
    public string customLogPath = "";

    private List<InputDevice> devices = new List<InputDevice>();
    private InputDevice device;
    private Eyes eyes;
    private VarjoEyeTracking.GazeData gazeData;
    private List<VarjoEyeTracking.GazeData> dataSinceLastUpdate;
    private Vector3 leftEyePosition;
    private Vector3 rightEyePosition;
    private Quaternion leftEyeRotation;
    private Quaternion rightEyeRotation;
    private Vector3 fixationPoint;
    private Vector3 direction;
    private Vector3 rayOrigin;
    private RaycastHit hit;
    private float distance;
    private StreamWriter writer = null;
    private bool logging = false;

    private static readonly string[] ColumnNames = {
        "raw_timestamp",
        "log_time",
        "focus_distance",
        "frame_number",
        "stability",
        "status",
        "gaze_forward_x",
        "gaze_forward_y",
        "gaze_forward_z",
        "gaze_origin_x",
        "gaze_origin_y",
        "gaze_origin_z",
        "HMD_position_x",
        "HMD_position_y",
        "HMD_position_z",
        "HMD_rotation_x",
        "HMD_rotation_y",
        "HMD_rotation_z",
        "left_forward_x",
        "left_forward_y",
        "left_forward_z",
        "left_origin_x",
        "left_origin_y",
        "left_origin_z",
        "left_pupil_size",
        "left_status",
        "right_forward_x",
        "right_forward_y",
        "right_forward_z",
        "right_origin_x",
        "right_origin_y",
        "right_origin_z",
        "right_pupil_size",
        "right_status", };

    void GetDevice()
    {
        InputDevices.GetDevicesAtXRNode(XRNode.CenterEye, devices);
        device = devices.FirstOrDefault();
    }

    void OnEnable()
    {
        if (!device.isValid)
        {
            GetDevice();
        }
    }

    private void Start()
    {
        VarjoEyeTracking.SetGazeOutputFrequency(gazeOutputFrequency);
        Debug.Log("Gaze output frequency is now: " + VarjoEyeTracking.GetGazeOutputFrequency());

        //make sure filtering is off
        VarjoEyeTracking.GazeOutputFilterType gazeOutputFilterType = VarjoEyeTracking.GazeOutputFilterType.None;
        VarjoEyeTracking.SetGazeOutputFilterType(gazeOutputFilterType);

        //Hiding the gazetarget if gaze is not available or if the gaze calibration is not done
        if (VarjoEyeTracking.IsGazeAllowed() && VarjoEyeTracking.IsGazeCalibrated() && showGazeTarget)
        {
            gazeTarget.GetComponentInChildren<MeshRenderer>().enabled = true;
        }
        else
        {
            gazeTarget.GetComponentInChildren<MeshRenderer>().enabled = false;
        }

        if (showFixationPoint)
        {
            fixationPointTransform.gameObject.SetActive(true);
        }
        else
        {
            fixationPointTransform.gameObject.SetActive(false);
        }
    }

    void Update()
    {
        // start loggin when calibration is finished
        if (VarjoEyeTracking.IsGazeAllowed() && VarjoEyeTracking.IsGazeCalibrated() && LogAfterCalibration == true)
        {
            StartLogging();
            LogAfterCalibration = false;
        }

        // Request gaze calibration
        if (Input.GetKeyDown(calibrationRequestKey))
        {
            VarjoEyeTracking.RequestGazeCalibration(gazeCalibrationMode);
        }
        // Check if gaze is allowed
        if (Input.GetKeyDown(checkGazeAllowed))
        {
            Debug.Log("Gaze allowed: " + VarjoEyeTracking.IsGazeAllowed());
        }

        // Check if gaze is calibrated
        if (Input.GetKeyDown(checkGazeCalibrated))
        {
            Debug.Log("Gaze calibrated: " + VarjoEyeTracking.IsGazeCalibrated());
        }

        // Toggle gaze target visibility
        if (Input.GetKeyDown(toggleGazeTarget))
        {
            gazeTarget.GetComponentInChildren<MeshRenderer>().enabled = !gazeTarget.GetComponentInChildren<MeshRenderer>().enabled;
        }

        // Get gaze data if gaze is allowed and calibrated
        if (VarjoEyeTracking.IsGazeAllowed() && VarjoEyeTracking.IsGazeCalibrated())
        {
            //Get device if not valid
            if (!device.isValid)
            {
                GetDevice();
            }

            // Show gaze target
            gazeTarget.SetActive(true);

            if (gazeSource == GazeSource.InputSubsystem)
            {
                // Get data for eye positions, rotations and the fixation point
                if (device.TryGetFeatureValue(CommonUsages.eyesData, out eyes))
                {
                    if (eyes.TryGetLeftEyePosition(out leftEyePosition))
                    {
                        leftEyeTransform.localPosition = leftEyePosition;
                    }

                    if (eyes.TryGetLeftEyeRotation(out leftEyeRotation))
                    {
                        leftEyeTransform.localRotation = leftEyeRotation;
                    }

                    if (eyes.TryGetRightEyePosition(out rightEyePosition))
                    {
                        rightEyeTransform.localPosition = rightEyePosition;
                    }

                    if (eyes.TryGetRightEyeRotation(out rightEyeRotation))
                    {
                        rightEyeTransform.localRotation = rightEyeRotation;
                    }

                    if (eyes.TryGetFixationPoint(out fixationPoint))
                    {
                        fixationPointTransform.localPosition = fixationPoint;
                    }
                }

                // Set raycast origin point to VR camera position
                rayOrigin = xrCamera.transform.position;

                // Direction from VR camera towards fixation point
                direction = (fixationPointTransform.position - xrCamera.transform.position).normalized;

            } else
            {
                gazeData = VarjoEyeTracking.GetGaze();

                if (gazeData.status != VarjoEyeTracking.GazeStatus.Invalid)
                {
                    // GazeRay vectors are relative to the HMD pose so they need to be transformed to world space
                    if (gazeData.leftStatus != VarjoEyeTracking.GazeEyeStatus.Invalid)
                    {
                        leftEyeTransform.position = xrCamera.transform.TransformPoint(gazeData.left.origin);
                        leftEyeTransform.rotation = Quaternion.LookRotation(xrCamera.transform.TransformDirection(gazeData.left.forward));
                    }

                    if (gazeData.rightStatus != VarjoEyeTracking.GazeEyeStatus.Invalid)
                    {
                        rightEyeTransform.position = xrCamera.transform.TransformPoint(gazeData.right.origin);
                        rightEyeTransform.rotation = Quaternion.LookRotation(xrCamera.transform.TransformDirection(gazeData.right.forward));
                    }

                    // Set gaze origin as raycast origin
                    rayOrigin = xrCamera.transform.TransformPoint(gazeData.gaze.origin);

                    // Set gaze direction as raycast direction
                    direction = xrCamera.transform.TransformDirection(gazeData.gaze.forward);

                    // Fixation point can be calculated using ray origin, direction and focus distance
                    fixationPointTransform.position = rayOrigin + direction * gazeData.focusDistance;
                }
            }
        }

        // Raycast to world from VR Camera position towards fixation point
        if (Physics.SphereCast(rayOrigin, gazeRadius, direction, out hit))
        {
            // Put target on gaze raycast position with offset towards user
            gazeTarget.transform.position = hit.point - direction * targetOffset;

            // Make gaze target point towards user
            gazeTarget.transform.LookAt(rayOrigin, Vector3.up);

            // Scale gazetarget with distance so it apperas to be always same size
            distance = hit.distance;
            gazeTarget.transform.localScale = Vector3.one * distance;

            // Prefer layers or tags to identify looked objects in your application
            // This is done here using GetComponent for the sake of clarity as an example
            RotateWithGaze rotateWithGaze = hit.collider.gameObject.GetComponent<RotateWithGaze>();
            if (rotateWithGaze != null)
            {
                rotateWithGaze.RayHit();
            }  
        }
        else
        {
            // If gaze ray didn't hit anything, the gaze target is shown at fixed distance
            gazeTarget.transform.position = rayOrigin + direction * floatingGazeTargetDistance;
            gazeTarget.transform.LookAt(rayOrigin, Vector3.up);
            gazeTarget.transform.localScale = Vector3.one * floatingGazeTargetDistance;
        }

        if (Input.GetKeyDown(loggingToggleKey))
        {
            if (!logging)
            {
                StartLogging();
            }
            else
            {
                StopLogging();
            }
            return;
        }

        if (logging)
        {
            int dataCount = VarjoEyeTracking.GetGazeList(out dataSinceLastUpdate);
            foreach (var data in dataSinceLastUpdate)
            {
                LogGazeData(data);
            }
        }
    }

    void LogGazeData(VarjoEyeTracking.GazeData data)
    {
        string[] logData = new string[34];

        // Gaze data capture time (nanoseconds)
        logData[0] = data.captureTime.ToString();

        // Log time (milliseconds)
        logData[1] = (DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond).ToString();

        // Focus
        logData[2] = data.focusDistance.ToString();

        // Gaze data frame number
        logData[3] = data.frameNumber.ToString();

        // Focus stability
        logData[4] = data.focusStability.ToString();

        // Gaze Status
        switch (data.status)
        {
            case VarjoEyeTracking.GazeStatus.Invalid:
                logData[5] = 0.ToString();
                break;
            case VarjoEyeTracking.GazeStatus.Adjust:
                logData[5] = 1.ToString();
                break;
            case VarjoEyeTracking.GazeStatus.Valid:
                logData[5] = 2.ToString();
                break;
        }

        // Combined gaze
        logData[6]  = data.gaze.forward.x.ToString();
        logData[7]  = data.gaze.forward.y.ToString();
        logData[8]  = data.gaze.forward.z.ToString();

        logData[9]  = data.gaze.origin.x.ToString();
        logData[10] = data.gaze.origin.y.ToString();
        logData[11] = data.gaze.origin.z.ToString();

        // HMD
        logData[12] = xrCamera.transform.localPosition.x.ToString();
        logData[13] = xrCamera.transform.localPosition.y.ToString();
        logData[14] = xrCamera.transform.localPosition.z.ToString();

        logData[15] = xrCamera.transform.localRotation.x.ToString();
        logData[16] = xrCamera.transform.localRotation.y.ToString();
        logData[17] = xrCamera.transform.localRotation.z.ToString();

        // Left eye
        logData[18] = data.left.forward.x.ToString();
        logData[19] = data.left.forward.y.ToString();
        logData[20] = data.left.forward.z.ToString();

        logData[21] = data.left.origin.x.ToString();
        logData[22] = data.left.origin.y.ToString();
        logData[23] = data.left.origin.z.ToString();

        logData[24] = data.leftPupilSize.ToString();

        switch (data.leftStatus)
        {
            case VarjoEyeTracking.GazeEyeStatus.Invalid:
                logData[25] = 0.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Visible:
                logData[25] = 1.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Compensated:
                logData[25] = 2.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Tracked:
                logData[25] = 3.ToString();
                break;
        }

        // Right eye
        logData[26] = data.right.forward.x.ToString();
        logData[27] = data.right.forward.y.ToString();
        logData[28] = data.right.forward.z.ToString();

        logData[29] = data.right.origin.x.ToString();
        logData[30] = data.right.origin.y.ToString();
        logData[31] = data.right.origin.z.ToString();

        logData[32] = data.rightPupilSize.ToString();

        switch (data.rightStatus)
        {
            case VarjoEyeTracking.GazeEyeStatus.Invalid:
                logData[33] = 0.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Visible:
                logData[33] = 1.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Compensated:
                logData[33] = 2.ToString();
                break;
            case VarjoEyeTracking.GazeEyeStatus.Tracked:
                logData[33] = 3.ToString();
                break;
        }

        Log(logData);
    }

    // Write given values in the log file
    void Log(string[] values)
    {
        if (!logging || writer == null)
            return;

        string line = "";
        for (int i = 0; i < values.Length; ++i)
        {
            values[i] = values[i].Replace("\r", "").Replace("\n", ""); // Remove new lines so they don't break csv
            line += values[i] + (i == (values.Length - 1) ? "" : ","); // Do not add comma to last data string
        }
        writer.WriteLine(line);
    }

    public void StartLogging()
    {
        if (logging)
        {
            Debug.LogWarning("Logging was on when StartLogging was called. No new log was started.");
            return;
        }

        logging = true;

        string logPath = useCustomLogPath ? customLogPath : Application.dataPath + "/Logs/";
        Directory.CreateDirectory(logPath);

        DateTime now = DateTime.Now;
        string fileName = string.Format("{0}-{1:00}-{2:00}_{3:00}-{4:00}-{5:00}-{6:00}", now.Year, now.Month, now.Day, now.Hour, now.Minute, now.Second, now.Millisecond);

        string path = logPath + "varjo_gaze_output_" + fileName + ".csv";
        writer = new StreamWriter(path);

        Log(ColumnNames);
        Debug.Log("Log file started at: " + path);
    }

    void StopLogging()
    {
        if (!logging)
            return;

        if (writer != null)
        {
            writer.Flush();
            writer.Close();
            writer = null;
        }
        logging = false;
        Debug.Log("Logging ended");
    }

    void OnApplicationQuit()
    {
        StopLogging();
    }
}