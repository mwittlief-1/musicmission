import SwiftUI

struct MusicAuthorizationPanel: View {
    @ObservedObject var service: MusicAuthorizationService

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Status")
                Spacer()
                Text(service.snapshot.status)
                    .font(.callout.monospaced())
                    .foregroundStyle(.secondary)
            }

            Text(service.snapshot.detail)
                .font(.caption)
                .foregroundStyle(.secondary)

            Button {
                Task {
                    await service.requestAuthorization()
                }
            } label: {
                Label("Request Access", systemImage: "music.note")
            }
            .disabled(!service.snapshot.canRequestAuthorization)

            if AppFeatureFlags.showDiagnosticTabs {
                Divider()

                LabeledContent("MusicKit check", value: service.environmentSnapshot.status)
                if let storefront = service.environmentSnapshot.storefront {
                    LabeledContent("Storefront", value: storefront)
                }
                if let canPlayCatalogContent = service.environmentSnapshot.canPlayCatalogContent {
                    LabeledContent("Can play catalog", value: canPlayCatalogContent ? "true" : "false")
                }
                if let hasCloudLibraryEnabled = service.environmentSnapshot.hasCloudLibraryEnabled {
                    LabeledContent("Cloud library", value: hasCloudLibraryEnabled ? "true" : "false")
                }

                Text(service.environmentSnapshot.detail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .textSelection(.enabled)

                Button {
                    Task {
                        await service.refreshEnvironment()
                    }
                } label: {
                    Label("Check MusicKit Status", systemImage: "checkmark.seal")
                }
                .disabled(service.snapshot.status != "authorized")
            }
        }
        .padding(.vertical, 4)
    }
}
