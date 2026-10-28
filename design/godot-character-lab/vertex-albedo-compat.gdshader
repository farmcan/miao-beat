shader_type spatial;
render_mode cull_disabled;
uniform float source_roughness = 0.65;
uniform float source_metallic = 0.0;
vec3 encoded_srgb(vec3 linear_rgb) {
	vec3 c = max(linear_rgb, vec3(0.0));
	return mix(1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055,
		12.92 * c, lessThanEqual(c, vec3(0.0031308)));
}
void fragment() {
	// glTF COLOR_0 is linear. Compatibility ignores BaseMaterial's sRGB flag.
	ALBEDO = OUTPUT_IS_SRGB ? encoded_srgb(COLOR.rgb) : COLOR.rgb;
	ROUGHNESS = source_roughness;
	METALLIC = source_metallic;
	if (!FRONT_FACING) NORMAL = -NORMAL;
}
