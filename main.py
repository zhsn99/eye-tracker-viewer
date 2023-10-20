import os
import csv
import pandas as pd
from utils import *
import argparse



def main():
    parser = argparse.ArgumentParser(description="Process or analyze raw data")
    
    valid_actions = ["eye_contact_detection", "pupil_correlation", "your_processed_action","avg_pupil_correlation", "avg_eyes_correlation", "time_series_plot"]
    # Command-line arguments
    parser.add_argument("data_option", choices = ["-","raw", "processed", "conditions"], help = "Choose 'raw' , 'conditions' or 'processed'")
    parser.add_argument("action", choices = valid_actions, help = "Specify the action to perform")

    args = parser.parse_args()

    data_option = args.data_option
    action = args.action
    script_dir = os.path.dirname(__file__)
    raw_data_folder = os.path.join(script_dir, "data\\")
    processed_data_folder = None
    if data_option == "raw":
        if action not in valid_actions:
            print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
            return
        else:
            process_raw_data(raw_data_folder, action)

    elif data_option == "processed":
        if action not in valid_actions:
            print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
            return
        else:
            process_processed_data(processed_data_folder, action)
    elif data_option == "conditions":
        if action not in valid_actions:
            print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
            return
        else:
            process_conditions(raw_data_folder, action)
    elif data_option == "-":
        if action not in valid_actions:
            print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
            return
        else:
            time_series_plot()
    else:
        print("Invalid data option. Choose 'raw' or 'processed'.")

if __name__ == "__main__":
    main()
 
    





   




