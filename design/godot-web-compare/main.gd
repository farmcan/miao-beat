extends Node3D
# Actual Godot renderer, controlled by the parent page. No audio or own stroke clock.
const TARGETS := ["Pluck", "FretLow", "FretHigh", "HeadTilt", "Lift"]
var character: Node3D
var camera: Camera3D
var morph_instances: Array[MeshInstance3D] = []
var pose_callback: JavaScriptObject
var view_callback: JavaScriptObject
var orbit_callback: JavaScriptObject
var native_negative_value := 0.0

func _ready() -> void:
	var packed := load("res://model/miao-playable.glb") as PackedScene
	if packed == null:
		push_error("Miao GLB did not import as a Godot PackedScene")
		return
	character = packed.instantiate() as Node3D
	add_child(character)
	var imported_cameras := character.find_children("*", "Camera3D", true, false)
	for imported in imported_cameras:
		imported.queue_free()
	var shader := load("res://vertex-albedo-compat.gdshader") as Shader
	for instance in character.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := instance as MeshInstance3D
		if mesh_instance.mesh.get_blend_shape_count() > 0:
			morph_instances.append(mesh_instance)
			for index in range(mesh_instance.mesh.get_blend_shape_count()):
				assert(str(mesh_instance.mesh.get_blend_shape_name(index)) == TARGETS[index])
		for surface in range(mesh_instance.mesh.get_surface_count()):
			var arrays: Array = mesh_instance.mesh.surface_get_arrays(surface)
			var material: Material = mesh_instance.get_active_material(surface)
			if material is BaseMaterial3D and arrays[Mesh.ARRAY_COLOR] != null and arrays[Mesh.ARRAY_COLOR].size() > 0:
				var configured := ShaderMaterial.new()
				configured.shader = shader
				configured.set_shader_parameter("source_roughness", material.roughness)
				configured.set_shader_parameter("source_metallic", material.metallic)
				if str(instance.name).contains("clear cornea"):
					configured.set_shader_parameter("source_clearcoat", 1.0)
					configured.set_shader_parameter("source_clearcoat_roughness", 0.035)
				mesh_instance.set_surface_override_material(surface, configured)
	assert(morph_instances.size() == 20)
	# The actual API retains a negative Pluck value; never clamp it to zero.
	morph_instances[0].set_blend_shape_value(0, -0.5)
	native_negative_value = morph_instances[0].get_blend_shape_value(0)
	assert(abs(native_negative_value + 0.5) < 0.0001)
	morph_instances[0].set_blend_shape_value(0, 0.0)
	camera = Camera3D.new()
	add_child(camera)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.current = true
	_set_view("whole")
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color(0.94, 0.92, 0.86)
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color(1.0, 0.98, 0.94)
	environment.environment.ambient_light_energy = 0.35
	add_child(environment)
	var key := DirectionalLight3D.new()
	add_child(key)
	key.rotation_degrees = Vector3(-40, -35, 0)
	key.light_color = Color(1, 0.96, 0.90)
	key.light_energy = 0.8
	key.shadow_enabled = false
	var fill := DirectionalLight3D.new()
	add_child(fill)
	fill.rotation_degrees = Vector3(-25, 120, 0)
	fill.light_color = Color(0.92, 0.96, 1)
	fill.light_energy = 0.28
	var floor_node := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(200, 200)
	floor_node.mesh = plane
	floor_node.position.y = -0.01
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.94, 0.92, 0.86)
	floor_mat.roughness = 1
	floor_node.material_override = floor_mat
	add_child(floor_node)
	if OS.has_feature("web"):
		pose_callback = JavaScriptBridge.create_callback(_js_pose)
		view_callback = JavaScriptBridge.create_callback(_js_view)
		orbit_callback = JavaScriptBridge.create_callback(_js_orbit)
		var window := JavaScriptBridge.get_interface("window")
		window.miaoGodotPose = pose_callback
		window.miaoGodotView = view_callback
		window.miaoGodotOrbit = orbit_callback
		# Direct bridge calls remain compatible with script-src 'wasm-unsafe-eval':
		# no ordinary JavaScript eval or inline script is required.
		window.miaoGodotReady = true
		var document := JavaScriptBridge.get_interface("document")
		document.body.dataset.miaoGodotReady = "true"
		document.body.dataset.miaoMorphMeshes = "20"
		var message := JavaScriptBridge.create_object("Object")
		message.type = "miao-godot-ready"
		window.parent.postMessage(message, window.location.origin)
	print("MIAO_GODOT_READY ", JSON.stringify({"renderer": RenderingServer.get_current_rendering_method(), "morph_meshes": morph_instances.size(), "negative_pluck_api_value": native_negative_value, "targets": TARGETS, "web": OS.has_feature("web")}))
	if "--diagnostic" in OS.get_cmdline_user_args():
		await get_tree().process_frame
		_set_pose(-0.6, 0.2, 0.0, 0.3, 0.1)
		var check := {"morph_meshes": morph_instances.size(), "negative_pluck": morph_instances[0].get_blend_shape_value(0), "camera_size": camera.size, "engine": Engine.get_version_info().string}
		print("MIAO_GODOT_DIAGNOSTIC ", JSON.stringify(check))
		get_tree().quit(0)

func _set_pose(p: float, low: float, high: float, head: float, lift: float) -> void:
	var values := [clampf(p, -1.0, 1.0), clampf(low, 0.0, 1.0), clampf(high, 0.0, 1.0), clampf(head, 0.0, 1.0), clampf(lift, 0.0, 1.0)]
	for instance in morph_instances:
		for index in range(TARGETS.size()):
			instance.set_blend_shape_value(index, values[index])

func _js_pose(arguments: Array) -> void:
	if arguments.size() >= 5:
		_set_pose(float(arguments[0]), float(arguments[1]), float(arguments[2]), float(arguments[3]), float(arguments[4]))

func _js_view(arguments: Array) -> void:
	if arguments.size() > 0:
		_set_view(str(arguments[0]))

func _js_orbit(arguments: Array) -> void:
	if arguments.size() > 0:
		character.rotation.y = deg_to_rad(clampf(float(arguments[0]), -35.0, 35.0))

func _set_view(mode: String) -> void:
	var target := Vector3(0.1, 1.61, 0)
	var zoom := 1.0
	if mode == "hands":
		target = Vector3(0.3, 1.7, 1.0)
		zoom = 1.25
	elif mode == "face":
		target = Vector3(0.07, 3.03, 0)
		zoom = 2.7
	camera.size = 4.20027637481689 / zoom
	camera.position = target + Vector3(0, 0.986, 12.0)
	camera.look_at(target)
