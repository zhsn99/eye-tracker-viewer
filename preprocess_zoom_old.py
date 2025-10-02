'''
This script will read in the raw tracking data into a npy format
This format is faster and more convienient to read in downstream processing
The rotation of each participant is also converted into rotation matricies
Since we may not know the Euler rotation order, this script will output version for all of them
'''

from openpyxl import load_workbook
import numpy as np
from tqdm import tqdm
import scipy
import sys
import os
import pandas as pd
import os
from multiprocessing import Pool
from scipy.spatial.transform import Rotation as R



def zoom_transform(point, t_mat, win_RB_3D_1, win_RB_3D_2, win_RB_3D_3, win_RB_3D_4, rotation_order):
    #3d gzaze origin point --> 2D gaze origin in pixel coordinates

    #2d pixe;s --> zoom_trasnfrom --> 3d gaze(on screen) in world coordinates

    x_range = (0, 2048)
    y_range = (0, 2732)

    points_2D = np.array([
        [2048, 2732],  # Corresponds to win_RB_3D_1
        [2048, 0],     # Corresponds to win_RB_3D_2
        [0, 0],        # Corresponds to win_RB_3D_3
        [0, 2732]      # Corresponds to win_RB_3D_4
    ])

    points_3D = np.array([
        win_RB_3D_1,
        win_RB_3D_2,
        win_RB_3D_3,
        win_RB_3D_4
    ])

    # Perform transformation of 3D points to 2D points
    point = np.hstack([point, 1])

    proj_h = np.dot(point, t_mat.T)

    # Normalize homogeneous coordinates to obtain non-homogeneous 2D points
    proj_2d = proj_h[:2] / proj_h[2]
    # proj_2d = [0,0]

    # Compute x- and y-axis interpolants needed to reach this point in pixel coords
    # aka inverse bilinear interpolation

    proj_2d = np.array(proj_2d)

    def lerp(a, b, t):
        return a + t * (b - a)

    def inverse_lerp(x, a, b):
        return (x - a) / (b - a)
    
    t_x = inverse_lerp(proj_2d[0], x_range[0], x_range[1])
    t_y = inverse_lerp(proj_2d[1], y_range[0], y_range[1])

    lerp_3d_x1 = lerp(win_RB_3D_3, win_RB_3D_2, t_x)
    lerp_3d_x2 = lerp(win_RB_3D_4, win_RB_3D_1, t_x)

    lerp_3d = lerp(lerp_3d_x1, lerp_3d_x2, t_y)

    return lerp_3d

# for rotation_order in all_rotation_orders:
def process_data(rotation_order):
    sequence_code = sys.argv[1]
    # files = os.listdir(f'raw_data_exp2/{sequence_code}')
    # print(files)
    # for file in files:
    path_data = os.path.join(f'raw_data_exp2/{sequence_code}/' )
    print(f'Processing {path_data}')
    df = pd.read_csv(f'raw_data_exp2/{sequence_code}/{sequence_code}.csv')

    print(f'Processing {os.path.abspath(f"raw_data_exp2/{sequence_code}/{sequence_code}")}')

    # Using pandas, column headers are directly available as df.columns
    column_map = {col_name: idx for idx, col_name in enumerate(df.columns)}

    data_out = {
        'T1':{
            'eye_2d':[],
            'translation':[],
            'rot_mat':[],
            # 'rot_euler':[],
            'left_gaze_dir':[],
            'right_gaze_dir':[],
            'left_gaze_origin':[],
            'right_gaze_origin':[],
            'gaze_3d':[],
             'left_gaze_zoom':[],
            'right_gaze_zoom':[],
        },
        'T2':{
            'eye_2d':[],
            'translation':[],
            'rot_mat':[],
            # 'rot_euler':[],
            'left_gaze_dir':[],
            'right_gaze_dir':[],
            'left_gaze_origin':[],
            'right_gaze_origin':[],
            'gaze_3d':[],
            'left_gaze_zoom':[],
            'right_gaze_zoom':[],
        },
        'win':{
            'translation':[],
            'rot_mat':[],
        },
        'win.RB.1':{
            'translation':[],
        },
        'win.RB.2':{
            'translation':[],
        },
        'win.RB.3':{
            'translation':[],
        },
        'win.RB.4':{
            'translation':[],
        },
        'eye_contact':{
            'T1':[0]*len(df),
            'T2':[0]*len(df),
            'Mutual':[0]*len(df),
        },
    }
    #add new columns to df 
    #T1.leftGazeOrigin.XW, T1.leftGazeOrigin.YW, T1.leftGazeOrigin.ZW, T1.rightGazeOrigin.XW, T1.rightGazeOrigin.YW, T1.rightGazeOrigin.ZW
    #T1.leftGazeDirection.XW,T1.leftGazeDirection.YW, T1.leftGazeDirection.ZW, T1.rightGazeDirection.XW. T1.rightGazeDirection.YW, T1.rightGazeDirection.ZW, 
    #T1.gaze3D.XW, T1.gaze3D.YW, T1.gaze3D.ZW
    #T2.leftGazeOrigin.XW, T2.leftGazeOrigin.YW, T2.leftGazeOrigin.ZW, T2.rightGazeOrigin.XW, T2.rightGazeOrigin.YW, T2.rightGazeOrigin.ZW
    #T2.leftGazeDirection.XW,T2.leftGazeDirection.YW, T2.leftGazeDirection.ZW, T2.rightGazeDirection.XW. T2.rightGazeDirection.YW, T2.rightGazeDirection.ZW,
    #T2.gaze3D.XW, T2.gaze3D.YW, T2.gaze3D.ZW

    df['T1.leftGazeOrigin.XW'] = 0
    df['T1.leftGazeOrigin.YW'] = 0
    df['T1.leftGazeOrigin.ZW'] = 0
    df['T1.rightGazeOrigin.XW'] = 0
    df['T1.rightGazeOrigin.YW'] = 0
    df['T1.rightGazeOrigin.ZW'] = 0
    df['T1.leftGazeDirection.XW'] = 0
    df['T1.leftGazeDirection.YW'] = 0
    df['T1.leftGazeDirection.ZW'] = 0
    df['T1.rightGazeDirection.XW'] = 0
    df['T1.rightGazeDirection.YW'] = 0
    df['T1.rightGazeDirection.ZW'] = 0

    df['T1.leftGazeOrigin.Xzoom'] = 0
    df['T1.leftGazeOrigin.Yzoom'] = 0
    df['T1.leftGazeOrigin.Zzoom'] = 0
    df['T1.rightGazeOrigin.Xzoom'] = 0
    df['T1.rightGazeOrigin.Yzoom'] = 0
    df['T1.rightGazeOrigin.Zzoom'] = 0

    df['T1.gaze3D.XW'] = 0
    df['T1.gaze3D.YW'] = 0
    df['T1.gaze3D.ZW'] = 0

    df['T2.leftGazeOrigin.XW'] = 0
    df['T2.leftGazeOrigin.YW'] = 0
    df['T2.leftGazeOrigin.ZW'] = 0
    df['T2.rightGazeOrigin.XW'] = 0
    df['T2.rightGazeOrigin.YW'] = 0
    df['T2.rightGazeOrigin.ZW'] = 0
    df['T2.leftGazeDirection.XW'] = 0
    df['T2.leftGazeDirection.YW'] = 0
    df['T2.leftGazeDirection.ZW'] = 0
    df['T2.rightGazeDirection.XW'] = 0
    df['T2.rightGazeDirection.YW'] = 0
    df['T2.rightGazeDirection.ZW'] = 0

    df['T2.leftGazeOrigin.Xzoom'] = 0
    df['T2.leftGazeOrigin.Yzoom'] = 0
    df['T2.leftGazeOrigin.Zzoom'] = 0
    df['T2.rightGazeOrigin.Xzoom'] = 0
    df['T2.rightGazeOrigin.Yzoom'] = 0
    df['T2.rightGazeOrigin.Zzoom'] = 0



    df['T2.gaze3D.XW'] = 0
    df['T2.gaze3D.YW'] = 0
    df['T2.gaze3D.ZW'] = 0
    theta_t1 = -0.10390170359667145
    offset_rotation_t1 = R.from_euler('x', theta_t1)
    offset_rotation_t1 = offset_rotation_t1.as_matrix()
    theta_t2 = -0.15253803537296742
    offset_rotation_t2 = R.from_euler('x', theta_t2)
    offset_rotation_t2 = offset_rotation_t2.as_matrix()

    #zoom trasnfromation  values
#     Estimated Transformation Matrix
#  [[-6.43329008e-04  4.96780876e-06  3.29838331e-04  8.85720183e-03]
#  [-8.69738291e-06 -5.90462285e-04  4.57856005e-04  9.99960233e-01]
#  [-1.19663297e-08  1.84017864e-08  3.18665571e-07 -3.35796108e-05]]
    #zoom transformation matrix
    zoom_transformation = np.array([[-6.43329008e-04, 4.96780876e-06, 3.29838331e-04, 8.85720183e-03], [-8.69738291e-06, -5.90462285e-04, 4.57856005e-04, 9.99960233e-01], [-1.19663297e-08, 1.84017864e-08, 3.18665571e-07, -3.35796108e-05]])     

    for row in tqdm(range(2,len(df))):

        # DEBUG
        # x = df.iloc[row][column_map['T1.leftGazeOrigin.X']
        # y = df.iloc[row][column_map['T1.leftGazeOrigin.Y']
        # z = df.iloc[row][column_map['T1.leftGazeOrigin.Z']
        # left_o = np.array([x,y,z]).astype(np.float32)
        # x = df.iloc[row][column_map['T1.rightGazeOrigin.X']
        # y = df.iloc[row][column_map['T1.rightGazeOrigin.Y']
        # z = df.iloc[row][column_map['T1.rightGazeOrigin.Z']
        # right_o = np.array([x,y,z]).astype(np.float32)
        # print(left_o,right_o)

        # ========================================

        # # # extract T1 2d eye gaze
        #check if file has any T1 columns
        if 'T1.gaze2D.X'  in column_map:
            x = df.iloc[row][column_map['T1.gaze2D.X']]
            y = df.iloc[row][column_map['T1.gaze2D.Y']]
            data_out['T1']['eye_2d'].append(np.array([x,y]).astype(np.float32))
            # # extract T1 position
            x = df.iloc[row][column_map['T1.TX']]
            y = df.iloc[row][column_map['T1.TY']]
            z = df.iloc[row][column_map['T1.TZ']]
            pos = np.array([x,y,z])
            data_out['T1']['translation'].append(pos.astype(np.float32))

            # extract T1 Quaternion rotation
            x = df.iloc[row][column_map['T1.RX']]
            y = df.iloc[row][column_map['T1.RY']]
            z = df.iloc[row][column_map['T1.RZ']]
            w = df.iloc[row][column_map['T1.RW']]
            # rot = scipy.spatial.transform.Rotation.from_euler(rotation_order,[x,y,z],degrees=)
            rot = scipy.spatial.transform.Rotation.from_quat([x,y,z,w])
            data_out['T1']['rot_mat'].append(rot.as_matrix().astype(np.float32))
            #convert quat to eular degrees

            # data_out['T1']['rot_euler'].append(np.array([x,y,z,w]).astype(np.float32))

            # # extract T1 gaze origin
            x = df.iloc[row][column_map['T1.leftGazeOrigin.X']]
            y = df.iloc[row][column_map['T1.leftGazeOrigin.Y']]
            z = df.iloc[row][column_map['T1.leftGazeOrigin.Z']]
            gaze_origin_vector = np.array([x,y,z])
            gaze_origin_vector = offset_rotation_t1 @ gaze_origin_vector
            gaze_origin_vector = rot.as_matrix() @ gaze_origin_vector + pos
            data_out['T1']['left_gaze_origin'].append(gaze_origin_vector.astype(np.float32))
            df.at[row,'T1.leftGazeOrigin.XW'] = gaze_origin_vector[0]
            df.at[row,'T1.leftGazeOrigin.YW'] = gaze_origin_vector[1]
            df.at[row,'T1.leftGazeOrigin.ZW'] = gaze_origin_vector[2]

            x = df.iloc[row][column_map['T1.rightGazeOrigin.X']]
            y = df.iloc[row][column_map['T1.rightGazeOrigin.Y']]
            z = df.iloc[row][column_map['T1.rightGazeOrigin.Z']]
            gaze_origin_vector = np.array([x,y,z])
            gaze_origin_vector = offset_rotation_t1 @ gaze_origin_vector
            gaze_origin_vector = rot.as_matrix() @ gaze_origin_vector + pos
            data_out['T1']['right_gaze_origin'].append(gaze_origin_vector.astype(np.float32))
            df.at[row,'T1.rightGazeOrigin.XW'] = gaze_origin_vector[0]
            df.at[row,'T1.rightGazeOrigin.YW'] = gaze_origin_vector[1]
            df.at[row,'T1.rightGazeOrigin.ZW'] = gaze_origin_vector[2]

            # # extract T1 gaze dir
            x = df.iloc[row][column_map['T1.leftGazeDirection.X']]
            y = df.iloc[row][column_map['T1.leftGazeDirection.Y']]
            z = df.iloc[row][column_map['T1.leftGazeDirection.Z']]
            gaze_dir_vector = np.array([x,y,z])
            gaze_dir_vector = offset_rotation_t1 @ gaze_dir_vector
            gaze_dir_vector = rot.as_matrix() @ gaze_dir_vector
            data_out['T1']['left_gaze_dir'].append(gaze_dir_vector.astype(np.float32))

            df.at[row,'T1.leftGazeDirection.XW'] = gaze_dir_vector[0]
            df.at[row,'T1.leftGazeDirection.YW'] = gaze_dir_vector[1]
            df.at[row,'T1.leftGazeDirection.ZW'] = gaze_dir_vector[2]

            x = df.iloc[row][column_map['T1.rightGazeDirection.X']]
            y = df.iloc[row][column_map['T1.rightGazeDirection.Y']]
            z = df.iloc[row][column_map['T1.rightGazeDirection.Z']]
            gaze_dir_vector = np.array([x,y,z])
            gaze_dir_vector = offset_rotation_t1 @ gaze_dir_vector
            gaze_dir_vector = rot.as_matrix() @ gaze_dir_vector
            data_out['T1']['right_gaze_dir'].append(gaze_dir_vector.astype(np.float32))
            df.at[row,'T1.rightGazeDirection.XW'] = gaze_dir_vector[0]
            df.at[row,'T1.rightGazeDirection.YW'] = gaze_dir_vector[1]
            df.at[row,'T1.rightGazeDirection.ZW'] = gaze_dir_vector[2]

            # #extract T1 3d gaze
            x = df.iloc[row][column_map['T1.gaze3D.X']]
            y = df.iloc[row][column_map['T1.gaze3D.Y']]
            z = df.iloc[row][column_map['T1.gaze3D.Z']]
            gaze_3d = np.array([x,y,z])
            gaze_3d = offset_rotation_t1 @ gaze_3d
            gaze_3d = rot.as_matrix() @ gaze_3d + pos
            data_out['T1']['gaze_3d'].append(gaze_3d.astype(np.float32))

            df.at[row,'T1.gaze3D.XW'] = gaze_3d[0]
            df.at[row,'T1.gaze3D.YW'] = gaze_3d[1]
            df.at[row,'T1.gaze3D.ZW'] = gaze_3d[2]

        if 'T2.gaze2D.X' in column_map:
            # # extract T2 2d eye gaze
            x = df.iloc[row][column_map['T2.gaze2D.X']]
            y = df.iloc[row][column_map['T2.gaze2D.Y']]
            data_out['T2']['eye_2d'].append(np.array([x,y]).astype(np.float32))

            # extract T2 position
            x = df.iloc[row][column_map['T2.TX']]
            y = df.iloc[row][column_map['T2.TY']]
            z = df.iloc[row][column_map['T2.TZ']]
            pos = np.array([x,y,z])
            data_out['T2']['translation'].append(pos.astype(np.float32))

            # # extract T2 euler rotation
            x = df.iloc[row][column_map['T2.RX']]
            y = df.iloc[row][column_map['T2.RY']]
            z = df.iloc[row][column_map['T2.RZ']]
            w = df.iloc[row][column_map['T2.RW']]
            # rot = scipy.spatial.transform.Rotation.from_euler(rotation_order,[x,y,z],degrees=)
            rot = scipy.spatial.transform.Rotation.from_quat([x,y,z,w])
            t2_final_rot = rot.as_matrix() 
            data_out['T2']['rot_mat'].append(t2_final_rot.astype(np.float32))
            # data_out['T2']['rot_euler'].append(np.array([x,y,z]).astype(np.float32))

            # extract T2 gaze origin
            x = df.iloc[row][column_map['T2.leftGazeOrigin.X']]
            y = df.iloc[row][column_map['T2.leftGazeOrigin.Y']]
            z = df.iloc[row][column_map['T2.leftGazeOrigin.Z']]
            gaze_origin_vector = np.array([x,y,z])
            gaze_origin_vector = offset_rotation_t2 @ gaze_origin_vector
            gaze_origin_vector = t2_final_rot @ gaze_origin_vector + pos
            data_out['T2']['left_gaze_origin'].append(gaze_origin_vector.astype(np.float32))
            df.at[row,'T2.leftGazeOrigin.XW'] = gaze_origin_vector[0]
            df.at[row,'T2.leftGazeOrigin.YW'] = gaze_origin_vector[1]
            df.at[row,'T2.leftGazeOrigin.ZW'] = gaze_origin_vector[2]

            x = df.iloc[row][column_map['T2.rightGazeOrigin.X']]
            y = df.iloc[row][column_map['T2.rightGazeOrigin.Y']]
            z = df.iloc[row][column_map['T2.rightGazeOrigin.Z']]
            gaze_origin_vector = np.array([x,y,z])
            gaze_origin_vector = offset_rotation_t2 @ gaze_origin_vector
            gaze_origin_vector = t2_final_rot @ gaze_origin_vector + pos
            data_out['T2']['right_gaze_origin'].append(gaze_origin_vector.astype(np.float32))
        
            df.at[row,'T2.rightGazeOrigin.XW'] = gaze_origin_vector[0]
            df.at[row,'T2.rightGazeOrigin.YW'] = gaze_origin_vector[1]
            df.at[row,'T2.rightGazeOrigin.ZW'] = gaze_origin_vector[2]

            # extract T2 gaze dir
            x = df.iloc[row][column_map['T2.leftGazeDirection.X']]
            y = df.iloc[row][column_map['T2.leftGazeDirection.Y']]
            z = df.iloc[row][column_map['T2.leftGazeDirection.Z']]
            gaze_dir_vector = np.array([x,y,z])
            gaze_dir_vector = offset_rotation_t2 @ gaze_dir_vector
            gaze_dir_vector = t2_final_rot @ gaze_dir_vector
            data_out['T2']['left_gaze_dir'].append(gaze_dir_vector.astype(np.float32))

            df.at[row,'T2.leftGazeDirection.XW'] = gaze_dir_vector[0]
            df.at[row,'T2.leftGazeDirection.YW'] = gaze_dir_vector[1]
            df.at[row,'T2.leftGazeDirection.ZW'] = gaze_dir_vector[2]

            x = df.iloc[row][column_map['T2.rightGazeDirection.X']]
            y = df.iloc[row][column_map['T2.rightGazeDirection.Y']]
            z = df.iloc[row][column_map['T2.rightGazeDirection.Z']]
            gaze_dir_vector = np.array([x,y,z])
            gaze_dir_vector = offset_rotation_t2 @ gaze_dir_vector
            gaze_dir_vector = t2_final_rot @ gaze_dir_vector
            data_out['T2']['right_gaze_dir'].append(gaze_dir_vector.astype(np.float32))
            
            df.at[row,'T2.rightGazeDirection.XW'] = gaze_dir_vector[0]
            df.at[row,'T2.rightGazeDirection.YW'] = gaze_dir_vector[1]
            df.at[row,'T2.rightGazeDirection.ZW'] = gaze_dir_vector[2]

            #extract T2 3d gaze
            x = df.iloc[row][column_map['T2.gaze3D.X']]
            y = df.iloc[row][column_map['T2.gaze3D.Y']]
            z = df.iloc[row][column_map['T2.gaze3D.Z']]
            gaze_3d = np.array([x,y,z])
            gaze_3d = offset_rotation_t2 @ gaze_3d
            gaze_3d = rot.as_matrix() @ gaze_3d + pos
            data_out['T2']['gaze_3d'].append(gaze_3d.astype(np.float32))

            df.at[row,'T2.gaze3D.XW'] = gaze_3d[0]
            df.at[row,'T2.gaze3D.YW'] = gaze_3d[1]
            df.at[row,'T2.gaze3D.ZW'] = gaze_3d[2]
            

        #Extract win position RB.1
        if 'win.RB.1.X' not in column_map:
            continue
        #2D win data 
        #(2732, 2048, 3)
        win_RB_2D_1 = np.array([2048,2732])
        win_RB_2D_2 = np.array([2048,0])
        win_RB_2D_3 = np.array([0,0])
        win_RB_2D_4 = np.array([0,2732])

        x = df.iloc[row][column_map['win.RB.1.X']]
        y = df.iloc[row][column_map['win.RB.1.Y']]
        z = df.iloc[row][column_map['win.RB.1.Z']]
        pos = np.array([x,y,z])
        data_out['win.RB.1']['translation'].append(pos.astype(np.float32))

        #Extract win RB. 2 position
        x = df.iloc[row][column_map['win.RB.2.X']]
        y = df.iloc[row][column_map['win.RB.2.Y']]
        z = df.iloc[row][column_map['win.RB.2.Z']]
        pos = np.array([x,y,z])
        data_out['win.RB.2']['translation'].append(pos.astype(np.float32))

        #Extract win RB. 3 position
        x = df.iloc[row][column_map['win.RB.3.X']]
        y = df.iloc[row][column_map['win.RB.3.Y']]
        z = df.iloc[row][column_map['win.RB.3.Z']]
        pos = np.array([x,y,z])
        data_out['win.RB.3']['translation'].append(pos.astype(np.float32))

        #Extract win RB. 4 position
        x = df.iloc[row][column_map['win.RB.4.X']]
        y = df.iloc[row][column_map['win.RB.4.Y']]
        z = df.iloc[row][column_map['win.RB.4.Z']]
        pos = np.array([x,y,z])
        data_out['win.RB.4']['translation'].append(pos.astype(np.float32))
        x = df.iloc[row][column_map['win.PX']]
        y = df.iloc[row][column_map['win.PY']]
        z = df.iloc[row][column_map['win.PZ']]
        pos = np.array([x,y,z])
        data_out['win']['translation'].append(pos.astype(np.float32))

        #Extract win rotation
        x = df.iloc[row][column_map['win.RX']]
        y = df.iloc[row][column_map['win.RY']]
        z = df.iloc[row][column_map['win.RZ']]
        w = df.iloc[row][column_map['win.RW']]
        #if x,y,z,w are nan fill in data with the last not nan
        if np.isnan(x) and np.isnan(y) and np.isnan(z) and np.isnan(w):
            print(row)
            df['win.RX'][row] = df['win.RX'][row-1]
            df['win.RY'][row] = df['win.RY'][row-1]
            df['win.RZ'][row] = df['win.RZ'][row-1]
            df['win.RW'][row] = df['win.RW'][row-1]
            x = df.iloc[row][column_map['win.RX']]
            y = df.iloc[row][column_map['win.RY']]
            z = df.iloc[row][column_map['win.RZ']]
            w = df.iloc[row][column_map['win.RW']]


        rot = scipy.spatial.transform.Rotation.from_quat([x,y,z,w])
        
        data_out['win']['rot_mat'].append(rot.as_matrix().astype(np.float32))

        #zoom gaze data T1
        # point = np.hstack([point, 1])
        # #apply the transformation matrix to the point
        # #convert 3D point to 2D point using t_mat
        # proj_h = np.dot(point, t_mat.T)
        # #normalize homogeneous coordinates to obtain non-homogeneous 2D points
        # proj_2d = proj_h[:2] / proj_h[2]
        # print('Projected 2D Point\n', proj_2d)
        # # extract T1 gaze origin
        win_RB_3D_1 = np.array([df.iloc[row][column_map['win.RB.1.X']],df.iloc[row][column_map['win.RB.1.Y']],df.iloc[row][column_map['win.RB.1.Z']]])
        win_RB_3D_2 = np.array([df.iloc[row][column_map['win.RB.2.X']],df.iloc[row][column_map['win.RB.2.Y']],df.iloc[row][column_map['win.RB.2.Z']]])
        win_RB_3D_3 = np.array([df.iloc[row][column_map['win.RB.3.X']],df.iloc[row][column_map['win.RB.3.Y']],df.iloc[row][column_map['win.RB.3.Z']]])
        win_RB_3D_4 = np.array([df.iloc[row][column_map['win.RB.4.X']],df.iloc[row][column_map['win.RB.4.Y']],df.iloc[row][column_map['win.RB.4.Z']]])

        #zoom for T1 left gaze origin
        x = df.iloc[row][column_map['T1.leftGazeOrigin.X']]
        y = df.iloc[row][column_map['T1.leftGazeOrigin.Y']]
        z = df.iloc[row][column_map['T1.leftGazeOrigin.Z']]
        gaze_origin_vector = np.array([x,y,z])
        gaze_origin_vector = offset_rotation_t1 @ gaze_origin_vector
        gaze_origin_vector = rot.as_matrix() @ gaze_origin_vector + pos
        gaze_origin_vector = zoom_transform(gaze_origin_vector, zoom_transformation, win_RB_3D_1, win_RB_3D_2, win_RB_3D_3, win_RB_3D_4, rotation_order)
        df.at[row,'T1.leftGazeOrigin.Xzoom'] = gaze_origin_vector[0]
        df.at[row,'T1.leftGazeOrigin.Yzoom'] = gaze_origin_vector[1]
        df.at[row,'T1.leftGazeOrigin.Zzoom'] = gaze_origin_vector[2]
        data_out['T1']['left_gaze_zoom'].append(gaze_origin_vector.astype(np.float32))

        #zoom for T1 right gaze origin
        x = df.iloc[row][column_map['T1.rightGazeOrigin.X']]
        y = df.iloc[row][column_map['T1.rightGazeOrigin.Y']]
        z = df.iloc[row][column_map['T1.rightGazeOrigin.Z']]
        gaze_origin_vector = np.array([x,y,z])
        gaze_origin_vector = offset_rotation_t1 @ gaze_origin_vector
        gaze_origin_vector = rot.as_matrix() @ gaze_origin_vector + pos
        gaze_origin_vector = zoom_transform(gaze_origin_vector, zoom_transformation, win_RB_3D_1, win_RB_3D_2, win_RB_3D_3, win_RB_3D_4, rotation_order)
        df.at[row,'T1.rightGazeOrigin.Xzoom'] = gaze_origin_vector[0]
        df.at[row,'T1.rightGazeOrigin.Yzoom'] = gaze_origin_vector[1]
        df.at[row,'T1.rightGazeOrigin.Zzoom'] = gaze_origin_vector[2]
        data_out['T1']['right_gaze_zoom'].append(gaze_origin_vector.astype(np.float32))



        # zoom for T2 left gaze origin
        x = df.iloc[row][column_map['T2.leftGazeOrigin.X']]
        y = df.iloc[row][column_map['T2.leftGazeOrigin.Y']]
        z = df.iloc[row][column_map['T2.leftGazeOrigin.Z']]
        gaze_origin_vector = np.array([x,y,z])
        gaze_origin_vector = offset_rotation_t2 @ gaze_origin_vector
        gaze_origin_vector = t2_final_rot @ gaze_origin_vector + pos
        gaze_origin_vector = zoom_transform(gaze_origin_vector, zoom_transformation, win_RB_3D_1, win_RB_3D_2, win_RB_3D_3, win_RB_3D_4, rotation_order)
        df.at[row,'T2.leftGazeOrigin.Xzoom'] = gaze_origin_vector[0]
        df.at[row,'T2.leftGazeOrigin.Yzoom'] = gaze_origin_vector[1]
        df.at[row,'T2.leftGazeOrigin.Zzoom'] = gaze_origin_vector[2]
        data_out['T2']['left_gaze_zoom'].append(gaze_origin_vector.astype(np.float32))

        #zoom for T2 right gaze origin
        x = df.iloc[row][column_map['T2.rightGazeOrigin.X']]
        y = df.iloc[row][column_map['T2.rightGazeOrigin.Y']]
        z = df.iloc[row][column_map['T2.rightGazeOrigin.Z']]
        gaze_origin_vector = np.array([x,y,z])
        gaze_origin_vector = offset_rotation_t2 @ gaze_origin_vector
        gaze_origin_vector = t2_final_rot @ gaze_origin_vector + pos
        gaze_origin_vector = zoom_transform(gaze_origin_vector, zoom_transformation, win_RB_3D_1, win_RB_3D_2, win_RB_3D_3, win_RB_3D_4, rotation_order)
        df.at[row,'T2.rightGazeOrigin.Xzoom'] = gaze_origin_vector[0]
        df.at[row,'T2.rightGazeOrigin.Yzoom'] = gaze_origin_vector[1]
        df.at[row,'T2.rightGazeOrigin.Zzoom'] = gaze_origin_vector[2]
        data_out['T2']['right_gaze_zoom'].append(gaze_origin_vector.astype(np.float32))
        



    #save df to new csv

          
    os.makedirs(f'exp2/{sequence_code}',exist_ok=True)
    df.to_csv(f'exp2/{sequence_code}/processed_{sequence_code}.csv',index=False)  
    np.save(f'exp2/{sequence_code}/extracted_data_{sequence_code}.npy',data_out)

all_rotation_orders = ['XYZ']
if __name__ == "__main__":
    with Pool(8) as p:
        p.map(process_data, all_rotation_orders)
