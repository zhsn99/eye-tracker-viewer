import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# List of columns to read
columns = ["T1.RX", "T1.RY", "T1.RZ", "T1.TX", "T1.TY", "T1.TZ", 
           "T2.RX", "T2.RY", "T2.RZ", "T2.TX", "T2.TY", "T2.TZ", 
           "win.RX", "win.RY", "win.RZ", "win.TX", "win.TY", "win.TZ", 
           "T1.timestamp", "T1.gaze2D.X", "T1.gaze2D.Y", "T1.gaze3D.X", 
           "T1.gaze3D.Y", "T1.gaze3D.Z", "T1.leftGazeDirection.X", 
           "T1.leftGazeDirection.Y", "T1.leftGazeDirection.Z", 
           "T1.rightGazeDirection.X", "T1.rightGazeDirection.Y", 
           "T1.rightGazeDirection.Z", "T1.leftGazeOrigin.X", 
           "T1.leftGazeOrigin.Y", "T1.leftGazeOrigin.Z", 
           "T1.rightGazeOrigin.X", "T1.rightGazeOrigin.Y", 
           "T1.rightGazeOrigin.Z", "T1.leftPupilDiameter", 
           "T1.rightPupilDiameter", "T2.timestamp", "T2.gaze2D.X", 
           "T2.gaze2D.Y", "T2.gaze3D.X", "T2.gaze3D.Y", "T2.gaze3D.Z", 
           "T2.leftGazeDirection.X", "T2.leftGazeDirection.Y", 
           "T2.leftGazeDirection.Z", "T2.rightGazeDirection.X", 
           "T2.rightGazeDirection.Y", "T2.rightGazeDirection.Z", 
           "T2.leftGazeOrigin.X", "T2.leftGazeOrigin.Y", "T2.leftGazeOrigin.Z", 
           "T2.rightGazeOrigin.X", "T2.rightGazeOrigin.Y", "T2.rightGazeOrigin.Z", 
           "T2.leftPupilDiameter", "T2.rightPupilDiameter"]

# Read folders in this directory same as script
path = os.getcwd()

folders = os.listdir(path)
print("Folders in this directory:", folders)

for folder in folders:
    #skip this foler : combinedData_Exp1_01
    if folder == 'combinedData_Exp1_01':
        continue
    if not os.path.isdir(folder):
        print("Skipping non-directory:", folder)
        continue
    files = os.listdir(folder)
    print("Folder:", folder)
    for file in files:
        if not file.endswith(".xlsx"):
            print("Skipping non-Excel file:", file)
            continue
        df = pd.read_excel(os.path.join(folder, file), usecols=columns)

        # Save DataFrame as a .pkl file
        print("Saving file:", file[:-5]+'.pkl...')
        df.to_pickle(os.path.join(folder, file[:-5]+'.pkl'))



