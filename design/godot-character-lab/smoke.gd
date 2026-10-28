extends Node3D
# Purposefully a neutral test object, never called the Miao model.
func _ready() -> void:
	var sample := MeshInstance3D.new()
	sample.mesh = SphereMesh.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.92, 0.27, 0.045)
	mat.roughness = 0.6
	sample.material_override = mat
	add_child(sample)
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(2.2, 1.5, 3.6)
	camera.look_at(Vector3.ZERO)
	camera.current = true
	var key := DirectionalLight3D.new()
	add_child(key)
	key.rotation_degrees = Vector3(-40, -35, 0)
	key.light_energy = 1.4
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.94, 0.92, 0.86)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color.WHITE
	env.environment.ambient_light_energy = 0.4
	add_child(env)
	for i in range(15):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var destination := ProjectSettings.globalize_path("res://../../artifacts/godot-setup/smoke-render.png")
	var result := image.save_png(destination)
	var receipt := {"engine": Engine.get_version_info(), "renderer": RenderingServer.get_current_rendering_method(), "video_adapter": RenderingServer.get_video_adapter_name(), "image_width": image.get_width(), "image_height": image.get_height(), "save_error": result, "scope": "Real local GPU render only. No character, rig, random motion or web acceptance."}
	var file := FileAccess.open("res://../../artifacts/godot-setup/smoke-receipt.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	print("MIAO_GODOT_ENVIRONMENT: ", JSON.stringify(receipt))
	get_tree().quit(0 if result == OK and not image.is_empty() else 1)
