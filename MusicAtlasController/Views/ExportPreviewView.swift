import SwiftUI

struct ExportPreviewView: View {
    @EnvironmentObject private var appModel: AppModel

    var body: some View {
        NavigationStack {
            List {
                Section("Export Contract") {
                    LabeledContent("JSON schema", value: "reaction_session.v0.2")
                    LabeledContent("Reconciliation", value: "not_reconciled")
                    LabeledContent("Markdown", value: "discovery_log_template_v0_2")
                    LabeledContent("Dev path", value: "data/exports/dev/")
                    LabeledContent("Acceptance path", value: "data/exports/acceptance/")
                }

                AppleMusicSignalProbePanel()

                MissionExportReadinessSection(progress: appModel.missionProgress)

                Section("Current Mission") {
                    if let mission = appModel.mission {
                        LabeledContent("Mission", value: mission.missionTitle)
                        LabeledContent("Items", value: "\(mission.items.count)")
                        LabeledContent("Resolved", value: "\(appModel.missionProgress.resolvedCount)")
                        LabeledContent("Played", value: "\(appModel.missionProgress.playedCount)")
                        LabeledContent("Reacted", value: "\(appModel.missionProgress.reactionCount)")
                        if let item = appModel.selectedItem {
                            LabeledContent("Selected", value: item.title)
                            LabeledContent("Resolution", value: appModel.resolution(for: item).status.rawValue)
                            LabeledContent("Playback", value: appModel.playback(for: item).status.rawValue)
                        }
                    } else {
                        Text("No mission loaded")
                            .foregroundStyle(.secondary)
                    }
                }

                Section {
                    Button {
                        appModel.generateDevelopmentExportPreview()
                    } label: {
                        Label("Generate Dev Stub Mission Export", systemImage: "doc.text")
                    }
                    .disabled(!appModel.canGenerateDevelopmentMissionExport)

                    Button {
                        appModel.generateAcceptanceExportPreview()
                    } label: {
                        Label("Generate Acceptance Mission Export", systemImage: "checkmark.seal")
                    }
                    .disabled(!appModel.canGenerateAcceptanceMissionExport)
                }

                if let preview = appModel.exportPreview {
                    Section("Files") {
                        LabeledContent("JSON", value: preview.jsonFilename)
                        LabeledContent("Markdown", value: preview.markdownFilename)

                        Button {
                            appModel.saveCurrentExportFiles()
                        } label: {
                            Label("Save Export Files", systemImage: "square.and.arrow.down")
                        }
                    }

                    if let savedExport = appModel.savedExport {
                        Section("Saved Export") {
                            LabeledContent("Type", value: savedExport.kind.displayName)
                            LabeledContent("Folder", value: savedExport.directoryURL.lastPathComponent)
                            LabeledContent("JSON", value: savedExport.jsonURL.lastPathComponent)
                            LabeledContent("Markdown", value: savedExport.markdownURL.lastPathComponent)

                            ShareLink(items: savedExport.shareURLs) {
                                Label("Share Saved Files", systemImage: "square.and.arrow.up")
                            }
                        }
                    }

                    Section("JSON Preview") {
                        ScrollView(.horizontal) {
                            Text(preview.jsonString)
                                .font(.system(.caption, design: .monospaced))
                                .textSelection(.enabled)
                        }
                    }

                    Section("Markdown Preview") {
                        Text(preview.markdownString)
                            .font(.caption)
                            .textSelection(.enabled)
                    }
                }

                if let message = appModel.lastActionMessage {
                    Section("Last Action") {
                        Text(message)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Export")
        }
    }
}

struct MissionExportReadinessSection: View {
    let progress: MissionProgress

    var body: some View {
        Section("Mission Export Readiness") {
            ReadinessRow(
                title: "Resolved",
                isComplete: progress.resolvedCount > 0,
                detail: "\(progress.resolvedCount) of \(progress.itemCount)"
            )
            ReadinessRow(
                title: "Played",
                isComplete: progress.playedCount > 0,
                detail: "\(progress.playedCount) of \(progress.itemCount)"
            )
            ReadinessRow(
                title: "Reacted",
                isComplete: progress.reactionCount > 0,
                detail: "\(progress.reactionCount) of \(progress.itemCount)"
            )
        }
    }
}

struct ReadinessRow: View {
    let title: String
    let isComplete: Bool
    let detail: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: isComplete ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(isComplete ? .green : .secondary)
                .imageScale(.large)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                Text(detail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
