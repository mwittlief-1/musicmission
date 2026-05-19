import SwiftUI

struct AppleMusicSignalProbePanel: View {
    @EnvironmentObject private var appModel: AppModel
    @StateObject private var probeStore = AppleMusicSignalProbeStore()

    var body: some View {
        Section("Apple Music Signal Probe") {
            LabeledContent("Status", value: probeStore.state.displayName)

            Button {
                Task {
                    await appModel.musicAuthorization.requestAuthorization()
                }
            } label: {
                Label("Request Apple Music Access", systemImage: "music.note")
            }
            .disabled(!appModel.musicAuthorization.snapshot.canRequestAuthorization)

            Button {
                Task {
                    await probeStore.scan()
                }
            } label: {
                Label("Run Read-Only Signal Probe", systemImage: "waveform.path.ecg")
            }
            .disabled(probeStore.state == .scanning)

            if let payload = probeStore.payload {
                SignalProbeSummary(payload: payload)

                Button {
                    probeStore.savePayload()
                } label: {
                    Label("Save Signal Payload JSON", systemImage: "square.and.arrow.down")
                }

                if let savedPayload = probeStore.savedPayload {
                    LabeledContent("Saved", value: savedPayload.jsonURL.lastPathComponent)
                    ShareLink(items: savedPayload.shareURLs) {
                        Label("Share Signal Payload", systemImage: "square.and.arrow.up")
                    }
                }
            }

            if let message = probeStore.lastMessage {
                Text(message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }

        if let jsonString = probeStore.jsonString {
            Section("Apple Music Signal JSON") {
                ScrollView(.horizontal) {
                    Text(jsonString)
                        .font(.system(.caption, design: .monospaced))
                        .textSelection(.enabled)
                }
            }
        }
    }
}

private struct SignalProbeSummary: View {
    let payload: AppleMusicSignalPayload

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            SignalProbeSummaryRow(
                title: "Environment",
                value: [
                    payload.authorization.musicAuthorizationStatus,
                    payload.environment.storefront ?? "no storefront"
                ].joined(separator: " / ")
            )

            SignalProbeSummaryRow(
                title: "Raw endpoints",
                value: "\(payload.rawEndpoints.filter(\.success).count) of \(payload.rawEndpoints.count) succeeded"
            )

            SignalProbeSummaryRow(
                title: "Library sample",
                value: "\(payload.libraryArtistsSample.count) artists, \(payload.libraryAlbumsSample.count) albums, \(payload.librarySongsSample.count) songs"
            )

            SignalProbeSummaryRow(
                title: "Recommendations",
                value: "\(payload.personalRecommendations.count)"
            )

            if !payload.errors.isEmpty {
                SignalProbeSummaryRow(
                    title: "Errors",
                    value: "\(payload.errors.count)"
                )
            }
        }
        .padding(.vertical, 4)
    }
}

private struct SignalProbeSummaryRow: View {
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .firstTextBaseline) {
            Text(title)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .multilineTextAlignment(.trailing)
        }
        .font(.caption)
    }
}
