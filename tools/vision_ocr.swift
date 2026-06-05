import Foundation
import Vision
import CoreGraphics
import ImageIO

struct OCRLine {
    let text: String
    let confidence: Float
    let box: CGRect
}

func recognize(path: String) throws -> [OCRLine] {
    let url = URL(fileURLWithPath: path)
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw NSError(domain: "vision_ocr", code: 1, userInfo: [NSLocalizedDescriptionKey: "Cannot read image: \(path)"])
    }

    var lines: [OCRLine] = []
    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            fputs("OCR error for \(path): \(error)\n", stderr)
            return
        }

        let observations = request.results as? [VNRecognizedTextObservation] ?? []
        for observation in observations {
            guard let candidate = observation.topCandidates(1).first else { continue }
            lines.append(OCRLine(text: candidate.string, confidence: candidate.confidence, box: observation.boundingBox))
        }
    }

    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["ja-JP", "en-US", "ko-KR"]

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])

    return lines.sorted {
        let dy = abs($0.box.midY - $1.box.midY)
        if dy > 0.012 {
            return $0.box.midY > $1.box.midY
        }
        return $0.box.minX < $1.box.minX
    }
}

let args = Array(CommandLine.arguments.dropFirst())
if args.isEmpty {
    fputs("usage: vision_ocr image1 [image2 ...]\n", stderr)
    exit(2)
}

for path in args {
    print("===== \(URL(fileURLWithPath: path).lastPathComponent) =====")
    do {
        let lines = try recognize(path: path)
        for line in lines {
            let text = line.text.replacingOccurrences(of: "\n", with: " ")
            print(String(format: "%.3f %.3f %.3f %.3f %.2f %@",
                         line.box.minX, line.box.minY, line.box.width, line.box.height,
                         line.confidence, text))
        }
    } catch {
        fputs("\((error as NSError).domain) \((error as NSError).code): \(error.localizedDescription)\n", stderr)
    }
}
