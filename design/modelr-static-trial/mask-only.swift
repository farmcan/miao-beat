import Foundation
import AppKit
let input=URL(fileURLWithPath:CommandLine.arguments[1])
let output=URL(fileURLWithPath:CommandLine.arguments[2],isDirectory:true)
guard let img=BackgroundRemover.loadCGImage(input),let mask=BackgroundRemover.visionMask(for:img),let cutout=BackgroundRemover.cutoutPNG(original:img,mask:mask),let png=BackgroundRemover.pngData(mask) else { fatalError("Vision segmentation failed") }
try cutout.write(to: output.appendingPathComponent("input-cutout.png"))
try png.write(to: output.appendingPathComponent("input-mask.png"))
print("mask and cutout written")
