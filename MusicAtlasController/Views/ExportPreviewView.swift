import SwiftUI

struct ExportPreviewView: View {
    @EnvironmentObject private var appModel: AppModel

    var body: some View {
        NavigationStack {
            List {
                if AppFeatureFlags.showExportDebugPanels {
                    Section("Export Contract") {
                        LabeledContent("JSON schema", value: "reaction_session.v0.2")
                        LabeledContent("Reconciliation", value: "not_reconciled")
                        LabeledContent("Markdown", value: "discovery_log_template_v0_2")
                        LabeledContent("Dev path", value: "data/exports/dev/")
                        LabeledContent("Acceptance path", value: "data/exports/acceptance/")
                    }
                } else {
                    Section("Share Evidence") {
                        Text("Prepare a local evidence package from the current mission. This is provisional Alpha evidence, not promoted Atlas truth.")
                            .font(.callout)
                            .foregroundStyle(.secondary)
                    }
                }

                if AppFeatureFlags.showExportDebugPanels {
                    AppleMusicSignalProbePanel()
                }

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
                    if AppFeatureFlags.showExportDebugPanels {
                        Button {
                            appModel.generateDevelopmentExportPreview()
                        } label: {
                            Label("Generate Dev Stub Mission Export", systemImage: "doc.text")
                        }
                        .disabled(!appModel.canGenerateDevelopmentMissionExport)
                    }

                    Button {
                        appModel.generateAcceptanceExportPreview()
                    } label: {
                        Label(AppFeatureFlags.showExportDebugPanels ? "Generate Acceptance Mission Export" : "Prepare Share Evidence Package", systemImage: "checkmark.seal")
                    }
                    .disabled(!appModel.canGenerateAcceptanceMissionExport)
                }

                if let preview = appModel.exportPreview {
                    Section(AppFeatureFlags.showExportDebugPanels ? "Files" : "Evidence Package") {
                        if AppFeatureFlags.showExportDebugPanels {
                            LabeledContent("JSON", value: preview.jsonFilename)
                            LabeledContent("Markdown", value: preview.markdownFilename)
                            LabeledContent("Atlas candidates", value: "\(preview.atlasSignalCandidateCount)")
                        } else {
                            LabeledContent("Items represented", value: "\(appModel.missionProgress.playedCount)")
                            LabeledContent("Evidence candidates", value: "\(preview.atlasSignalCandidateCount)")
                        }

                        Button {
                            appModel.saveCurrentExportFiles()
                        } label: {
                            Label(AppFeatureFlags.showExportDebugPanels ? "Save Export Files" : "Save Share Package", systemImage: "square.and.arrow.down")
                        }
                    }

                    if let savedExport = appModel.savedExport {
                        Section(AppFeatureFlags.showExportDebugPanels ? "Saved Export" : "Saved Evidence") {
                            if AppFeatureFlags.showExportDebugPanels {
                                LabeledContent("Type", value: savedExport.kind.displayName)
                                LabeledContent("Folder", value: savedExport.directoryURL.lastPathComponent)
                                LabeledContent("JSON", value: savedExport.jsonURL.lastPathComponent)
                                LabeledContent("Markdown", value: savedExport.markdownURL.lastPathComponent)
                            } else {
                                Text("Share these files with the Cartenza Alpha team if requested.")
                                    .font(.callout)
                                    .foregroundStyle(.secondary)
                            }

                            ShareLink(items: savedExport.shareURLs) {
                                Label("Share Evidence Files", systemImage: "square.and.arrow.up")
                            }

                            Button {
                                Task {
                                    await appModel.uploadSavedEvidenceManually()
                                }
                            } label: {
                                Label(
                                    appModel.isEvidenceUploadInFlight ? "Uploading Evidence" : "Upload Evidence to Cartenza",
                                    systemImage: "arrow.up.circle"
                                )
                            }
                            .disabled(appModel.isEvidenceUploadInFlight || !appModel.isSupabaseAuthenticated)

                            if let result = appModel.lastEvidenceUploadResult {
                                LabeledContent("Upload", value: result.status)
                                LabeledContent("User attached", value: result.userIDPresent == true ? "yes" : "no")
                            }
                        }
                    }

                    if AppFeatureFlags.showExportDebugPanels {
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
                }

                Section("Support Diagnostics") {
                    Text("Creates a support-only audit package for the Cartenza team: Apple Music signal, Survey page selection, Survey evidence, generation attempts, import outcomes, and client errors when available.")
                        .font(.callout)
                        .foregroundStyle(.secondary)

                    Button {
                        appModel.saveSupportDiagnosticPackage()
                    } label: {
                        Label("Prepare Support Diagnostics", systemImage: "stethoscope")
                    }

                    if let package = appModel.savedSupportDiagnosticsPackage {
                        LabeledContent("Artifacts", value: "\(package.artifactURLs.count)")
                        ShareLink(items: package.shareURLs) {
                            Label("Share Support Diagnostics", systemImage: "square.and.arrow.up")
                        }

                        Button {
                            Task {
                                await appModel.uploadSupportDiagnosticsManually()
                            }
                        } label: {
                            Label(
                                appModel.isDiagnosticUploadInFlight ? "Uploading Diagnostics" : "Upload Diagnostics to Cartenza",
                                systemImage: "arrow.up.doc"
                            )
                        }
                        .disabled(appModel.isDiagnosticUploadInFlight)

                        if let result = appModel.lastDiagnosticUploadResult {
                            LabeledContent("Upload", value: result.status)
                            LabeledContent("Artifacts uploaded", value: "\(result.uploadedCount)")
                            LabeledContent("User attached", value: result.userIDPresent == true ? "yes" : "no")
                        }

                        Text("Manual diagnostic upload is support-only. Automatic diagnostic upload remains blocked until final privacy/support policy is approved.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                if let message = appModel.lastActionMessage {
                    Section("Last Action") {
                        Text(message)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Share Evidence")
        }
    }
}

struct MissionExportReadinessSection: View {
    let progress: MissionProgress

    var body: some View {
        Section("Evidence Readiness") {
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
