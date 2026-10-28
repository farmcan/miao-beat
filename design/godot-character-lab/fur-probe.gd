extends Node3D
# Neutral material viability probe, not Miao art or a performance benchmark.
const Fur = preload("res://addons/so_fluffy/so_fluffy.gd")
func _ready() -> void:
	var sample := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radial_segments = 48
	sphere.rings = 32
	sample.mesh = sphere
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.92, 0.27, 0.045)
	mat.roughness = 0.7
	sample.material_override = mat
	add_child(sample)
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(1.4, 0.8, 2.2)
	camera.look_at(Vector3.ZERO)
	camera.current = true
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 1.5
	var light := DirectionalLight3D.new()
	add_child(light)
	light.rotation_degrees = Vector3(-40, -35, 0)
	light.light_energy = 1.4
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.94, 0.92, 0.86)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color.WHITE
	world.environment.ambient_light_energy = 0.4
	add_child(world)
	var results: Array = []
	for shells in [0, 8, 16]:
		var fur: Node = null
		if shells > 0:
			fur = Fur.new()
			fur.number_of_shells = shells
			fur.length = 0.025
			fur.density = 0.15
			var gradient := GradientTexture2D.new()
			gradient.gradient = Gradient.new()
			gradient.gradient.set_color(0, Color(0.55, 0.55, 0.55))
			gradient.gradient.set_color(1, Color.WHITE)
			fur.height_gradient = gradient
			fur.albedo_color = Color(0.92, 0.27, 0.045)
			fur.physics_enabled = false
			fur.seed = 17
			fur.turbulence_strength = 0.1
			sample.add_child(fur)
		for i in range(60):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		var path := ProjectSettings.globalize_path("res://../../artifacts/godot-fur-probe/shell-%02d.png" % shells)
		var error := image.save_png(path)
		results.append({"shells": shells, "actual_material_count": fur.shells.size() if fur else 0, "png_save_error": error, "draw_calls_in_frame": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), "rendered_primitives_in_frame": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME), "image_width": image.get_width(), "image_height": image.get_height()})
		if fur:
			fur.queue_free()
			await get_tree().process_frame
	var receipt := {"godot": Engine.get_version_info().string, "renderer": RenderingServer.get_current_rendering_method(), "video_adapter": RenderingServer.get_video_adapter_name(), "seed": 17, "macro_camera_ortho_size": 1.5, "density": 0.15, "root_gradient": 0.55, "upstream_commit": "09af7e68c17db7b85a4780220b28dc015da28a91", "renders": results, "limits": ["Neutral sphere only, not Miao, skinned geometry, web export or a quality pass.", "Actual draw counters are diagnostic; no FPS benchmark under shared concurrent work.", "Native Compatibility only; WebGL2 browser must still be tested."]}
	var file := FileAccess.open(ProjectSettings.globalize_path("res://../../artifacts/godot-fur-probe/receipt.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	print("MIAO_GODOT_FUR_PROBE: ", JSON.stringify(receipt))
	get_tree().quit()
