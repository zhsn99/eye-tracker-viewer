import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import numpy as np
from scipy.ndimage import gaussian_filter


def reading_file(file_path):
        # Read the pkl file
        df = pd.read_pickle(file_path)
        return df

def check_file_type(file):
        print("Processing file: " + file + " ...")
        if file.endswith(".pkl"):
            print("This is a pkl file. Processing...")
            return True
        else:
            print("This is not a pkl file. Skipping...")
            return False
        
def time_series_plot():
    folder_path = "./time_series/"  
    files = os.listdir(folder_path)

    for file in files:
        print("Processing file: " + file + " ...")
        
        # Read pkl file
        if check_file_type(file) == False:
            continue
        data = pd.read_pickle(os.path.join(folder_path, file))
        time = list(range(len(data)))  
        data = make_data_better(data)
        # Extract data columns
        columns_of_interest = [ 'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
        data = data[columns_of_interest].apply(lambda col: gaussian_kernel(col, 51, 2))

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
        plt.suptitle(f"Time Series of Pupil Diameters for {file[0:len(file)-4]}-Gaussian51_improved")

        # Adjust subplot layout and save the plot
        plt.tight_layout()
        #exclude file extension (.pkl)
        plt.savefig(os.path.join(folder_path, file[0:len(file)-4] +"improved_Gussian51.png"))

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

def conditional_kernel(data, window_size, min_threshold):
    data[(data < min_threshold)] = np.nan
    smoothed_data = data.rolling(window=window_size, min_periods=1).mean()  # Initial smoothing
    smoothed_data[(data < min_threshold)] = np.nan  # Set values outside the range to NaN

def gaussian_kernel(data, window_size, min_threshold):
    # Make a copy of data to avoid modifying the original array
    data_copy = np.copy(data)
    data_copy = data_copy.astype(np.float64)
    sigma = window_size / 20
    smoothed_data = gaussian_filter(data_copy, sigma)
    #check if there is any value less than min_threshold
    smoothed_data[(data_copy < min_threshold)] = np.nan
    return smoothed_data



def plot_correlation_matrix(correlation_matrix, condition):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 for consition: ' + condition)

    #save in the results folder same directory as script
    if not os.path.exists("results/"):
        os.makedirs("results/")
    plt.savefig(os.path.join("results", f'correlation_matrix_pupil_{condition}.png'))  # Save it afterward

def avg_eyes_correlation(df, folder_path, folder, file, improved):
    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    #get average of T1.leftPupilDiameter', 'T1.rightPupilDiameter' columns row by row
    df = make_data_better(df)
    df['T1.averagePupilDiameter'] = df[columns_of_interest[0:2]].mean(axis=1)
    #get average of T2.leftPupilDiameter', 'T2.rightPupilDiameter' columns row by row
    df['T2.averagePupilDiameter'] = df[columns_of_interest[2:4]].mean(axis=1)
    columns_of_interest = ['T1.averagePupilDiameter', 'T2.averagePupilDiameter']
    df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 100, 2))
    # calculate corrolation between T1.averagePupilDiameter and T2.averagePupilDiameter
    correlation = df_smoothed[columns_of_interest].corr()
    with open(folder_path + folder + f"_summary_{folder}.txt", 'a') as f:
        if improved:
            f.write("Correlation Matrix between average eyes of T1 and T2 improved data\n\n")
            f.write(str(correlation))
            f.write("\n\n\n")
        else:
            f.write("Correlation Matrix between average eyes of T1 and T2 raw data\n\n")
            f.write(str(correlation))
            f.write("\n\n")
    # # Plot the heatmap
    # plt.figure(figsize=(10, 8))
    # sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f')
    # plt.title('Correlation Matrix between Pupil Diameters T1 and T2 avg between eyes')

    # #save in the results folder same directory as script
    # if not os.path.exists(folder_path + folder +"/improved_data/"):
    #     os.makedirs(folder_path + folder +"/improved_data/")
    # results_folder = os.path.join(folder_path, folder, "improved_data")  # Use os.path.join for path construction
    # plt.savefig(os.path.join(results_folder, f'avg_eyes_correlation_matrix_pupil_{file}.png'))  # Save it afterward


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
            df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 100, 2))
            #subset = df[columns_of_interest]
            correlation_matrix = df_smoothed[columns_of_interest].corr()
            sum_matrix = sum_matrix + correlation_matrix
        average_matrix = average_matrix + sum_matrix/len(conditions[k])
        plot_correlation_matrix(average_matrix, k)

def pupil_correlation_one_eye(df, folder_path, folder, file, improved, window_size):
    columns_of_interest = [ 'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    right_eyes = ['T1.rightPupilDiameter', 'T2.rightPupilDiameter']
    left_eyes = ['T1.leftPupilDiameter', 'T2.leftPupilDiameter']
    df_smoothed_right = df[right_eyes].apply(lambda col: gaussian_kernel(col, 51, 2))
    df_smoothed_left = df[left_eyes].apply(lambda col: gaussian_kernel(col, 51, 2))
    correlation_matrix_right = df_smoothed_right[right_eyes].corr()
    correlation_matrix_left = df_smoothed_left[left_eyes].corr()

    # Plot the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix_right, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 for the right eye-window size: ' + str(window_size)+'\n'+file[0:len(file)-4])

    #save in the results folder same directory as script
    if not os.path.exists(folder_path + folder +"/smoothed_gussian_51/"):
        os.makedirs(folder_path + folder +f"/smoothed_gussian__{window_size}/")
    results_folder = os.path.join(folder_path, folder, f"smoothed_gussian_{window_size}")  # Use os.path.join for path construction
    plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file[0:len(file)-4]}_right_eye.png')) 
    
    # Plot the heatmap fro left eye
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix_left, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 for the left eye-window size: ' + str(window_size)+'\n'+file[0:len(file)-4])

    #save in the results folder same directory as script
    if not os.path.exists(folder_path + folder +"/smoothed_gussian_51/"):
        os.makedirs(folder_path + folder +f"/smoothed_gussian__{window_size}/")
    results_folder = os.path.join(folder_path, folder, f"smoothed_gussian_{window_size}")  # Use os.path.join for path construction
    plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file[0:len(file)-4]}_left_eye.png')) 

    
def pupil_correlation(df, folder_path, folder, file, improved, window_size):

    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    df_smoothed = df[columns_of_interest].apply(lambda col: gaussian_kernel(col, window_size, 2))
    correlation_matrix = df_smoothed[columns_of_interest].corr()
    # with open(folder_path + folder + f"_summary_{folder}.txt", 'a') as f:
    #     if improved:
    #         f.write("Correlation Matrix between Pupil Diameters T1 and T2 improved data")
    #         f.write("\n\n")
    #         f.write(str(correlation_matrix))
    #         f.write("\n\n")
    #     else:
    #         f.write("start file: " + file + " ...\n")
    #         f.write("\n\n")
    #         f.write("Correlation Matrix between Pupil Diameters T1 and T2 raw data")
    #         f.write("\n\n")
    #         f.write(str(correlation_matrix))
    #         f.write("\n\n")

    if improved: 
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Correlation Matrix between Pupil Diameters T1 and T2')
            if not os.path.exists(folder_path + folder +f"/improved_smoothed_gussian_{window_size}/"):
                os.makedirs(folder_path + folder +f"/improved_smoothed_gussian_{window_size}/")
            results_folder = os.path.join(folder_path, folder, f"improved_smoothed_gussian_{window_size}")  # Use os.path.join for path construction

            plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file[0:len(file)-4]}_improved_smoothed_{window_size}.png'))  # Save it afterward
        
    else:   
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Matrix between Pupil Diameters T1 and T2')
        if not os.path.exists(folder_path + folder +f"/smoothed_gussian_{window_size}/"):
            os.makedirs(folder_path + folder +f"/smoothed_gussian_{window_size}/")
        results_folder = os.path.join(folder_path, folder, f"smoothed_gussian_{window_size}")  # Use os.path.join for path construction

        plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file[0:len(file)-4]}_smoothed_{window_size}.png'))  # Save it afterward
 
 
# loading data raw data
def process_raw_data(folder_path, action):
    # a dictionry of lists
   
    # check if results folder exits
    valid_actions = ["eye_contact_detection", "pupil_correlation", "avg_eyes_correlation", "avg_pupil_correlation", "all", "one_eye_pupil_correlation"]
    # loop through folders in folder path
    folders = os.listdir(folder_path)
    print(folders)
    for folder in folders:
        #check if folder is a folder
        if os.path.isdir(folder_path + folder) == False:
            print("This is not a folder. Skipping...")
            continue
        # get files in folder
        files = os.listdir(folder_path + folder)
        print(20*"#",f"start folder {folder}", 20*"#")
        with open(folder_path + folder + f"_summary_{folder}.txt", 'a') as f:
            for file in files:
                if check_file_type(file):
                    file_path = os.path.join(folder_path, folder, file)
                    df = reading_file(file_path)
                    
                    if action == valid_actions[4]:
                        pupil_correlation(df, folder_path, folder, file,False)
                        pupil_correlation(make_data_better(df), folder_path, folder, file, True)
                        avg_eyes_correlation(df, folder_path, folder, file, False)
                        avg_eyes_correlation(make_data_better(df), folder_path, folder, file, True)
                        
            
                    elif action == valid_actions[0]:
                        pass
                    elif action == valid_actions[1]:
                        pupil_correlation(make_data_better(df), folder_path, folder, file, True, 101)
                    elif action == valid_actions[2]:
                        avg_eyes_correlation(make_data_better(df), folder_path, folder, file)
                    elif action == valid_actions[5]:
                        pupil_correlation_one_eye(df, folder_path, folder, file, False, 101)
                        # pupil_correlation_one_eye(make_data_better(df), folder_path, folder, file, True, 101)
                        pupil_correlation_one_eye(df, folder_path, folder, file, False, 51)
                        # pupil_correlation_one_eye(make_data_better(df), folder_path, folder, file, True, 51)
                     
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


def make_data_better(df):
    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 
        'T2.leftPupilDiameter', 'T2.rightPupilDiameter'
    ]
    
    # Use forward fill to keep the last available data when a value is missed
    df[columns_of_interest] = df[columns_of_interest].fillna(method='ffill')
    
    # If there are still missing values at the beginning of the dataset, you can backfill them
    df[columns_of_interest] = df[columns_of_interest].fillna(method='bfill')
    
    return df


# def make_data_better(df):
#     columns_of_interest = ['T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']

#     #get average of T1.leftPupilDiameter'
#     mean_T1R = df[columns_of_interest[1]].mean()
    
#     mean_T1L = df[columns_of_interest[0]].mean()

#     Mean_T2R = df[columns_of_interest[3]].mean()

#     Mean_T2L = df[columns_of_interest[2]].mean()

#     mean_T1 = np.average([mean_T1L, mean_T1R])
#     mean_T2 = np.average([Mean_T2L, Mean_T2R])
#     print(mean_T1, mean_T2)


#     for i in range(len(df)):
#         if pd.isna(df[columns_of_interest[0]][i]) & (pd.isna(df[columns_of_interest[1]][i])==False):
#             df.loc[i, columns_of_interest[0]] = pd.isna(df[columns_of_interest[1]][i])
#         elif pd.isna(df[columns_of_interest[1]][i]) & (pd.isna(df[columns_of_interest[0]][i])==False):
#             df.loc[i, columns_of_interest[1]] = pd.isna(df[columns_of_interest[0]][i])
#         elif pd.isna(df[columns_of_interest[0]][i]) & pd.isna(df[columns_of_interest[1]][i]):
#             df.loc[i, columns_of_interest[0]] = mean_T1
#             df.loc[i, columns_of_interest[1]] = mean_T1
#         if pd.isna(df[columns_of_interest[2]][i]) & (pd.isna(df[columns_of_interest[3]][i])==False):
#             df.loc[i, columns_of_interest[2]] = pd.isna(df[columns_of_interest[3]][i])
#         elif pd.isna(df[columns_of_interest[3]][i]) & (pd.isna(df[columns_of_interest[2]][i])==False):
#             df.loc[i, columns_of_interest[3]] = pd.isna(df[columns_of_interest[2]][i])
#         elif pd.isna(df[columns_of_interest[2]][i]) & pd.isna(df[columns_of_interest[3]][i]):
#             mean_T2
#             df.loc[i, columns_of_interest[2]] = mean_T2
#             df.loc[i, columns_of_interest[3]] = mean_T2
#         else:
#             continue
#     return df
