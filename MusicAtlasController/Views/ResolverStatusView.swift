import SwiftUI

struct ResolverStatusView: View {
    @EnvironmentObject private var appModel: AppModel

    var body: some View {
        NavigationStack {
            List {
                Section("Service Mode") {
                    Picker("Service Mode", selection: $appModel.musicServiceMode) {
                        ForEach(MusicServiceMode.allCases) { mode in
                            Text(mode.displayName).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)

                    Text(appModel.musicServiceMode.detail)
                        .foregroundStyle(.secondary)

                    Button {
                        Task {
                            await appModel.resolveAllMissionItems()
                        }
                    } label: {
                        Label(appModel.isResolvingMission ? "Resolving Mission" : "Resolve Whole Mission", systemImage: "wand.and.stars")
                    }
                    .disabled(appModel.isResolvingMission)
                }

                Section("Catalog Resolution") {
                    Text("Resolution stores candidate count, confidence, resolver method, storefront, and resolved catalog metadata.")
                        .foregroundStyle(.secondary)

                    if let mission = appModel.mission {
                        ForEach(mission.items) { item in
                            Button {
                                appModel.selectItem(item)
                            } label: {
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(item.title)
                                        Text(item.artist)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                    }
                                    Spacer()
                                    if appModel.selectedItemID == item.itemID {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(.green)
                                    }
                                    ResolutionBadge(status: appModel.resolution(for: item).status)
                                }
                            }
                        }
                    }
                }

                Section("Selected Item") {
                    if let item = appModel.selectedItem {
                        let resolution = appModel.resolution(for: item)

                        LabeledContent("Title", value: item.title)
                        LabeledContent("Artist", value: item.artist)
                        LabeledContent("Status", value: resolution.status.rawValue)
                        LabeledContent("Playback", value: appModel.playback(for: item).status.rawValue)
                        LabeledContent("Candidate Count", value: Self.displayCount(resolution.candidateCount))
                        LabeledContent("Confidence", value: Self.displayConfidence(resolution.confidence))
                        LabeledContent("Resolver", value: resolution.resolver?.rawValue ?? "none")
                        LabeledContent("Storefront", value: resolution.storefront ?? "none")
                        LabeledContent("Catalog ID", value: resolution.catalogID ?? "none")
                        if let reason = resolution.reason {
                            LabeledContent("Reason", value: reason)
                        }
                        if let errorCode = resolution.errorCode {
                            LabeledContent("Error Code", value: errorCode)
                        }
                        if let errorMessage = resolution.errorMessage {
                            Text(errorMessage)
                                .font(.caption.monospaced())
                                .foregroundStyle(.secondary)
                                .textSelection(.enabled)
                        }

                        Button {
                            Task {
                                await appModel.resolveSelectedItem()
                            }
                        } label: {
                            Label(appModel.musicServiceMode.resolveButtonTitle, systemImage: "wand.and.stars")
                        }

                        Button {
                            appModel.markSelectedItemSkipped()
                        } label: {
                            Label("Mark Skipped", systemImage: "forward.end")
                        }

                        Button {
                            appModel.markSelectedItemUnavailableRegion()
                        } label: {
                            Label("Unavailable Region", systemImage: "globe")
                        }

                        Button {
                            appModel.markSelectedItemUnavailableSubscription()
                        } label: {
                            Label("Unavailable Subscription", systemImage: "person.crop.circle.badge.exclamationmark")
                        }

                        Button(role: .destructive) {
                            appModel.resetSelectedItemResolution()
                        } label: {
                            Label("Reset Unresolved", systemImage: "arrow.counterclockwise")
                        }
                    } else {
                        Text("No item selected")
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
            .navigationTitle("Resolve")
        }
    }

    private static func displayCount(_ count: Int?) -> String {
        count.map(String.init) ?? "none"
    }

    private static func displayConfidence(_ confidence: Double?) -> String {
        guard let confidence else {
            return "none"
        }

        return confidence.formatted(.number.precision(.fractionLength(2)))
    }
}
