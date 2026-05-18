import Foundation
import Combine

#if canImport(MusicKit)
import MusicKit
#endif

struct MusicAuthorizationSnapshot {
    let status: String
    let detail: String
    let canRequestAuthorization: Bool

    static let unavailable = MusicAuthorizationSnapshot(
        status: "unavailable",
        detail: "MusicKit is not available in the current build environment.",
        canRequestAuthorization: false
    )
}

struct MusicEnvironmentSnapshot {
    let status: String
    let detail: String
    let storefront: String?
    let canPlayCatalogContent: Bool?
    let hasCloudLibraryEnabled: Bool?

    static let notChecked = MusicEnvironmentSnapshot(
        status: "notChecked",
        detail: "MusicKit environment has not been checked yet.",
        storefront: nil,
        canPlayCatalogContent: nil,
        hasCloudLibraryEnabled: nil
    )

    static let unavailable = MusicEnvironmentSnapshot(
        status: "unavailable",
        detail: "MusicKit is not available in the current build environment.",
        storefront: nil,
        canPlayCatalogContent: nil,
        hasCloudLibraryEnabled: nil
    )
}

@MainActor
final class MusicAuthorizationService: ObservableObject {
    @Published private(set) var snapshot = MusicAuthorizationSnapshot(
        status: "notDetermined",
        detail: "Authorization has not been requested yet.",
        canRequestAuthorization: true
    )
    @Published private(set) var environmentSnapshot = MusicEnvironmentSnapshot.notChecked

    init() {
        refreshStatus()
    }

    func refreshStatus() {
        #if canImport(MusicKit)
        let status = MusicAuthorization.currentStatus
        snapshot = MusicAuthorizationSnapshot(
            status: Self.label(for: status),
            detail: Self.detail(for: status),
            canRequestAuthorization: status == .notDetermined
        )
        #else
        snapshot = .unavailable
        #endif
    }

    func refreshEnvironment() async {
        #if canImport(MusicKit)
        do {
            async let storefront = MusicDataRequest.currentCountryCode
            async let subscription = MusicSubscription.current
            let resolvedStorefront = try await storefront
            let resolvedSubscription = try await subscription

            environmentSnapshot = MusicEnvironmentSnapshot(
                status: resolvedSubscription.canPlayCatalogContent ? "playbackReady" : "playbackBlocked",
                detail: "MusicKit storefront and subscription check completed.",
                storefront: resolvedStorefront,
                canPlayCatalogContent: resolvedSubscription.canPlayCatalogContent,
                hasCloudLibraryEnabled: resolvedSubscription.hasCloudLibraryEnabled
            )
        } catch {
            environmentSnapshot = MusicEnvironmentSnapshot(
                status: "failed",
                detail: error.musicAtlasDiagnosticDescription,
                storefront: nil,
                canPlayCatalogContent: nil,
                hasCloudLibraryEnabled: nil
            )
        }
        #else
        environmentSnapshot = .unavailable
        #endif
    }

    func requestAuthorization() async {
        #if canImport(MusicKit)
        let status = await MusicAuthorization.request()
        snapshot = MusicAuthorizationSnapshot(
            status: Self.label(for: status),
            detail: Self.detail(for: status),
            canRequestAuthorization: status == .notDetermined
        )
        await refreshEnvironment()
        #else
        snapshot = .unavailable
        #endif
    }

    #if canImport(MusicKit)
    private static func label(for status: MusicAuthorization.Status) -> String {
        switch status {
        case .notDetermined:
            return "notDetermined"
        case .denied:
            return "denied"
        case .restricted:
            return "restricted"
        case .authorized:
            return "authorized"
        @unknown default:
            return "unknown"
        }
    }

    private static func detail(for status: MusicAuthorization.Status) -> String {
        switch status {
        case .notDetermined:
            return "Apple Music access has not been requested."
        case .denied:
            return "Apple Music access was denied. Playback is blocked."
        case .restricted:
            return "Apple Music access is restricted on this device."
        case .authorized:
            return "Apple Music access is authorized."
        @unknown default:
            return "Apple Music authorization returned an unknown status."
        }
    }
    #endif
}
