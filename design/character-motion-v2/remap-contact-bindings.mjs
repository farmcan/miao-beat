/** Exact C35 -> merged-body map only. Never falls back to nearest/provenance
 * tuples: six support vertices have non-unique integer provenance (3742 matches).
 * New geometry still needs a new actual contact/collision audit after this step.
 */
export function remapContactBindings(profile, { sourceSha256, indexMap, targetWorldVertices, targetNativeSha256 }) {
  if (sourceSha256 !== profile.source_native_sha256) throw new Error('Source SHA does not match frozen profile');
  if (!(indexMap instanceof Map) || !targetNativeSha256) throw new Error('Explicit source-to-target vertex map and target SHA required');
  return profile.left_hold.anchors.map(anchor => {
    const indices = anchor.triangle_vertex_indices.map(i => {
      const target = indexMap.get(i);
      if (!Number.isInteger(target) || target < 0) throw new Error(`Missing exact source index mapping for ${i}`);
      if (targetWorldVertices[target]?.length !== 3 || !targetWorldVertices[target].every(Number.isFinite)) throw new Error(`Missing target world vertex ${target}`);
      return target;
    });
    if (new Set(indices).size !== 3) throw new Error('Triangle remap collapsed distinct source vertices');
    const world = [0, 1, 2].map(axis => indices.reduce((sum, id, i) => sum + targetWorldVertices[id][axis] * anchor.barycentric[i], 0));
    const drift = Math.hypot(...world.map((value, i) => value - anchor.world[i]));
    return { ...structuredClone(anchor), triangle_vertex_indices: indices,
      source_triangle_vertex_indices: [...anchor.triangle_vertex_indices],
      target_native_sha256: targetNativeSha256, reconstructed_world: world,
      rest_contact_drift_u: drift, actual_contact_audit_required: true,
      contact_pass_inherited: false };
  });
}
