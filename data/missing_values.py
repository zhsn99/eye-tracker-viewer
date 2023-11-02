import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def missing_values_plot(df, file):  
    #data to plot
    n_groups = 4
    missing_values =(df['T1.leftPupilDiameter'].isnull().sum(),
                        df['T1.rightPupilDiameter'].isnull().sum(),
                        df['T2.leftPupilDiameter'].isnull().sum(),
                        df['T2.rightPupilDiameter'].isnull().sum()
                        )
    missing_values_percentage = (
        df['T1.leftPupilDiameter'].isnull().sum() / df.shape[0] * 100,
        df['T1.rightPupilDiameter'].isnull().sum() / df.shape[0] * 100,
        df['T2.leftPupilDiameter'].isnull().sum() / df.shape[0] * 100,
        df['T2.rightPupilDiameter'].isnull().sum() / df.shape[0] * 100
    )
    # create plot
    #make plot bigger
    plt.rcParams["figure.figsize"] = (10,10)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.9

    rects1 = plt.bar(index, missing_values_percentage, bar_width,
                     alpha=opacity, color='b', label='Missing Values (%)')

    plt.xlabel('Eyes')
    plt.ylabel('Percentage of missing values')
    plt.title('Percentage of Missing values of Pupil Diameter per eye\n  No. Frames: '+str(df.shape[0])+"\n"+"file name:"+file)

    # Show the actual count of missing values and the percentage on top of each bar
    for i, (v, perc) in enumerate(zip(missing_values, missing_values_percentage)):
        # Add actual count of missing values just above the bar
        ax.text(i, perc + 1, str(v)+"\n", ha='center', color='red', fontweight='bold')
        # Add percentage slightly below the count
        ax.text(i, perc + 1, str(round(perc, 2))+"%", ha='center', color='blue', fontweight='bold')

    plt.xticks(index, ('T1.left', 'T1.right', 'T2.left', 'T2.right'), rotation=45)
    plt.ylim(0, 100)  # set y-axis limits to 0-100
    plt.legend()

    # Save the plot
    plt.savefig(file[:-4]+"_missing_values.png")
    return missing_values_percentage, missing_values



path = os.getcwd()

folders = os.listdir(path)
print("Folders in this directory:", folders)

details = {}
for folder in folders:
    #skip if it is not a directory
    if not os.path.isdir(folder):
        print("Skipping non-directory:", folder)
        continue
    files = os.listdir(folder)
    print("Folder:", folder)
    for file in files:

        if not file.endswith(".pkl"):
            print("Skipping non-pkl file:", file)
            continue
        df = pd.read_pickle(os.path.join(folder, file))
        #add fike without extension as key to the dictionary
        details[file[:-4]] = {}
        percentage, numbers = missing_values_plot(df, file)
        details[file[:-4]]['percentage'] = percentage
        details[file[:-4]]['numbers'] = numbers
        details[file[:-4]]['frame_number'] = df.shape[0]


#find the the Tracker with most missing values(T1 or T2)
#find the eye with most missing values(left or right) for each tracker
#append to a text file result

for key in details.keys():
    #find the tracker with most missing values
    if details[key]['percentage'][0] + details[key]['percentage'][1] > details[key]['percentage'][2] + details[key]['percentage'][3]:
        if details[key]['numbers'][0] + details[key]['numbers'][1] <1:
            details[key]['tracker'] = 'None'
        else:
            details[key]['tracker'] = 'T1'
    else:
        if details[key]['numbers'][2] + details[key]['numbers'][3] <1:
            details[key]['tracker'] = 'None'
        else:
            details[key]['tracker'] = 'T2'
    #find the eye with most missing values
    if details[key]['percentage'][0] > details[key]['percentage'][1]:
        if details[key]['numbers'][0] <1:
            details[key]['eye'] = 'None'
        else:
            details[key]['eye'] = 'left'
    else:
        if details[key]['numbers'][1] <1:
            details[key]['eye'] = 'None'
        else:
            details[key]['eye'] = 'right'


with open("missing_values_result.txt", "a") as f:
    for key in details.keys():
        f.write("File name: "+key+"\n")
        f.write("Number of frames: "+str(details[key]['frame_number'])+"\n")
        f.write("Tracker with most missing values: "+details[key]['tracker']+"\n")
        f.write("Eye with most missing values: "+details[key]['eye']+"\n")
        f.write("Missing values per column:\n")
        f.write(f"number of missing values: {details[key]['numbers'][0]}, " \
                f"Percentage of missing values: {details[key]['percentage'][0]}%\n")

        f.write(f"number of missing values: {details[key]['numbers'][1]}, " \
                f"Percentage of missing values: {details[key]['percentage'][1]}%\n")

        f.write(f"number of missing values: {details[key]['numbers'][2]}, " \
                f"Percentage of missing values: {details[key]['percentage'][2]}%\n")

        f.write(f"number of missing values: {details[key]['numbers'][3]}, " \
                f"Percentage of missing values: {details[key]['percentage'][3]}%\n")

        f.write("\n\n")

#what is most repeated tracker and eye with most missing values

tracker = []
eye = []
for key in details.keys():
    tracker.append(details[key]['tracker'])
    eye.append(details[key]['eye'])
print("Tracker with most missing values:", max(set(tracker), key=tracker.count))
print("Eye with most missing values:", max(set(eye), key=eye.count))

#append to the text file
with open("missing_values_result.txt", "a") as f:
    f.write("Tracker with most missing values: "+max(set(tracker), key=tracker.count)+"\n")
    f.write("Eye with most missing values: "+max(set(eye), key=eye.count)+"\n")

#plot a final plot of the percentage of missing values per eye over all files

#usign details dictionary

#data to plot
n_groups = 4
missing_values =[]
missing_values_percentage = []
T1_left_sum =0
T2_left_sum =0
T1_right_sum =0
T2_right_sum =0
frame_total=0
for key in details.keys():
    # missing_values.append(details[key]['numbers'][0])
    T1_left_sum+=details[key]['numbers'][0]
    T1_right_sum+=details[key]['numbers'][1]
    T2_left_sum+=details[key]['numbers'][2]
    T2_right_sum+=details[key]['numbers'][3]
    frame_total+=details[key]['frame_number']


#a plot with for bars for each eye sum

# create plot
#make plot bigger
plt.rcParams["figure.figsize"] = (10,10)
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.9

rects1 = plt.bar(index, [T1_left_sum/frame_total*100, T1_right_sum/frame_total*100, T2_left_sum/frame_total*100, T2_right_sum/frame_total*100], bar_width,
                    alpha=opacity, color='b', label='Missing Values (%)')

plt.xlabel('Eyes')
plt.ylabel('Percentage of missing values')
plt.title('Percentage of Missing values of Pupil Diameter per eye\n  No. Frames: '+str(frame_total)+"\n"+"file name: All files")

# Show the actual count of missing values and the percentage on top of each bar
for i, perc in enumerate([T1_left_sum/frame_total*100, T1_right_sum/frame_total*100, T2_left_sum/frame_total*100, T2_right_sum/frame_total*100]):
    # Add actual count of missing values just above the bar
    ax.text(i, perc + 1, str(round(perc, 2))+"%", ha='center', color='blue', fontweight='bold')

plt.xticks(index, ('T1.left', 'T1.right', 'T2.left', 'T2.right'), rotation=45)
plt.ylim(0, 100)  # set y-axis limits to 0-100
plt.legend()
plt.savefig("All_files_missing_values.png")