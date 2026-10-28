extends Node3D
# Native-only migration diagnostic; no audio, motion or final-art claim.
func _ready() -> void:
	get_tree().root.size = Vector2i(1024, 1024)
	get_tree().root.content_scale_size = Vector2i(1024, 1024)
	var source := ProjectSettings.globalize_path("res://../../artifacts/godot-cat-static/whole-cat-diagnostic.glb")
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var start := Time.get_ticks_msec()
	var error := document.append_from_file(source, state)
	if error != OK:
		push_error("Static GLB append failed: %d" % error)
		get_tree().quit(1)
		return
	var character := document.generate_scene(state)
	add_child(character)
	get_viewport().msaa_3d = Viewport.MSAA_4X
	# Runtime GLTFDocument does not enable the material color switch here.
	# Inspect actual surface arrays and explicitly apply glTF linear COLOR_0.
	for instance in character.find_children("*", "MeshInstance3D", true, false):
		for surface in range(instance.mesh.get_surface_count()):
			var arrays: Array = instance.mesh.surface_get_arrays(surface)
			var material: Material = instance.get_active_material(surface)
			if material is BaseMaterial3D and arrays[Mesh.ARRAY_COLOR] != null and arrays[Mesh.ARRAY_COLOR].size() > 0:
				var configured := ShaderMaterial.new()
				configured.shader = load("res://vertex-albedo-compat.gdshader")
				configured.set_shader_parameter("source_roughness", material.roughness)
				configured.set_shader_parameter("source_metallic", material.metallic)
				instance.set_surface_override_material(surface, configured)
			if str(instance.name).contains("clear cornea"):
				var clear := StandardMaterial3D.new()
				clear.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
				clear.albedo_color = Color(1, 1, 1, 0.04)
				clear.roughness = 0.035
				clear.metallic_specular = 0.65
				clear.cull_mode = BaseMaterial3D.CULL_BACK
				instance.set_surface_override_material(surface, clear)
	var cameras := character.find_children("*", "Camera3D", true, false)
	if cameras.size() != 1:
		push_error("Expected one source camera")
		get_tree().quit(1)
		return
	cameras[0].current = true
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color(0.94, 0.92, 0.86)
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color(1, 0.98, 0.94)
	environment.environment.ambient_light_energy = 0.35
	add_child(environment)
	var key := DirectionalLight3D.new()
	add_child(key)
	key.rotation_degrees = Vector3(-40, -35, 0)
	key.light_color = Color(1, 0.96, 0.9)
	key.light_energy = 0.8
	key.shadow_enabled = false
	key.directional_shadow_max_distance = 25
	key.shadow_normal_bias = 0.15
	key.shadow_bias = 0.02
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
	for i in range(45):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var destination := ProjectSettings.globalize_path("res://../../artifacts/godot-cat-static/godot-static.png")
	var save_error := image.save_png(destination)
	var meshes := character.find_children("*", "MeshInstance3D", true, false)
	var source_colors := 0
	for mesh_node in meshes:
		for index in range(mesh_node.mesh.get_surface_count()):
			var mat: Material = mesh_node.get_active_material(index)
			if (mat is BaseMaterial3D and mat.vertex_color_use_as_albedo) or mat is ShaderMaterial:
				source_colors += 1
	var receipt := {"scope": "Unaccepted C8 whole-scene native migration diagnostic only", "godot": Engine.get_version_info().string, "renderer": RenderingServer.get_current_rendering_method(), "device": RenderingServer.get_video_adapter_name(), "load_and_45_frames_ms": Time.get_ticks_msec() - start, "camera": {"name": str(cameras[0].name), "projection": cameras[0].projection, "size": cameras[0].size}, "meshes": meshes.size(), "shadow_diagnostic_disabled": true, "linear_color_0_compat_shader": true, "materials_using_vertex_color": source_colors, "render_primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME), "draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), "png_size": [image.get_width(), image.get_height()], "save_error": save_error, "limits": ["No native groom or authoring lights; linear COLOR_0 explicitly enabled; transparent cornea alpha approximation, not native transmission. No material/identity/quality or animation acceptance.", "Desktop Compatibility only; browser/phone/audio/export not tested.", "No FPS benchmark under concurrent Blender work."]}
	var output := FileAccess.open(ProjectSettings.globalize_path("res://../../artifacts/godot-cat-static/godot-receipt.json"), FileAccess.WRITE)
	output.store_string(JSON.stringify(receipt, "\t") + "\n")
	print("RESULT ", JSON.stringify(receipt))
	get_tree().quit(0 if save_error == OK else 1)
