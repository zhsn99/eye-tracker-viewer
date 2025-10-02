


# Setup
Please use conda and setup your python env using the included environment.yaml

# PREPROCESSING
You will have to convert the video/excel file before using this viewer.
1) Place the raw data into the `raw_data` directory.
2) Use `preprocess_motive.py <sequence_code>` to preprocess the data, it extracts some of the fields and converts the rotations, see the script for more details.
3) Use `convert_json_motive.py <sequence_code>` to convert the data to json, which is read by the web based visualizer.
4) Use `eye_contact_viewer.py <sequence_code>` to generate 2d images of gaze 3D and gaze origins.
5) Use `crop_video.py <sequence_code>` to crop videos according to the syncronization time.
5) Use `./extract_frames.sh <sequence_code>` extract the frames of the video into images.

After following these steps, all the data should be ready to run the visualization, check cure_data2 folder and see if all the data is avaible under the `<sequence_code>` folder.

# Visualizing
Run `./serve.py`, which will run a local web server on port `8080`. 
Open `localhost:8080` in a web browser to view the visualization.

# Steps 
1) Set the camera: `Viewer camera world transform` 
2) Choose the order of Transformation, since we are using motive data choose `XYZ` order.
3) Enter the `<sequence_code>` and press the `Load` button.
4) Now, press the `Play capture` button.
5) There are some other controling buttons like skiping or stoppins, you can use them as well.
6) Click on the 3D visualuzation and move around using your touch pad or mouse, you can also use arrow keys to "walk" around the scene, Q and E to move up and down, click and drag to rotate the camera.
I have also loaded a default `Viewer camera world transform` that move the camera to look at the participants in this example.
