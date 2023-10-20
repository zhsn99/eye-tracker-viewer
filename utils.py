import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def reading_file(file_path):
        # Read the excel file
        df = pd.read_excel(file_path)
        return df

def check_file_type(file):
        print("Processing file: " + file + " ...")
        if file.endswith(".xlsx"):
            print("This is a excel file. Processing...")
            return True
        else:
            print("This is not a excel file. Skipping...")
            return False
        
def time_series_plot():
    folder_path = "./time_series/"  
    files = os.listdir(folder_path)

    for file in files:
        print("Processing file: " + file + " ...")
        
        # Read Excel file
        if file.endswith(".xlsx") == False:
            continue
        data = pd.read_excel(os.path.join(folder_path, file))
        time = list(range(len(data)))  # Assuming you have data in some sequence. You might have timestamps or other time indicators.

        # Extract data columns
        columns_of_interest = [ 'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
        data = data[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))

        # Create subplots
        fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

        # Plot each time series in its respective subplot
        axs[0].plot(time, data['T1.leftPupilDiameter'], label='T1 Left Pupil Diameter', color='blue')
        axs[0].set_ylabel('Pupil Diameter')
        axs[0].legend()
        axs[0].grid(True)

        axs[1].plot(time, data['T1.rightPupilDiameter'], label='T1 Right Pupil Diameter', color='cyan')
        axs[1].set_ylabel('Pupil Diameter')
        axs[1].legend()
        axs[1].grid(True)

        axs[2].plot(time, data['T2.leftPupilDiameter'], label='T2 Left Pupil Diameter', color='red')
        axs[2].set_ylabel('Pupil Diameter')
        axs[2].legend()
        axs[2].grid(True)

        axs[3].plot(time, data['T2.rightPupilDiameter'], label='T2 Right Pupil Diameter', color='orange')
        axs[3].set_xlabel('Time')
        axs[3].set_ylabel('Pupil Diameter')
        axs[3].legend()
        axs[3].grid(True)

        # Set the title for the entire figure
        plt.suptitle(f"Time Series of Pupil Diameters for {file[0:10]}")

        # Adjust subplot layout and save the plot
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, file+"smoothed"+ ".png"))
        plt.close()  # Close the figure to release resources



def list_files(folder_path, folder, file, conditions):

    if file.find("c01") != -1:
        conditions["c01"].append(os.path.join(folder_path, folder, file))
    elif file.find("c02") != -1:
        conditions["c02"].append(os.path.join(folder_path, folder, file))
    elif file.find("c03") != -1:
        conditions["c03"].append(os.path.join(folder_path, folder, file))
    elif file.find("c04") != -1:
        conditions["c04"].append(os.path.join(folder_path, folder, file))
    elif file.find("c05") != -1:
        conditions["c05"].append(os.path.join(folder_path, folder, file))
    elif file.find("c06") != -1:
        conditions["c06"].append(os.path.join(folder_path, folder, file))
    else:
        print(20*"#",f"start folder {file}", 20*"#")
    return conditions

# def conditional_kernel_pd(data, column_name, window_size, min_threshold, max_threshold):
#     data[(data < min_threshold) | (data > max_threshold)] = np.nan
#     smoothed_data = data.rolling(window=window_size, min_periods=1).mean()  # Initial smoothing
#     smoothed_data[(data < min_threshold) | (data > max_threshold)] = np.nan  # Set values outside the range to NaN
#     smoothed_data = data.loc[(data[column_name] < min_threshold) | (data[column_name] > max_threshold), column_name] = np.nan
#     return smoothed_data


def conditional_kernel(data, window_size, min_threshold, max_threshold):
    data[(data < min_threshold) | (data > max_threshold)] = np.nan
    smoothed_data = data.rolling(window=window_size, min_periods=1).mean()  # Initial smoothing
    smoothed_data[(data < min_threshold) | (data > max_threshold)] = np.nan  # Set values outside the range to NaN
    return smoothed_data

def plot_correlation_matrix(correlation_matrix, condition):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 for consition: ' + condition)

    #save in the results folder same directory as script
    if not os.path.exists("results/"):
        os.makedirs("results/")
    plt.savefig(os.path.join("results", f'correlation_matrix_pupil_{condition}.png'))  # Save it afterward

def avg_eyes_correlation(df, folder_path, folder, file):
    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    #get average of T1.leftPupilDiameter', 'T1.rightPupilDiameter' columns row by row
    df['T1.averagePupilDiameter'] = df[columns_of_interest[0:2]].mean(axis=1)
    #get average of T2.leftPupilDiameter', 'T2.rightPupilDiameter' columns row by row
    df['T2.averagePupilDiameter'] = df[columns_of_interest[2:4]].mean(axis=1)
    columns_of_interest = ['T1.averagePupilDiameter', 'T2.averagePupilDiameter']
    df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
    # calculate corrolation between T1.averagePupilDiameter and T2.averagePupilDiameter
    correlation = df_smoothed[columns_of_interest].corr()

    # Plot the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 avg between eyes')

    #save in the results folder same directory as script
    if not os.path.exists(folder_path + folder +"/smoothed_results/"):
        os.makedirs(folder_path + folder +"/smoothed_results/")
    results_folder = os.path.join(folder_path, folder, "smoothed_results")  # Use os.path.join for path construction
    plt.savefig(os.path.join(results_folder, f'avg_eyes_correlation_matrix_pupil_{file}.png'))  # Save it afterward


def avg_pupil_correlation(conditions):
    print("Calculating average pupil correlation...")
    data = {
        'T1.leftPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T1.rightPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T2.leftPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T2.rightPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000]
    }

    # Create a DataFrame with the specified shape
    

    keys = conditions.keys()
    for k in keys:
        average_matrix = pd.DataFrame(data, columns=data.keys(), index=data.keys())
        print(20*"#","Working on Conidition: ", k,20*"#")
        sum_matrix = pd.DataFrame(data, columns=data.keys(), index=data.keys())
        for file in conditions[k]:
            print("Processing file: " + file + " ...")
            df = reading_file(file)
            columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
            df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
            #subset = df[columns_of_interest]
            correlation_matrix = df_smoothed[columns_of_interest].corr()
            sum_matrix = sum_matrix + correlation_matrix
        average_matrix = average_matrix + sum_matrix/len(conditions[k])
        plot_correlation_matrix(average_matrix, k)

def pupil_correlation(df, folder_path, folder, file):

    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
    correlation_matrix = df_smoothed[columns_of_interest].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2')
    if not os.path.exists(folder_path + folder +"/smoothed_results/"):
        os.makedirs(folder_path + folder +"/smoothed_results/")
    results_folder = os.path.join(folder_path, folder, "smoothed_results")  # Use os.path.join for path construction

    plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file}.png'))  # Save it afterward
 
 
# loading data raw data
def process_raw_data(folder_path, action):
    # a dictionry of lists
   
    # check if results folder exits
    valid_actions = ["eye_contact_detection", "pupil_correlation", "avg_eyes_correlation", "avg_pupil_correlation"]
    # loop through folders in folder path
    folders = os.listdir(folder_path)
    print(folders)
    for folder in folders:
        files = os.listdir(folder_path + folder)
        print(20*"#",f"start folder {folder}", 20*"#")
        for file in files:
            if check_file_type(file):
                file_path = os.path.join(folder_path, folder, file)
                df = reading_file(file_path)
                if action == valid_actions[0]:
                     pass
                elif action == valid_actions[1]:
                     pupil_correlation(df, folder_path, folder, file)
                elif action == valid_actions[2]:
                     avg_eyes_correlation(df, folder_path, folder, file)
                    
                else:
                     print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
                
            else:
                continue
            # If it was the last file, print "Done!"
            if file == files[-1]:
                print(f"Done! {folder_path + folder}")
            else:
                print("Done!, next file...")


def process_processed_data(folder_path, action):
     return 0

def process_conditions(folder_path, action):
    print("Processing conditions...")
    conditions = {"c01": [], "c02": [], "c03": [], "c04": [], "c05": [], "c06": []}
    folders = os.listdir(folder_path)
    for folder in folders:
        files = os.listdir(folder_path + folder)
        for file in files:
            if check_file_type(file):
                conditions = list_files(folder_path, folder, file, conditions)   
            else:
                continue
            # If it was the last file, print "Done!"
            if file == files[-1]:
                print(f"Done! {folder_path + folder}")
            else:
                print("Done!, next file...")
    
    print(conditions)
    if action == "avg_pupil_correlation":
        avg_pupil_correlation(conditions)
    return 0