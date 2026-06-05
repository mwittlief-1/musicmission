import Combine
import Foundation

enum AtlasHomeReadoutLoadState: Equatable {
    case idle
    case loading
    case loaded
    case failed(String)
}

final class AtlasHomeReadoutStore: ObservableObject {
    static let resourceName = "atlas_home_what_were_seeing_so_far_fixture_v0_2"
    static let supportedSchemaVersion = "cartenza.atlas_home_what_were_seeing_so_far.v0.2"

    @Published private(set) var loadState: AtlasHomeReadoutLoadState = .idle
    @Published private(set) var fixture: AtlasHomeReadoutFixture?

    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var displayModel: AtlasHomeReadoutDisplayModel? {
        fixture?.displayModel
    }

    func load() {
        guard loadState != .loaded else {
            return
        }

        loadState = .loading

        do {
            fixture = try Self.loadFixture(bundle: bundle)
            loadState = .loaded
        } catch {
            loadState = .failed(error.localizedDescription)
        }
    }

    static func loadFixture(bundle: Bundle = .main) throws -> AtlasHomeReadoutFixture {
        guard let url = bundle.url(forResource: resourceName, withExtension: "json") else {
            throw AtlasHomeReadoutStoreError.missingBundleResource(resourceName)
        }

        let data = try Data(contentsOf: url)
        return try loadFixture(data: data)
    }

    static func loadFixture(data: Data) throws -> AtlasHomeReadoutFixture {
        let fixture = try JSONDecoder().decode(AtlasHomeReadoutFixture.self, from: data)
        guard fixture.schemaVersion == supportedSchemaVersion else {
            throw AtlasHomeReadoutStoreError.unsupportedSchemaVersion(fixture.schemaVersion)
        }
        guard fixture.displayModel.moduleName == "What We're Seeing So Far" else {
            throw AtlasHomeReadoutStoreError.unsupportedModuleName(fixture.displayModel.moduleName)
        }

        return fixture
    }
}

enum AtlasHomeReadoutStoreError: LocalizedError {
    case missingBundleResource(String)
    case unsupportedSchemaVersion(String)
    case unsupportedModuleName(String)

    var errorDescription: String? {
        switch self {
        case .missingBundleResource(let resourceName):
            return "Missing Atlas Home readout resource \(resourceName)."
        case .unsupportedSchemaVersion(let schemaVersion):
            return "Unsupported Atlas Home readout schema version \(schemaVersion)."
        case .unsupportedModuleName(let moduleName):
            return "Unsupported Atlas Home readout module name \(moduleName)."
        }
    }
}
