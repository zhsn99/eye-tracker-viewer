import * as THREE from 'three';
import * as JSZIP from 'jszip';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { get_free_tform_from_ae, add_lights, add_axis_indicator, add_grid } from '/utils.js';

// helpers for rendering
let scene = null;
let renderer = null;
let camera = null;

// helpers for mouse interface
let mouse_is_down = false;
let mouse_velocity_x = 0;
let mouse_velocity_y = 0;

// helpers for camera motion with keyboard
let camera_forward_velocity = 0;
let camera_right_velocity = 0;
let camera_up_velocity = 0;
let move_forward_basis = new THREE.Vector3(0,0,-1);
let move_right_basis = new THREE.Vector3(1,0,0);
//let move_up_basis = new THREE.Vector3(0,1,0);
let move_up_basis = new THREE.Vector3(0,1,0); // this one is using our up

// helpers for camera rotation
let camera_azimuth = 0.5;
let camera_elevation = -0.6;
let camera_radius = 5; // unused currently, used for orbit motion
const viewer_container = document.getElementById('viewer');

// helpers visualizing eye tracking
let scene_content = {};
let tracking_data = null;
let pose_canonical_transform = null;
let is_playingback = false;
let plotting_data = {};

// scene offsets to place participants closer to the center of 3D space
let scale = 0.01;
let x_offset = 0;
let y_offset = 0;
let z_offset = -1000;
let eye_contact_frame = -1;
let p1_looking_at_p2_frame = -1;
let p2_looking_at_p1_frame = -1;
let file_name;
let p1 = true;
let p2 = true;
let win = true;
let twoD = true;
let eye_contact = true;
let zoom = true;

// view attachment state
let is_attached = false;
let is_attached1 = false;
function main(){
	// create scene, camera params: fov, aspect_ratio, near, far
	scene = new THREE.Scene();
	//scene.background = new THREE.Color( 0xffffff );
	scene.background = new THREE.Color( 0x000000 );
	camera = new THREE.PerspectiveCamera( 70, parseInt(viewer_container.style.width)/parseInt(viewer_container.style.height), 0.1, 1000 );
	camera.position.x = 4;
	camera.position.y = 4;
	camera.position.z = 7;

	// create renderer, put into main html document
	renderer = new THREE.WebGLRenderer({antialias:true});
	renderer.setSize( parseInt(viewer_container.style.width), parseInt(viewer_container.style.height) );
	viewer_container.appendChild(renderer.domElement);

	// Create Plotly plots within the specified containers
	// createPlot('T1_gaze_plot');
	// createPlot('T2_gaze_plot');

	//load file name using load_data_file
	


	// create frustrums to visualize the paticipants' glasses
	create_participant_elements();
	create_experiment_elements();
	// change_rot_order('XYZ');

	// light the scene up
	add_lights(scene);

	add_grid(scene,5,5);
	let grid_rot = new THREE.Matrix3(
		1,0,0,
		0,0,1,
		0,-1,0);
	add_grid(scene,20,10,new THREE.Vector3(0,15,-40), grid_rot);
	//add_axis_indicator(scene,new THREE.Vector3(1.5,-6.8,0));
	add_axis_indicator(scene,new THREE.Vector3(0,0,0.001));

	// start animation loop
	function animate() {
		// recalc camera pos
		camera_elevation += mouse_velocity_y*0.005;
		camera_azimuth += mouse_velocity_x*0.005;

		// move camera
		let camera_rot = get_free_tform_from_ae(camera_azimuth,camera_elevation);
		let rot_quat = new THREE.Quaternion();
		rot_quat.setFromRotationMatrix(camera_rot);
		let camera_new_pos = new THREE.Vector3();
		camera_new_pos.copy(camera.position);

		let temp_move = new THREE.Vector3();
		temp_move.copy(move_forward_basis);
		temp_move.applyMatrix4(camera_rot);
		temp_move.y = 0;
		temp_move.normalize();
		temp_move.multiplyScalar(camera_forward_velocity);
		camera_new_pos.add(temp_move);

		temp_move.copy(move_right_basis);
		temp_move.applyMatrix4(camera_rot);
		temp_move.y = 0;
		temp_move.normalize();
		temp_move.multiplyScalar(camera_right_velocity);
		camera_new_pos.add(temp_move);

		temp_move.copy(move_up_basis);
		temp_move.multiplyScalar(camera_up_velocity);
		camera_new_pos.add(temp_move);

		// compute new pos
		camera.position.copy(camera_new_pos);

		camera.quaternion.x = rot_quat.x;
		camera.quaternion.y = rot_quat.y;
		camera.quaternion.z = rot_quat.z;
		camera.quaternion.w = rot_quat.w;

		// overwrite camera transform to attach camera to participant
		if (is_attached1){
			let pos = scene_content['participants'][0][0].position;
			let rot = scene_content['participants'][0][0].quaternion;
			let poop = -3.14159/2;
			// let rot_offset = new THREE.Matrix4(
			// 	Math.cos(poop),0,Math.sin(poop),0,
			// 	0,1,0,0,
			// 	-Math.sin(poop),0,Math.cos(poop),0,
			// 	0,0,0,1
			// );
			let rot_offset_x = new THREE.Matrix4(
				1,0,0,0,
				0,Math.cos(poop),-Math.sin(poop),0,
				0,Math.sin(poop),Math.cos(poop),0,
				0,0,0,1
			);
			poop = -3.14159/4;
			let rot_offset_z = new THREE.Matrix4(
				Math.cos(poop),-Math.sin(poop),0,0,
				Math.sin(poop),Math.cos(poop),0,0,
				0,0,1,0,
				0,0,0,1
			);
			let rot_offset_quat_x = new THREE.Quaternion();
			let rot_offset_quat_z = new THREE.Quaternion();
			rot_offset_quat_x.setFromRotationMatrix(rot_offset_x);
			rot_offset_quat_z.setFromRotationMatrix(rot_offset_z);
			camera.position.copy(pos);
			camera.quaternion.copy(rot);
			camera.quaternion.multiply(rot_offset_quat_x);
			camera.quaternion.multiply(rot_offset_quat_z);
		}
		if (is_attached){
			let pos = scene_content['participants'][1][0].position;
			let rot = scene_content['participants'][1][0].quaternion;
			let poop = -3.14159/2;
			// let rot_offset = new THREE.Matrix4(
			// 	Math.cos(poop),0,Math.sin(poop),0,
			// 	0,1,0,0,
			// 	-Math.sin(poop),0,Math.cos(poop),0,
			// 	0,0,0,1
			// );
			let rot_offset_x = new THREE.Matrix4(
				1,0,0,0,
				0,Math.cos(poop),-Math.sin(poop),0,
				0,Math.sin(poop),Math.cos(poop),0,
				0,0,0,1
			);
			poop = -3.14159/4;
			let rot_offset_z = new THREE.Matrix4(
				Math.cos(poop),-Math.sin(poop),0,0,
				Math.sin(poop),Math.cos(poop),0,0,
				0,0,1,0,
				0,0,0,1
			);
			let rot_offset_quat_x = new THREE.Quaternion();
			let rot_offset_quat_z = new THREE.Quaternion();
			rot_offset_quat_x.setFromRotationMatrix(rot_offset_x);
			rot_offset_quat_z.setFromRotationMatrix(rot_offset_z);
			camera.position.copy(pos);
			camera.quaternion.copy(rot);
			camera.quaternion.multiply(rot_offset_quat_x);
			camera.quaternion.multiply(rot_offset_quat_z);
		}

		// update UI with current camera pose
		document.getElementById('pos_x').value = camera.position.x;
		document.getElementById('pos_y').value = camera.position.y;
		document.getElementById('pos_z').value = camera.position.z;
		document.getElementById('azi').value = camera_azimuth;
		document.getElementById('ele').value = camera_elevation;
		document.getElementById('camera_tform_serialized_out').value = `${camera.position.x},${camera.position.y},${camera.position.z},${camera_azimuth},${camera_elevation}`;

		requestAnimationFrame( animate );
		renderer.render( scene, camera );
	}
	animate();
}



// ====================================================================================

// create the scene elements for the participants
// also stores the canonical transform
function create_experiment_elements(){
	let elements ={
		'win':0xff0000,
		'win.RB.1':0xff7c00,//orange
		'win.RB.2':0xfffe00,//yellow
		'win.RB.3':0x04ffff,//light blue
		'win.RB.4':0x00ff00,//light green
	};
	scene_content['win'] = [];
	if(win){
		for (let w in elements){
			let cur_pose_elements = [];
			const window_size = 0.1
			const window_material = new THREE.MeshLambertMaterial( { color: elements[w] } );
			const window_geometry = new THREE.SphereGeometry( window_size, 32, 16 ); 
			const window_sphere = new THREE.Mesh( window_geometry, window_material );
			scene.add( window_sphere );
			cur_pose_elements.push(window_sphere);
			scene_content['win'].push(cur_pose_elements);

		};
		
	}
	else{
		//do nothing
	}

};
function create_participant_elements(){
	//t1_left yello
	//t1 right red
	//t2 left blue
	//t2 right green
	let participants = { // set participant colours
		'T1':0xff0000,
		'T2':0x00ff00,
		'zoom': 0xffffff,
		// 'Window':0xcccccc,
		// 'T1_left':0xffff00,
		// 'T1_right':0xff0000,
		// 'T2_left':0x00ffff,
		// 'T2_right':0x00ff00
		//white color code 0xffffff
	};

	// draw poses
	scene_content['participants'] = [];
	for (let par in participants){
		if (par == 'T1' && p1 == false){
			console.log('p1 is false*********************');
			continue;
		}
		if (par == 'T2' && p2 == false){
			console.log('p2 is false*********************');
			continue;
		}
		let cur_pose_elements = [];
		const cone_size = 1.00;
		const geometry = new THREE.ConeGeometry( cone_size, cone_size*2, 4 ); 
		const material = new THREE.MeshLambertMaterial( { color: participants[par] } );
		material.opacity = 0.3;
		material.transparent = true;
		const cone = new THREE.Mesh( geometry, material );
		scene.add( cone );
		cur_pose_elements.push(cone);

		const wireframe = new THREE.WireframeGeometry( geometry );
		let line_material = new THREE.LineBasicMaterial({color: participants[par]})
		let line = new THREE.LineSegments( wireframe,line_material );
		line.material.depthTest = true;
		line.material.opacity = 0.8;
		line.material.transparent = true;
		//line.material.depthTest = false;
		scene.add( line );
		cur_pose_elements.push(line);

		// create eye balls
		const eye_size = 0.25
		const eye_material = new THREE.MeshLambertMaterial( { color: participants[par] } );
		const le_geometry = new THREE.SphereGeometry( eye_size, 32, 16 ); 
		const le_sphere = new THREE.Mesh( le_geometry, eye_material );
		scene.add( le_sphere );
		cur_pose_elements.push(le_sphere);

		const re_geometry = new THREE.SphereGeometry( eye_size, 32, 16 ); 
		const re_sphere = new THREE.Mesh( re_geometry, eye_material );
		scene.add( re_sphere );
		cur_pose_elements.push(re_sphere);

		// create eye rays
		let ray_length = 5;
		let le_arrow = new THREE.ArrowHelper(new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 1, 0, 0 ), ray_length, participants[par],0.2,0.2);
		scene.add(le_arrow);
		let re_arrow = new THREE.ArrowHelper(new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 1, 0, 0 ), ray_length, participants[par],0.2,0.2);
		scene.add(re_arrow);
		cur_pose_elements.push(le_arrow);
		cur_pose_elements.push(re_arrow);

		// create gaze trasnparent sphere
		const gaze_size = 0.2
		const gaze_material = new THREE.MeshLambertMaterial( { color: participants[par] } );
		gaze_material.opacity = 0.5;
		gaze_material.transparent = true;
		const gaze_geometry = new THREE.SphereGeometry( gaze_size, 32, 16 );
		const gaze_sphere = new THREE.Mesh( gaze_geometry, gaze_material );
		scene.add( gaze_sphere );
		cur_pose_elements.push(gaze_sphere);

		if(zoom){
			const zoom_size = 0.1 
			const zoom_material = new THREE.MeshLambertMaterial( { color: participants['zoom'] } );
			zoom_material.opacity = 0.5;
			zoom_material.transparent = true;
			const zoom_geometry = new THREE.SphereGeometry( zoom_size, 32, 16 );
			const zoom_sphere = new THREE.Mesh( zoom_geometry, zoom_material );
			scene.add( zoom_sphere );
			cur_pose_elements.push(zoom_sphere);
		}


		// rotates camera to point down like in blender, also rotates 4 sided cone to correct orientation
		let canonical_transform = new THREE.Matrix4( // transforms to blender camera down
			0.707,0,0.707,0,
			0.707,0,-0.707,0,
			0,1,0,-cone_size,
			0,0,0,1
		);
		let canonical_transform_final = new THREE.Matrix4( // points frustrum to Z+
			-1,0,0,0,
			0,1,0,0,
			0,0,-1,0,
			0,0,0,1
		);
		// compose the transforms
		canonical_transform_final.multiply(canonical_transform);
		pose_canonical_transform = canonical_transform_final; // save globally, needed every time we update pose
		
		cone.setRotationFromMatrix(canonical_transform_final);
		line.setRotationFromMatrix(canonical_transform_final);

		cone.position.setFromMatrixPosition(canonical_transform_final);
		line.position.setFromMatrixPosition(canonical_transform_final);
		scene_content['participants'].push(cur_pose_elements);
	}
}

function change_3d_vis(vis_type){
	console.log('*******************vis_type*****************', vis_type);
	if (vis_type == 'Win'){
		//window vis show the window
				win = false;
			}
	if (vis_type == '2d_eyes'){
			twoD = false;
	}
	if (vis_type == 'zoom'){
		zoom = false;
	}
	if (vis_type == 'P2'){
		p2 = false;
	}
	if (vis_type == 'P1'){
		p1 = false;
	}
	if (vis_type == 'eye_contact'){
		eye_contact = false;
	}

}
// loads data for specific rot order
// This call is asyncronous since it takes time for the json to load, code runs once file is loaded


// updates the 3D vis of a participant's head
// hacky, assumes each participant has 2 scene elements that need updating
function update_3d_gaze(participant_elements,gaze_3d)
{
	let x = (gaze_3d[0] + x_offset) * scale;
	let y = (gaze_3d[1] + y_offset) * scale;
	let z = (gaze_3d[2] + z_offset) * scale;
	participant_elements[6].position.set(x,y,z);

}
function update_eye_pose_vis(participant_elements,left_gaze_origin,right_gaze_origin,left_gaze_dir,right_gaze_dir){
	let x = (left_gaze_origin[0] + x_offset) * scale;
	let y = (left_gaze_origin[1] + y_offset) * scale;
	let z = (left_gaze_origin[2] + z_offset) * scale;
	participant_elements[2].position.set(x,y,z);
	participant_elements[4].position.set(x,y,z);

	x = (right_gaze_origin[0] + x_offset) * scale;
	y = (right_gaze_origin[1] + y_offset) * scale;
	z = (right_gaze_origin[2] + z_offset) * scale;
	participant_elements[3].position.set(x,y,z);
	participant_elements[5].position.set(x,y,z);

	participant_elements[4].setDirection(new THREE.Vector3(left_gaze_dir[0],left_gaze_dir[1],left_gaze_dir[2]));
	participant_elements[5].setDirection(new THREE.Vector3(right_gaze_dir[0],right_gaze_dir[1],right_gaze_dir[2]));
}
function update_head_pose_vis(participant_elements,pos_list,rot_list){

	let x = (pos_list[0] + x_offset) * scale;
	let y = (pos_list[1] + y_offset) * scale;
	let z = (pos_list[2] + z_offset) * scale;
	participant_elements[0].position.set(x,y,z);
	participant_elements[1].position.set(x,y,z);
	let mat_el_list = rot_list[0].concat([0]).concat(rot_list[1]).concat([0]).concat(rot_list[2]).concat([0]).concat([0,0,0,1]); // add elements to make 4x4 from a 3x3
	let transform = new THREE.Matrix4(...mat_el_list); // build the rot matrix from the list of matrix elements
	transform.multiply(pose_canonical_transform); // we first apply the canonical transform to get the cone into a common pose first, then apply the actual transform
	participant_elements[0].setRotationFromMatrix(transform);
	participant_elements[1].setRotationFromMatrix(transform);
}
function update_window_pose_vis(elements,pos_list){
	if(win){	
	// set translation of the participant
	let x = (pos_list[0] + x_offset) * scale;
	let y = (pos_list[1] + y_offset) * scale;
	let z = (pos_list[2] + z_offset) * scale;
	elements[0].position.set(x,y,z);
	}

}

function update_eye_zoom_pose(participant_elements,left_zoom,right_zoom){
	if(zoom){
		let x = (left_zoom[0] + x_offset) * scale;
		let y = (left_zoom[1] + y_offset) * scale;
		let z = (left_zoom[2] + z_offset) * scale;
		participant_elements[7].position.set(x,y,z);
		x = (right_zoom[0] + x_offset) * scale;
		y = (right_zoom[1] + y_offset) * scale;
		z = (right_zoom[2] + z_offset) * scale;
		participant_elements[8].position.set(x,y,z);
	

	}
}
// // ============================plot 2d graphs========================================================
// Create an empty plot
// Function to create a Plotly plot within a specific container
function createPlot(containerId) {
    let plotData_x = [
        {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'X Rotation',
            line: { color: 'orange' },
        }];

    let plotData_y = [
        {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Y Rotation',
            line: { color: 'green' },
        }];

    let plotData_z = [
        {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Z Rotation',
            line: { color: 'blue' },
        }];

    let plotLayout = {
        title: 'Rotation Data Time Series',
        xaxis: { title: 'Frame Index' },
        yaxis: { title: 'Rotation Value' },
    };

    // Create the initial plots
    Plotly.newPlot(containerId, plotData_x, plotLayout);
    Plotly.addTraces(containerId, plotData_y);
    Plotly.addTraces(containerId, plotData_z);

    // Create states for plots
    plotting_data[containerId] = { 'x': [[], [], []], 'y': [[], [], []] };
}

// Function to update a Plotly plot
function updatePlot(containerId, frames, rotationValues) {
    let update_x = {
        x: [[frames]],
        y: [[rotationValues[0]]],
    };

    let update_y = {
        x: [[frames]],
        y: [[rotationValues[1]]],
    };

    let update_z = {
        x: [[frames]],
        y: [[rotationValues[2]]],
    };

    // Update the Plotly plots with the new data
    Plotly.extendTraces(containerId, update_x, [0]);
    Plotly.extendTraces(containerId, update_y, [1]);
    Plotly.extendTraces(containerId, update_z, [2]);
}


// Define a variable to keep track of the current frame index
let currentFrameIndex = 0;

// Function to skip frames
function skipFrames(step) {
    // Increment the current frame index by the specified step
    currentFrameIndex += step;

    // Call a function to update the plot with the new frame index
    updatePlotWithFrameIndex(currentFrameIndex);
}

// Function to update the plot with a specific frame index (you need to implement this)
function updatePlotWithFrameIndex(frameIndex) {
    // Add your code here to update the plot with the new frame index
    // For example, you can call your updatePlot function with the new frame index
    // updatePlot(containerId, frameIndex, rotationValues);
}


// this will update all scene elements to data for frame_idx
function update_visualization(frame_num){
	// grab the scene elements for the participants
	// this is kinda hacky, it's a list of participants
	// where each participant is a list of scene elements for that participants
	let participants = scene_content['participants'];
	let elements = scene_content['win'];

	//document.getElementById('file_name_display').innerHTML = 'File name: '+'exp2/'+String(file_name)+'/2d_vis/T1/'+String(frame_num).padStart(8, '0')+'.png';;
	// // update frame index display
	document.getElementById('frame_display').innerHTML = 'Tracking frame: '+frame_num;
	
	//update 2d gaze visualization
	//console.log('exp2/'+String(file_name)+'/gaze/T1/'+String(frame_num).padStart(8, '0')+'.png')
	if(twoD){
	document.getElementById('T1_gaze').src = 'exp2/'+String(file_name)+'/gaze/T1/'+'frame_'+String(frame_num).padStart(8, '0')+'.jpeg';
	document.getElementById('T2_gaze').src = 'exp2/'+String(file_name)+'/gaze/T2/'+'frame_'+String(frame_num).padStart(8, '0')+'.jpeg';
	}
	// update head mounted camera view videos
	let frame_offset = 0;
	let offsetted_video_idx = frame_num - frame_offset;
	document.getElementById('video_frame_display').innerHTML = 'Video frame: '+offsetted_video_idx;
	let video_idx = Math.floor((offsetted_video_idx)/4); // video is at 25 fps, tracking is at 120 hz
	
	
	if (eye_contact){	
		if (tracking_data['eye_contact']['Mutual'][frame_num] == 1){
			eye_contact_frame = frame_num;
			document.getElementById('eye_contact').innerHTML = 'eye contact detected at: ' + eye_contact_frame;
			document.getElementById('eye_contact').style.color = 'green';
			p1_looking_at_p2_frame = frame_num;
			document.getElementById('p1_looking_at_p2').innerHTML ='p1 is looking at p2 at frame: ' + p1_looking_at_p2_frame;
			document.getElementById('p1_looking_at_p2').style.color = 'green';
			p2_looking_at_p1_frame = frame_num;
			document.getElementById('p2_looking_at_p1').innerHTML ='p2 is looking at p1 at frame: ' + p2_looking_at_p1_frame;
			document.getElementById('p2_looking_at_p1').style.color = 'green';
		}
		else if(tracking_data['eye_contact']['T1'][frame_num]==0 && tracking_data['eye_contact']['T2'][frame_num]==1){
			document.getElementById('p1_looking_at_p2').style.color = 'black';
			p1_looking_at_p2_frame = frame_num;
			document.getElementById('p1_looking_at_p2').innerHTML ='p1 is looking at p2 at frame: ' + p1_looking_at_p2_frame;
	
		}
		else if(tracking_data['eye_contact']['T1'][frame_num]==1 && tracking_data['eye_contact']['T2'][frame_num]==0){
			document.getElementById('p2_looking_at_p1').style.color = 'black';
			p2_looking_at_p1_frame = frame_num;
			document.getElementById('p2_looking_at_p1').innerHTML ='p2 is looking at p1 at frame: ' + p2_looking_at_p1_frame;
		}

	}
	if(p1){
	document.getElementById('T1_cam').src = 'exp2/'+String(file_name)+'/frames/T1/c01_'+String(video_idx).padStart(8, '0')+'.png';
	update_head_pose_vis(participants[0],tracking_data['T1']['translation'][frame_num],tracking_data['T1']['rot_mat'][frame_num])
	update_eye_pose_vis(participants[0],tracking_data['T1']['left_gaze_origin'][frame_num],tracking_data['T1']['right_gaze_origin'][frame_num],tracking_data['T1']['left_gaze_dir'][frame_num],tracking_data['T1']['right_gaze_dir'][frame_num])
	update_3d_gaze(participants[0],tracking_data['T1']['gaze_3d'][frame_num])
}
if(p2){
	document.getElementById('T2_cam').src = 'exp2/'+String(file_name)+'/frames/T2/c01_'+String(video_idx).padStart(8, '0')+'.png';
	update_head_pose_vis(participants[1],tracking_data['T2']['translation'][frame_num],tracking_data['T2']['rot_mat'][frame_num])
	update_eye_pose_vis(participants[1],tracking_data['T2']['left_gaze_origin'][frame_num],tracking_data['T2']['right_gaze_origin'][frame_num],tracking_data['T2']['left_gaze_dir'][frame_num],tracking_data['T2']['right_gaze_dir'][frame_num])
	update_3d_gaze(participants[1],tracking_data['T2']['gaze_3d'][frame_num])
}
	if(win){
	update_window_pose_vis(elements[0],tracking_data['win']['translation'][frame_num])
	update_window_pose_vis(elements[1],tracking_data['win.RB.1']['translation'][frame_num])
	update_window_pose_vis(elements[2],tracking_data['win.RB.2']['translation'][frame_num])
	update_window_pose_vis(elements[3],tracking_data['win.RB.3']['translation'][frame_num])
	update_window_pose_vis(elements[4],tracking_data['win.RB.4']['translation'][frame_num])
	}
	// updatePlot('T1_gaze_plot', frame_num, tracking_data['T1']['rot_euler'][frame_num]);
	// updatePlot('T2_gaze_plot', frame_num, tracking_data['T2']['rot_euler'][frame_num]);
	// if(zoom){
	// 	update_eye_zoom_pose(participants[0],tracking_data['T1']['left_gaze_zoom'],tracking_data['T1']['right_gaze_zoom'][frame_num])
	// 	update_eye_zoom_pose(participants[1],tracking_data['T2']['left_gaze_zoom'],tracking_data['T2']['right_gaze_zoom'][frame_num])
	// }

}

// auto playback function, will call itself at 100hz until is_playingback = false
function advance_frame(){
	let frame_num = document.getElementById('frame_num').value;
	document.getElementById('frame_num').value = parseInt(frame_num)+1;
	window.change_frame(); // trigger frame update

	if (is_playingback){
		setTimeout(advance_frame,10);
	}
}





// ====================================================================================
// methods called by UI interactions
// ====================================================================================

window.playback = function(){
	is_playingback = true;
	advance_frame();
}

window.stop_playback = function(){
	is_playingback = false;
}
window.resume = function(){
	let frame_num = document.getElementById('frame_num').value;
	is_playingback = true;
	update_visualization(frame_num);
	advance_frame();
}

window.change_frame = function(){
	let frame_num = document.getElementById('frame_num').value;
	update_visualization(frame_num);
}
window.skipFrames = function(step){
	let frame_num = document.getElementById('frame_num').value;
	document.getElementById('frame_num').value = parseInt(frame_num)+step;
	window.change_frame(); // trigger frame update
}
window.load_data_file = function(){
	file_name = document.getElementById('file_name').value;
	//check if file name is not null
	if (file_name == ""){
		alert("Please enter a file name");
		return;
	}
	// callback to populate camera poses from json
	let xhr = new XMLHttpRequest();
	// add file name after exp2/{file_name} (a variable reading from load file)
	file_name = document.getElementById('file_name').value;
	xhr.open('GET', `exp2/${file_name}/extracted_data_${file_name}.json?dummy=${Math.random()}`, true); // we add a random number to force reload
	//xhr.responseType = 'json';
	console.log('file_name', file_name);
	console.log('exp2/${file_name}/extracted_data_${file_name}.json?dummy=${Math.random()}');
	xhr.onloadend = function() {
		var status = xhr.status;
		if (status === 200) {
			let participants = { // set participant colours, duplicated might be hacky
				'T1':0xff0000,
				'T2':0x0000ff,
			};

			// set slider limit
			let response = JSON.parse(xhr.response);
			if (p1){
				document.getElementById('frame_num').max = response['T1']['translation'].length;

			}
			else if (p2){
				document.getElementById('frame_num').max = response['T2']['translation'].length;
			}
	
			// save tracking data
			console.log('response', response);
			tracking_data = response;
		}
	};
	xhr.send();
	update_visualization(1);
}


// Moves camera to location based on user provided transform
window.set_camera_tform = function (){
	let str_vals = document.getElementById('camera_tform_serialized_in').value;
	let vals = JSON.parse("[" + str_vals + "]");
	camera.position.x = vals[0];
	camera.position.y = vals[1];
	camera.position.z = vals[2];
	camera_azimuth = vals[3];
	camera_elevation = vals[4];
};

// just save the render out as a png
window.save_canvas = function(){
	renderer.render( scene, camera );
	let datauri = renderer.domElement.toDataURL('image/png').replace("image/png", "image/octet-stream");
	saveAs(datauri,'test.png');
}

window.save_pose_animation = function(){
	// disabled
}

// goes to a certain frame input by the user
window.goto_frame = function(){
	let frame = document.getElementById('frame_goto').value;
	document.getElementById('frame_num').value = parseInt(frame);
	window.change_frame(); // trigger frame update
}

// window.change_rot_order = change_rot_order;
window.change_3d_vis_win = function(){
	let vis_type_window = document.getElementById('window_check').value;
	console.log('vis_type_window', vis_type_window);
	change_3d_vis(vis_type_window);
}
window.change_3d_vis_2d = function(){
	
	let vis_type_2d = document.getElementById('2d_eyes_check').value;
	console.log('vis_type_2d', vis_type_2d);
	change_3d_vis(vis_type_2d);
}
window.change_3d_vis_p1 = function(){
	let vis_type_p1 = document.getElementById('Participant1_check').value;
	console.log('vis_type_p1', vis_type_p1);
	change_3d_vis(vis_type_p1);
}
window.change_3d_vis_p2 = function(){
	let vis_type_p2 = document.getElementById('Participant2_check').value;
	console.log('vis_type_p1', vis_type_p2);
	change_3d_vis(vis_type_p2);
}
window.change_3d_vis_zoom = function(){
	let vis_type_zoom = document.getElementById('zoom_check').value;
	console.log('vis_type_zoom', vis_type_zoom);
	change_3d_vis(vis_type_zoom);
}
window.change_3d_vis_eye_contact = function(){
	console.log('heloooooo');
	let vis_type_eye_contact = document.getElementById('eye_contact_check').value;
	console.log('vis_type_eye_contact', vis_type_eye_contact);
	change_3d_vis(vis_type_eye_contact);
}
window.attach_to_participant1 = function(){
	is_attached1 = true;
}

window.detach_to_participant1 = function(){
	is_attached1 = false;
}
window.attach_to_participant = function(){
	is_attached = true;
}

window.detach_to_participant = function(){
	is_attached = false;
}







// ====================================================================================
// Stuff for interactive interface
// ====================================================================================

// add events for mouse controls
viewer_container.addEventListener('mouseup',function(e){
	mouse_is_down = false;
	mouse_velocity_x = 0;
	mouse_velocity_y = 0;
});
viewer_container.addEventListener('mousedown',function(e){
	mouse_is_down = true;
});
viewer_container.addEventListener('mousemove',function(e){
	if (mouse_is_down){
		mouse_velocity_x = e.movementX;
		mouse_velocity_y = e.movementY;
	}
});
viewer_container.addEventListener('keydown',function(e){
	let base_speed = 0.05;
	if (e.keyCode === 87) camera_forward_velocity = base_speed;
	else if (e.keyCode === 83) camera_forward_velocity = -base_speed;

	if (e.keyCode === 68) camera_right_velocity = base_speed;
	else if (e.keyCode === 65) camera_right_velocity = -base_speed;

	if (e.keyCode === 81) camera_up_velocity = base_speed;
	else if (e.keyCode === 69) camera_up_velocity = -base_speed;
});
viewer_container.addEventListener('keyup',function(e){
	if (e.keyCode === 87 || e.keyCode === 83) camera_forward_velocity = 0;
	if (e.keyCode === 68 || e.keyCode === 65) camera_right_velocity = 0;
	if (e.keyCode === 81 || e.keyCode === 69) camera_up_velocity = 0;
});

window.onload = main;

