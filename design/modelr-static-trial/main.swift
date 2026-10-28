import Foundation
import CoreGraphics
import ImageIO
import MLX
import Hy3DMLX

let args = CommandLine.arguments
if args.count == 2 && args[1] == "--selftest" {
 let x = MLXArray([Float(1),2,3]); let y = x * x; eval(y); print("MLX_GPU_SELFTEST \(y.asArray(Float.self))"); exit(0)
}
func fail(_ message: String) -> Never { fputs(message + "\n", stderr); exit(1) }
guard args.count == 4 else { fail("usage: MiaoShapeCLI input-image weights.safetensors output.glb") }
let input = URL(fileURLWithPath: args[1])
let weights = URL(fileURLWithPath: args[2])
let output = URL(fileURLWithPath: args[3])
let started = Date()
func log(_ value: String) { print("\(ISO8601DateFormatter().string(from: Date())) \(value)"); fflush(stdout) }
log("input=\(input.path) seed=17 steps=30 guidance=5 resolution=256 quantize=0")
guard let original = BackgroundRemover.loadCGImage(input) else { fail("cannot decode input") }
guard let mask = BackgroundRemover.visionMask(for: original),
      let cutout = BackgroundRemover.cutoutPNG(original: original, mask: mask) else { fail("native Vision foreground segmentation failed") }
let cutoutURL = output.deletingLastPathComponent().appendingPathComponent("input-cutout.png")
try cutout.write(to: cutoutURL)
if let maskPNG = BackgroundRemover.pngData(mask) { try maskPNG.write(to: output.deletingLastPathComponent().appendingPathComponent("input-mask.png")) }
guard let source = CGImageSourceCreateWithData(cutout as CFData, nil), let cg = CGImageSourceCreateImageAtIndex(source, 0, nil) else { fail("cannot decode cutout") }
log("segmented; loading shape-small fp16")
let generator = try ShapeGenerator(weightsURL: weights, quantize: 0)
log("loaded")
let counts = try generator.generateGLB(image: cg, to: output, steps: 30, guidance: 5, seed: 17, resolution: 256, octree: true) { progress in
  log("\(progress.stage) \(progress.fraction)")
}
let receipt: [String: Any] = ["seed":17,"steps":30,"guidance":5,"resolution":256,"quantize":0,"elapsed_seconds":Date().timeIntervalSince(started),"vertices":counts.verts,"faces":counts.faces,"peak_mlx_bytes":MLX.Memory.peakMemory,"input":input.path,"output":output.path,"status":"generated_unreviewed"]
try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted,.sortedKeys]).write(to: output.deletingPathExtension().appendingPathExtension("receipt.json"))
log("DONE vertices=\(counts.verts) faces=\(counts.faces) elapsed=\(Date().timeIntervalSince(started)) peakMLX=\(MLX.Memory.peakMemory)")
