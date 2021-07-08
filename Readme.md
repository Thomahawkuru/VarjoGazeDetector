# Varjo Gaze Detector

Varjo Gaze Detector classifies gaze events in eye-tracking recordings from the Varjo VR and XR headsets. It detects fixations, saccades, smooth persuits and blinks. As well as their duration, amplituded and mean/max velocities. 
This tool is developed by Thomas de Boer, with use of the detection algorithm from [sp_tool](https://github.com/MikhailStartsev/sp_tool) by Mikhail Startsev. Please cite their paper when using this code:

    @inproceedings{agtzidis2016smooth,
      title={Smooth pursuit detection based on multiple observers},
      author={Agtzidis, Ioannis and Startsev, Mikhail and Dorr, Michael},
      booktitle={Proceedings of the Ninth Biennial ACM Symposium on Eye Tracking Research \& Applications},
      pages={303--306},
      year={2016},
      organization={ACM}
    }

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/. license - GPL.

version: 1.0 \
date: 5-7-2021

Build using:
 - Python 3.9
 - Unity 2020.3.7f1
 - Varjo Base 3.0.5.14
 - XR-1 developer edition firmware 2.5

# Recording eye-tracking data
VarjoGazeDetector works with two methods of recording eye-tracking data. 
- Through the build in recording option in Varjo Base. For information see: https://developer.varjo.com/docs/get-started/gaze-data-collection
- With a script directly in Unity. The script and prefab used are included in the folder 'Unity'

Both methods produce a .csv with eye-tracking data, which VarjoGazeDetector can process. 
Only Varjo Base recording produces a video capture automatically. 
When Varjo Base is used, the detections are matched with the time of the video.

The tool is set up to assume a folder structure based on research participants with a certain number of trails each.
Make sure the folder structure is participant/trail as follows, if you would like to use the tool as is. Both recording methods can be mixed. 

    data_folder/
        1/
            1/
                varjo_gaze_output_XX-XX-XXXX.csv
                varjo_capture_XX-XX-XXXX.csv
            2/
                varjo_gaze_output_XX-XX-XXXX.csv
        2/
            1/
                varjo_gaze_output_XX-XX-XXXX.csv
            2/
                varjo_gaze_output_XX-XX-XXXX.csv
                varjo_capture_XX-XX-XXXX.csv
        3/
            1/
                varjo_gaze_output_XX-XX-XXXX.csv
            2/
                varjo_gaze_output_XX-XX-XXXX.csv

The detection results are saved in a 'detection' folder in each trail folder. 
Detection and their measures are saved as fixations.csv, saccades.csv, persuits.csv and blinks.csv

# How to use
Make sure the right packages are installed in your environment:
```bash
pip install numpy pandas matplotlib liac-arff 
```

Detection is run by running the script main.py. Here you can set global parameters for running the detection:

```python
savedata        = False     # whether or not the gaze events and their measures are saved in .csv files
showfig         = True      # whether or not the plot figures are shown after detection
savefig         = False     # whether or not the plot figures are saved after detection
debugdetection  = False     # show runtime info about the detection in the console
printresults    = True      # show results of the detection in the console
```
Also in main.py you have to give the path to the data folder, and specify the participants and trails
```python
datapath        = 'C:/path_to_data'             # put the full path to your data here
participants    = 2                             # number of participants
trails          = 2                             # trails per participant
filename        = 'varjo_gaze_output'           # looks for files with this string in the name
```

The parameters for detection are specified in run_detection.py. 