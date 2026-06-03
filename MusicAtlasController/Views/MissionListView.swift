import SwiftUI

struct MissionListView: View {
    @EnvironmentObject private var appModel: AppModel
    @State private var importSheet: MissionImportSheet?
    @State private var importDraft = ""
    @State private var showResetConfirmation = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Missions")
                                .font(.largeTitle.weight(.bold))
                                .foregroundStyle(WaymarkTheme.text)
                            Text(appModel.hasReviewedMissionAssignments ? "Reviewed routes ready for Alpha listening." : "Waiting for a reviewed mission assignment.")
                                .font(.callout)
                                .foregroundStyle(WaymarkTheme.mutedText)
                        }

                        Spacer()

                        Text(appModel.hasReviewedMissionAssignments ? "Ready" : "Waiting")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(appModel.hasReviewedMissionAssignments ? WaymarkTheme.positive.opacity(0.18) : WaymarkTheme.waypoint.opacity(0.18), in: Capsule())
                    }

                    switch appModel.missionLoadState {
                    case .idle, .loading:
                        ProgressView("Loading missions")
                            .tint(WaymarkTheme.route)
                            .frame(maxWidth: .infinity, minHeight: 120)
                    case .failed(let message):
                        MissionSurfaceNotice(
                            title: "Mission failed to load",
                            detail: message,
                            systemImage: "exclamationmark.triangle",
                            tint: WaymarkTheme.negative
                        )
                    case .loaded:
                        loadedMissionContent
                    }

                    if let message = appModel.lastActionMessage {
                        MissionSurfaceNotice(
                            title: "Latest update",
                            detail: message,
                            systemImage: "info.circle",
                            tint: WaymarkTheme.signal
                        )
                    }

                    if AppFeatureFlags.showDiagnosticTabs {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Apple Music")
                                .font(.headline)
                                .foregroundStyle(WaymarkTheme.text)
                            MusicAuthorizationPanel(service: appModel.musicAuthorization)
                        }
                        .padding(14)
                        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
                    }
                }
                .padding(18)
            }
            .background(WaymarkTheme.background.ignoresSafeArea())
            .navigationTitle("Cartenza")
            .sheet(item: $importSheet) { sheet in
                importSheetView(sheet)
            }
            .confirmationDialog(
                "Reset reviewed missions and local mission sessions?",
                isPresented: $showResetConfirmation,
                titleVisibility: .visible
            ) {
                Button("Reset", role: .destructive) {
                    appModel.resetReviewedMissionAssignmentsAndSessions()
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Reviewed/imported assignments and their local session state are cleared.")
            }
        }
    }

    @ViewBuilder
    private var loadedMissionContent: some View {
        if let mission = appModel.mission {
            VStack(alignment: .leading, spacing: 10) {
                Text("Now assigned")
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                NavigationLink {
                    MissionDetailView(
                        mission: mission,
                        atlasExplainerStore: appModel.atlasExplainerStore
                    )
                } label: {
                    MissionCard(
                        assignment: appModel.missionAssignment(for: mission) ?? MissionAssignment(
                            mission: mission,
                            source: .manualReviewed,
                            importedAt: Date(),
                            sourceRunID: nil,
                            importNote: nil
                        ),
                        isActive: true
                    )
                }
                .buttonStyle(.plain)
            }
        }

        VStack(alignment: .leading, spacing: 10) {
            Text("Reviewed mission assignments")
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)

            if appModel.reviewedMissionAssignments.isEmpty {
                MissionlessEmptyState(
                    showSupportActions: AppFeatureFlags.showDiagnosticTabs,
                    openManualImport: {
                        importSheet = .manualReviewed
                    },
                    openGeneratedImport: {
                        importSheet = .supabaseResponse
                    }
                )
            } else {
                ForEach(appModel.reviewedMissionAssignments) { assignment in
                    NavigationLink {
                        MissionDetailView(
                            mission: assignment.mission,
                            atlasExplainerStore: appModel.atlasExplainerStore
                        )
                    } label: {
                        MissionCard(
                            assignment: assignment,
                            isActive: appModel.isActiveMission(assignment.mission)
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
        }

        if AppFeatureFlags.showAlphaUATFixtureControls && !AppFeatureFlags.showDiagnosticTabs {
            VStack(alignment: .leading, spacing: 10) {
                Button {
                    appModel.importLocalAlphaAppImportReadyUATFixtures()
                } label: {
                    Label("Load Resolved UAT Fixtures", systemImage: "play.rectangle.on.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.bordered)
            }
        }

        if AppFeatureFlags.showDiagnosticTabs {
            VStack(alignment: .leading, spacing: 10) {
                Text("Support assignment")
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)

                Button {
                    importSheet = .manualReviewed
                } label: {
                    Label("Paste Reviewed Mission", systemImage: "doc.badge.plus")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.borderedProminent)

                Button {
                    importSheet = .supabaseResponse
                } label: {
                    Label("Paste Generation Response", systemImage: "tray.and.arrow.down")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.bordered)

                Button {
                    appModel.importLocalAlphaApprovedCandidateFixtures()
                } label: {
                    Label("Load Local Alpha Fixtures", systemImage: "shippingbox.and.arrow.down")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.bordered)

                Button {
                    appModel.importLocalAlphaAppImportReadyUATFixtures()
                } label: {
                    Label("Load Resolved UAT Fixtures", systemImage: "play.rectangle.on.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.bordered)
            }

            VStack(alignment: .leading, spacing: 10) {
                Button(role: .destructive) {
                    showResetConfirmation = true
                } label: {
                    Label("Reset Reviewed Missions and Sessions", systemImage: "arrow.counterclockwise")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.bordered)
            }
        }
    }

    private func importSheetView(_ sheet: MissionImportSheet) -> some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 14) {
                Text(sheet.instructions)
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                TextEditor(text: $importDraft)
                    .font(.system(.body, design: .monospaced))
                    .frame(minHeight: 240)
                    .padding(8)
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 10))

                Spacer()
            }
            .padding()
            .navigationTitle(sheet.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        importDraft = ""
                        importSheet = nil
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Import") {
                        switch sheet {
                        case .manualReviewed:
                            appModel.importReviewedMissionJSON(importDraft)
                        case .supabaseResponse:
                            appModel.importSupabaseMissionBatchResponseJSON(importDraft)
                        }
                        importDraft = ""
                        importSheet = nil
                    }
                    .disabled(importDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
}

private enum MissionImportSheet: String, Identifiable {
    case manualReviewed
    case supabaseResponse

    var id: String {
        rawValue
    }

    var title: String {
        switch self {
        case .manualReviewed:
            return "Reviewed Assignment"
        case .supabaseResponse:
            return "Cartenza Assignment"
        }
    }

    var instructions: String {
        switch self {
        case .manualReviewed:
            return "Paste a reviewed mission assignment from Cartenza support. The app rejects assignments that are not marked ready for app import."
        case .supabaseResponse:
            return "Paste a generated assignment packet from Cartenza support. Only reviewed app-ready packets will import."
        }
    }
}

private struct MissionlessEmptyState: View {
    let showSupportActions: Bool
    let openManualImport: () -> Void
    let openGeneratedImport: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("No reviewed mission assigned", systemImage: "tray")
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)

            Text(showSupportActions ? "Cartenza now starts missionless in production. Import a reviewed mission assignment or an app-import-candidate generation response before listening." : "Cartenza is still preparing the first Alpha mission batch. You can return here once generation finishes.")
                .font(.callout)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            if showSupportActions {
                VStack(spacing: 10) {
                    Button("Paste Reviewed Mission", action: openManualImport)
                        .frame(maxWidth: .infinity)
                        .buttonStyle(.borderedProminent)

                    Button("Paste Generation Response", action: openGeneratedImport)
                        .frame(maxWidth: .infinity)
                        .buttonStyle(.bordered)
                }
                .font(.caption.weight(.semibold))
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(WaymarkTheme.line, lineWidth: 1)
        )
    }
}

private struct MissionCard: View {
    let assignment: MissionAssignment
    let isActive: Bool

    private var mission: Mission {
        assignment.mission
    }

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            VStack(alignment: .leading, spacing: 8) {
                Text(mission.missionTitle)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)

                Text(mission.missionType.displayName)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(WaymarkTheme.route)

                Text(mission.hypothesis)
                    .font(.subheadline)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .lineLimit(3)

                HStack(spacing: 8) {
                    Label("\(mission.items.count) items", systemImage: "music.note")
                    Label("Play \(mission.successBar.minimumItemsToPlay)", systemImage: "play.circle")
                    Text(assignment.source.displayName)
                        .font(.caption2.weight(.bold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(WaymarkTheme.raisedPanel, in: Capsule())
                }
                .font(.caption)
                .foregroundStyle(WaymarkTheme.mutedText)
            }

            if isActive {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundStyle(WaymarkTheme.positive)
                    .font(.title3)
                    .accessibilityLabel("Active mission")
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(isActive ? WaymarkTheme.route.opacity(0.45) : WaymarkTheme.line, lineWidth: 1)
        )
    }
}

private struct MissionSurfaceNotice: View {
    let title: String
    let detail: String
    let systemImage: String
    let tint: Color

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: systemImage)
                .foregroundStyle(tint)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                Text(detail)
                    .font(.callout)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer()
        }
        .padding(14)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(WaymarkTheme.line, lineWidth: 1)
        )
    }
}
