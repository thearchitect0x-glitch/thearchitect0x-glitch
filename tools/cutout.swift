// Lift the subject out of a photo with macOS Vision (no downloads): cutout <in> <out.png>
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count == 3 else { print("usage: cutout in out.png"); exit(2) }
guard let ci = CIImage(contentsOf: URL(fileURLWithPath: args[1])) else { print("cannot read"); exit(1) }
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: ci)
try handler.perform([req])
guard let obs = req.results?.first else { print("no subject"); exit(1) }
let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: false)
let out = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
guard let cs = CGColorSpace(name: CGColorSpace.sRGB) else { exit(1) }
try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: args[2]), format: .RGBA8, colorSpace: cs)
print("ok", Int(out.extent.width), Int(out.extent.height))
