import SwiftUI

struct MissionDetailView: View {
    @EnvironmentObject private var appModel: AppModel

    let mission: Mission

    var body: some View {
        List {
            Section {
                Button {
                    appModel.selectMission(mission)
                } label: {
                    Label(
                        appModel.isActiveMission(mission) ? "Active Mission" : "Start Mission",
                        systemImage: appModel.isActiveMission(mission) ? "checkmark.circle.fill" : "play.circle.fill"
                    )
                    .font(.headline)
                }
                .disabled(appModel.isActiveMission(mission))
            }

            Section("Hypothesis") {
                Text(mission.hypothesis)
                Text(mission.inflationWarning)
                    .foregroundStyle(.secondary)
            }

            Section("Success Bar") {
                LabeledContent("Resolve", value: "\(mission.successBar.minimumItemsToResolve)")
                LabeledContent("Play", value: "\(mission.successBar.minimumItemsToPlay)")
                LabeledContent("React", value: "\(mission.successBar.minimumReactionsRequired)")
                LabeledContent("Physical iPhone", value: mission.successBar.requiresPhysicalIPhone ? "Required" : "No")
            }

            Section("Items") {
                ForEach(mission.items) { item in
                    Button {
                        if !appModel.isActiveMission(mission) {
                            appModel.selectMission(mission)
                        }
                        appModel.selectItem(item)
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text("\(item.sequence). \(item.title)")
                                    .font(.headline)
                                Spacer()
                                if appModel.selectedItemID == item.itemID {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundStyle(.green)
                                }
                                ResolutionBadge(status: appModel.resolution(for: item).status)
                            }

                            Text(item.artist)
                                .font(.subheadline)

                            if let whyIncluded = item.whyIncluded {
                                Text(whyIncluded)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }                    
                }
            }
        }
        .navigationTitle(mission.missionTitle)
    }
}

struct ResolutionBadge: View {
    let status: ResolutionStatus

    var body: some View {
        Text(status.rawValue)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(.thinMaterial, in: Capsule())
    }
}
