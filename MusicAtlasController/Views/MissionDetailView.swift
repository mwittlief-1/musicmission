import SwiftUI

struct MissionDetailView: View {
    @EnvironmentObject private var appModel: AppModel
    @ObservedObject var atlasExplainerStore: AtlasExplainerStore

    let mission: Mission

    init(mission: Mission, atlasExplainerStore: AtlasExplainerStore) {
        self.mission = mission
        self.atlasExplainerStore = atlasExplainerStore
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Mission")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(WaymarkTheme.route)
                            .textCase(.uppercase)
                        Text(mission.missionTitle)
                            .font(.largeTitle.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)
                            .fixedSize(horizontal: false, vertical: true)
                        Text(mission.missionType.displayName)
                            .font(.caption.weight(.bold))
                            .foregroundStyle(WaymarkTheme.route)
                    }

                    Spacer()

                    Text("\(mission.items.count) songs")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(WaymarkTheme.raisedPanel, in: Capsule())
                }

                Button {
                    appModel.selectMission(mission)
                } label: {
                    Label(
                        appModel.isActiveMission(mission) ? "Active Mission" : "Start Mission",
                        systemImage: appModel.isActiveMission(mission) ? "checkmark.circle.fill" : "play.circle.fill"
                    )
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                }
                .disabled(appModel.isActiveMission(mission))
                .buttonStyle(.borderedProminent)

                VStack(alignment: .leading, spacing: 10) {
                    if let brief = mission.brief {
                        Text("Brief")
                            .font(.title3.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)
                        Text(brief)
                            .font(.body)
                            .foregroundStyle(WaymarkTheme.text)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    Text("Hypothesis")
                        .font(.title3.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                    Text(mission.hypothesis)
                        .font(.body)
                        .foregroundStyle(WaymarkTheme.text)
                        .fixedSize(horizontal: false, vertical: true)
                    if let inflationWarning = detailInflationWarning {
                        Text(inflationWarning)
                            .font(.callout)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    if let missionReason = detailMissionReason {
                        Text(detailMissionReasonTitle)
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)
                            .padding(.top, 4)
                        Text(missionReason)
                            .font(.callout)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    HStack(spacing: 8) {
                        if let statusLabel = detailImportStatusLabel {
                            MissionInfoPill(label: statusLabel)
                        }
                        if let riskLevel = mission.riskLevel {
                            MissionInfoPill(label: "risk: \(riskLevel)")
                        }
                    }
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
                .overlay(
                    RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                        .stroke(WaymarkTheme.line, lineWidth: 1)
                )

                AtlasMissionDetailExplainerModule(
                    mission: mission,
                    library: atlasExplainerStore.library
                )

                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                    MissionMetricCard(title: "Play", value: "\(mission.successBar.minimumItemsToPlay)")
                    MissionMetricCard(title: "React", value: "\(mission.successBar.minimumReactionsRequired)")
                    MissionMetricCard(title: "iPhone", value: mission.successBar.requiresPhysicalIPhone ? "Required" : "Optional")
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Route preview")
                        .font(.title3.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)

                    ForEach(mission.items) { item in
                        Button {
                            if !appModel.isActiveMission(mission) {
                                appModel.selectMission(mission)
                            }
                            appModel.selectItem(item)
                        } label: {
                            HStack(alignment: .top, spacing: 12) {
                                Text(String(format: "%02d", item.sequence))
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(WaymarkTheme.text)
                                    .frame(width: 34, height: 34)
                                    .background(WaymarkTheme.raisedPanel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))

                                VStack(alignment: .leading, spacing: 5) {
                                    HStack(alignment: .firstTextBaseline) {
                                        Text(item.title)
                                            .font(.headline)
                                            .foregroundStyle(WaymarkTheme.text)
                                            .lineLimit(2)
                                        Spacer()
                                        if appModel.selectedItemID == item.itemID {
                                            Image(systemName: "checkmark.circle.fill")
                                                .foregroundStyle(WaymarkTheme.positive)
                                        }
                                    }

                                    Text(item.artist)
                                        .font(.subheadline)
                                        .foregroundStyle(WaymarkTheme.mutedText)

                                    HStack(spacing: 6) {
                                        if let role = item.alphaRouteRole {
                                            MissionInfoPill(label: role.displayName)
                                        }
                                        MissionInfoPill(label: item.alphaDisplayResolutionStatus)
                                    }

                                    if let whyIncluded = detailWhyIncluded(for: item) {
                                        Text(whyIncluded)
                                            .font(.caption)
                                            .foregroundStyle(WaymarkTheme.mutedText)
                                            .lineLimit(2)
                                    }

                                    if let expectedSignal = item.expectedTestSignal {
                                        Text(expectedSignal)
                                            .font(.caption2)
                                            .foregroundStyle(WaymarkTheme.mutedText)
                                            .lineLimit(2)
                                    }

                                    if AppFeatureFlags.showDiagnosticTabs {
                                        ResolutionBadge(status: appModel.resolution(for: item).status)
                                    }
                                }
                            }
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
                            .overlay(
                                RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                                    .stroke(appModel.selectedItemID == item.itemID ? WaymarkTheme.route.opacity(0.5) : WaymarkTheme.line, lineWidth: 1)
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .padding(18)
        }
        .background(WaymarkTheme.background.ignoresSafeArea())
        .navigationTitle(mission.missionTitle)
        .task {
            atlasExplainerStore.load()
        }
    }

    private var isResolvedAlphaSmokeFixture: Bool {
        mission.alphaAppImportStatus == .appImportReady
    }

    private var detailInflationWarning: String? {
        isResolvedAlphaSmokeFixture ? nil : mission.inflationWarning
    }

    private var detailMissionReasonTitle: String {
        isResolvedAlphaSmokeFixture ? "Smoke test route" : "Why this mission now"
    }

    private var detailMissionReason: String? {
        if isResolvedAlphaSmokeFixture {
            return "This fixed Alpha route is for playback and reaction smoke testing. It verifies resolved Apple Music links, reactions, and progress persistence; it is not yet personalized from your Survey responses."
        }

        return mission.whyThisMissionNow
    }

    private var detailImportStatusLabel: String? {
        guard let status = mission.alphaAppImportStatus else {
            return nil
        }

        switch status {
        case .appImportReady:
            return "Playback ready"
        case .appImportCandidate:
            return "Import candidate"
        case .appImportBlockedPolicy, .appImportBlockedUnresolved:
            return "Import blocked"
        case .reviewOnly:
            return "Review only"
        case .schemaValid:
            return "Schema valid"
        case .contractValid:
            return "Contract valid"
        case .needsRevision:
            return "Needs revision"
        case .rejectedProduct:
            return "Rejected"
        }
    }

    private func detailWhyIncluded(for item: MissionItem) -> String? {
        guard isResolvedAlphaSmokeFixture else {
            return item.whyIncluded
        }

        if let role = item.alphaRouteRole {
            return "Included as a \(role.displayName.lowercased()) item in this fixed playback route."
        }

        return "Included in this fixed playback route."
    }
}

private struct MissionInfoPill: View {
    let label: String

    var body: some View {
        Text(label)
            .font(.caption2.weight(.bold))
            .foregroundStyle(WaymarkTheme.text)
            .padding(.horizontal, 7)
            .padding(.vertical, 4)
            .background(WaymarkTheme.raisedPanel, in: Capsule())
    }
}

struct ResolutionBadge: View {
    let status: ResolutionStatus

    var body: some View {
        Text(status.rawValue)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .foregroundStyle(WaymarkTheme.route)
            .background(WaymarkTheme.route.opacity(0.12), in: Capsule())
    }
}

private struct MissionMetricCard: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(value)
                .font(.title3.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
            Text(title)
                .font(.caption)
                .foregroundStyle(WaymarkTheme.mutedText)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                .stroke(WaymarkTheme.line, lineWidth: 1)
        )
    }
}
