import * as THREE from 'three';

function get_orbit_tform_from_ae(azimuth,elevation,radius){
	let camera_world = new THREE.Matrix4(
		1,0,0,0,
		0,0,-1,-radius,
		0,1,0,0,
		0,0,0,1);
	let rot_elevation_mat = new THREE.Matrix4(
		1,0,0,0,
		0,Math.cos(elevation),-Math.sin(elevation),0,
		0,Math.sin(elevation),Math.cos(elevation),0,
		0,0,0,1
	);
	let rot_azimuth_mat = new THREE.Matrix4(
		Math.cos(azimuth),-Math.sin(azimuth),0,0,
		Math.sin(azimuth),Math.cos(azimuth),0,0,
		0,0,1,0,
		0,0,0,1
	);
	camera_world.premultiply(rot_elevation_mat);
	camera_world.premultiply(rot_azimuth_mat);
	return camera_world;
}

function get_free_tform_from_ae(azimuth,elevation){
	let rot_elevation_mat = new THREE.Matrix4(
		1,0,0,0,
		0,Math.cos(elevation),-Math.sin(elevation),0,
		0,Math.sin(elevation),Math.cos(elevation),0,
		0,0,0,1
	);
	let rot_azimuth_mat = new THREE.Matrix4(
		Math.cos(azimuth),0,Math.sin(azimuth),0,
		0,1,0,0,
		-Math.sin(azimuth),0,Math.cos(azimuth),0,
		0,0,0,1
	);
	rot_elevation_mat.premultiply(rot_azimuth_mat);
	return rot_elevation_mat;
}

function add_lights(scene){
	const directionalLight = new THREE.DirectionalLight( 0xffffff, 0.8 );
	directionalLight.lookAt(0,0,0);
	scene.add( directionalLight );
	const directionalLight2 = new THREE.DirectionalLight( 0xffffff, 0.8 );
	directionalLight2.position.x = 1;
	directionalLight2.position.y = 0;
	directionalLight2.position.z = 0;
	directionalLight2.lookAt(0,0,0);
	scene.add( directionalLight2 )
	const directionalLight3 = new THREE.DirectionalLight( 0xffffff, 0.8 );
	directionalLight3.position.x = 0;
	directionalLight3.position.y = 0;
	directionalLight3.position.z = 1;
	directionalLight3.lookAt(0,0,0);
	scene.add( directionalLight3 )
	const light = new THREE.AmbientLight( 0x404040 ); // soft white light
	scene.add( light );
}

function add_axis_indicator(scene,pos){
	//const x_endpoint = (new THREE.Vector3()).copy(pos);
	//const y_endpoint = (new THREE.Vector3()).copy(pos);
	//const z_endpoint = (new THREE.Vector3()).copy(pos);

	//x_endpoint.add(new THREE.Vector3(1,0,0));
	//y_endpoint.add(new THREE.Vector3(0,1,0));
	//z_endpoint.add(new THREE.Vector3(0,0,1));

	//let line_material = new THREE.LineBasicMaterial( { color: 'rgb(255,0,0)' } );
	//let points = [ pos, x_endpoint];
	//let line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	//let line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	//line_material = new THREE.LineBasicMaterial( { color: 'rgb(0,255,0)' } );
	//points = [ pos, y_endpoint];
	//line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	//line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	//line_material = new THREE.LineBasicMaterial( { color: 'rgb(0,0,255)' } );
	//points = [ pos, z_endpoint];
	//line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	//line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	const x_dir = (new THREE.Vector3(1,0,0));
	const y_dir = (new THREE.Vector3(0,1,0));
	const z_dir = (new THREE.Vector3(0,0,1));

	let arrow = new THREE.ArrowHelper(x_dir,pos, 1, 0xff0000,0.2,0.2); scene.add(arrow);
	arrow = new THREE.ArrowHelper(y_dir,pos, 1, 0x00ff00,0.2,0.2); scene.add(arrow);
	arrow = new THREE.ArrowHelper(z_dir,pos, 1, 0x0000ff,0.2,0.2); scene.add(arrow);
}

function add_grid(scene,size,n_divisions,offset=null,rot=null){
	if (offset==null){
		offset = new THREE.Vector3(0,0,0);
	}
	if (rot==null){
		rot = new THREE.Matrix3(1,0,0,0,1,0,0,0,1);
	}
	// create x grid
	let grid_scale = size/n_divisions;
	for(let i=-n_divisions;i<n_divisions+1;i++){
		const line_material = new THREE.LineBasicMaterial( { color: 'rgb(128,128,128)' } );
		const points = [ new THREE.Vector3( -size, 0, i*grid_scale ), new THREE.Vector3(  size, 0, i*grid_scale )];
		points[0].applyMatrix3(rot).add(offset);points[1].applyMatrix3(rot).add(offset);
		const line_geometry = new THREE.BufferGeometry().setFromPoints( points );
		const line = new THREE.Line( line_geometry, line_material ); scene.add( line );
	}

	// create y grid
	for(let i=-n_divisions;i<n_divisions+1;i++){
		const line_material = new THREE.LineBasicMaterial( { color: 'rgb(128,128,128)'  } );
		const points = [new THREE.Vector3( i*grid_scale, 0, -size ),new THREE.Vector3( i*grid_scale, 0, size )];
		points[0].applyMatrix3(rot).add(offset);points[1].applyMatrix3(rot).add(offset);
		const line_geometry = new THREE.BufferGeometry().setFromPoints( points );
		const line = new THREE.Line( line_geometry, line_material ); scene.add( line );
	}
}

function add_grid_with_axis(scene,size,n_divisions){
	// create x grid
	let grid_scale = size/n_divisions;
	for(let i=-n_divisions;i<n_divisions+1;i++){
		if (i == 0) continue;
		const line_material = new THREE.LineBasicMaterial( { color: 0xffffff } );
		const points = [ new THREE.Vector3( -size, i*grid_scale, 0 ), new THREE.Vector3(  size, i*grid_scale, 0 )];
		const line_geometry = new THREE.BufferGeometry().setFromPoints( points );
		const line = new THREE.Line( line_geometry, line_material ); scene.add( line );
	}
	let line_material = new THREE.LineBasicMaterial( { color: 0xffffff } );
	let points = [ new THREE.Vector3( -size, 0, 0 ), new THREE.Vector3( 0, 0, 0 )];
	let line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	let line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	line_material = new THREE.LineBasicMaterial( { color: 0xff0000 } );
	points = [ new THREE.Vector3( size, 0, 0 ), new THREE.Vector3( 0, 0, 0 )];
	line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	// create y grid
	for(let i=-n_divisions;i<n_divisions+1;i++){
		if (i == 0) continue;
		const line_material = new THREE.LineBasicMaterial( { color: 0xffffff } );
		const points = [new THREE.Vector3( i*grid_scale, -size, 0 ),new THREE.Vector3( i*grid_scale,  size, 0 )];
		const line_geometry = new THREE.BufferGeometry().setFromPoints( points );
		const line = new THREE.Line( line_geometry, line_material ); scene.add( line );
	}
	line_material = new THREE.LineBasicMaterial( { color: 0xffffff } );
	points = [ new THREE.Vector3( 0, -size, 0 ), new THREE.Vector3( 0, 0, 0 )];
	line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	line_material = new THREE.LineBasicMaterial( { color: 0x00ff00 } );
	points = [ new THREE.Vector3( 0, size, 0 ), new THREE.Vector3( 0, 0, 0 )];
	line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( line_geometry, line_material ); scene.add( line );

	line_material = new THREE.LineBasicMaterial( { color: 0x0000ff } );
	points = [ new THREE.Vector3( 0, 0, size ), new THREE.Vector3( 0, 0, 0 )];
	line_geometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( line_geometry, line_material ); scene.add( line );
}

export { get_free_tform_from_ae, add_lights, add_axis_indicator, add_grid, add_grid_with_axis };
