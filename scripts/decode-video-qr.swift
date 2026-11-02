// Local, independent Vision decoder for QA frames; no camera or network access.
import Foundation
import Vision
var results = [[String: Any]]()
for path in CommandLine.arguments.dropFirst() {
    let request = VNDetectBarcodesRequest()
    request.symbologies = [.qr]
    let handler = VNImageRequestHandler(url: URL(fileURLWithPath: path))
    try handler.perform([request])
    let payloads = (request.results ?? []).compactMap { $0.payloadStringValue }
    results.append(["file": URL(fileURLWithPath: path).lastPathComponent, "payloads": payloads])
}
let data = try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
print(String(data: data, encoding: .utf8)!)
