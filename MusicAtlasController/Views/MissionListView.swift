import SwiftUI

struct MissionListView: View {
    @EnvironmentObject private var appModel: AppModel

    var body: some View {
        NavigationStack {
            List {
                switch appModel.missionLoadState {
                case .idle, .loading:
                    ProgressView("Loading mission")
                case .failed(let message):
                    ContentUnavailableView(
                        "Mission failed to load",
                        systemImage: "exclamationmark.triangle",
                        description: Text(message)
                    )
                case .loaded:
                    if let mission = appModel.mission {
                        Section("Active") {
                            NavigationLink {
                                MissionDetailView(mission: mission)
                            } label: {
                                MissionCard(mission: mission, isActive: true)
                            }
                        }
                    }

                    Section("Available Missions") {
                        ForEach(appModel.availableMissions) { mission in
                            NavigationLink {
                                MissionDetailView(mission: mission)
                            } label: {
                                MissionCard(
                                    mission: mission,
                                    isActive: appModel.isActiveMission(mission)
                                )
                            }
                        }
                    }
                }

                Section("Apple Music") {
                    MusicAuthorizationPanel(service: appModel.musicAuthorization)
                }
            }
            .navigationTitle("Music Atlas")
        }
    }
}

private struct MissionCard: View {
    let mission: Mission
    let isActive: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            VStack(alignment: .leading, spacing: 8) {
                Text(mission.missionTitle)
                    .font(.headline)

                Text(mission.hypothesis)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)

                HStack {
                    Label("\(mission.items.count) items", systemImage: "music.note")
                    Label("Resolve \(mission.successBar.minimumItemsToResolve)", systemImage: "checkmark.circle")
                }
                .font(.caption)
                .foregroundStyle(.secondary)
            }

            if isActive {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundStyle(.green)
                    .font(.title3)
                    .accessibilityLabel("Active mission")
            }
        }
        .padding(.vertical, 6)
    }
}
