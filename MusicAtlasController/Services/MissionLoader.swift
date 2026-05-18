import Foundation

enum MissionLoaderError: LocalizedError {
    case missingBundledMission(String)
    case emptyBundledMissionLibrary(String)

    var errorDescription: String? {
        switch self {
        case .missingBundledMission(let filename):
            return "Could not find bundled mission resource: \(filename).json"
        case .emptyBundledMissionLibrary(let filename):
            return "Bundled mission library is empty: \(filename).json"
        }
    }
}

final class MissionLoader {
    private let decoder: JSONDecoder

    init(decoder: JSONDecoder = MissionLoader.makeDecoder()) {
        self.decoder = decoder
    }

    func loadBundledSampleMission() throws -> Mission {
        try loadBundledMission(named: "sample_mission_love_tributaries_v0_2")
    }

    func loadBundledDefaultMission() throws -> Mission {
        try loadBundledMission(named: "sample_mission_lithuanian_discovery_v0_3_alpha")
    }

    func loadBundledMissionLibrary() throws -> [Mission] {
        let missions = try loadBundledMissionCollection(named: "waymark_matt_10_personal_missions_v0_1")
        guard !missions.isEmpty else {
            throw MissionLoaderError.emptyBundledMissionLibrary("waymark_matt_10_personal_missions_v0_1")
        }

        return missions
    }

    func loadBundledMission(named resourceName: String) throws -> Mission {
        guard let url = Bundle.main.url(forResource: resourceName, withExtension: "json") else {
            throw MissionLoaderError.missingBundledMission(resourceName)
        }

        let data = try Data(contentsOf: url)
        return try decoder.decode(Mission.self, from: data)
    }

    func loadBundledMissionCollection(named resourceName: String) throws -> [Mission] {
        guard let url = Bundle.main.url(forResource: resourceName, withExtension: "json") else {
            throw MissionLoaderError.missingBundledMission(resourceName)
        }

        let data = try Data(contentsOf: url)
        return try decoder.decode([Mission].self, from: data)
    }

    private static func makeDecoder() -> JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}
