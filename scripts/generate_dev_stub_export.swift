import Foundation

@main
struct GenerateDevStubExport {
    static func main() async throws {
        let arguments = CommandLine.arguments
        guard arguments.count == 3 else {
            throw GenerateDevStubExportError.invalidArguments(
                "Usage: generate_dev_stub_export <repo-root> <output-json-path>"
            )
        }

        let repoRoot = URL(fileURLWithPath: arguments[1], isDirectory: true)
        let outputURL = URL(fileURLWithPath: arguments[2])
        let missionURL = repoRoot.appendingPathComponent("data/missions/sample_mission_love_tributaries_v0_2.json")

        let missionData = try Data(contentsOf: missionURL)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let mission = try decoder.decode(Mission.self, from: missionData)

        guard let item = mission.items.first else {
            throw GenerateDevStubExportError.missingMissionItem
        }

        let now = Date()
        let resolution = try await StubMusicSearchService().resolve(item: item, at: now)
        let playback = await StubMusicPlaybackService().play(resolution: resolution, at: now)
        let reaction = ReactionRecord(
            reactionValue: .hit,
            reactedAt: now,
            notes: ReactionNotes(text: "Generated dev stub export for schema validation.", voiceNoteRefs: nil)
        )

        let preview = try SessionExporter().makeDevelopmentExport(
            mission: mission,
            item: item,
            resolution: resolution,
            playback: playback,
            reaction: reaction,
            authorizationStatus: "notDetermined",
            now: now
        )

        try FileManager.default.createDirectory(
            at: outputURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        try preview.jsonString.write(to: outputURL, atomically: true, encoding: .utf8)
        print(outputURL.path)
    }
}

enum GenerateDevStubExportError: LocalizedError {
    case invalidArguments(String)
    case missingMissionItem

    var errorDescription: String? {
        switch self {
        case let .invalidArguments(message):
            return message
        case .missingMissionItem:
            return "Sample mission does not contain any items."
        }
    }
}
