import SwiftUI

struct MissionReviewView: View {
    @EnvironmentObject private var appModel: AppModel

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("Mission Review")
        }
    }

    @ViewBuilder
    private var content: some View {
        let snapshot = appModel.missionReviewSnapshot

        if let mission = snapshot.mission {
            List {
                MissionReviewSummarySection(
                    mission: mission,
                    summary: snapshot.summary
                )

                Section("Route Items") {
                    ForEach(snapshot.items) { evidence in
                        NavigationLink {
                            MissionReviewItemEditorView(itemID: evidence.item.itemID)
                        } label: {
                            MissionReviewRow(evidence: evidence)
                        }
                    }
                }

                if let message = appModel.lastActionMessage {
                    Section("Last Action") {
                        Text(message)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        } else {
            ContentUnavailableView(
                "No mission loaded",
                systemImage: "music.note.list",
                description: Text("Load a mission before reviewing evidence.")
            )
        }
    }
}

private struct MissionReviewSummarySection: View {
    let mission: Mission
    let summary: MissionReviewSummary

    var body: some View {
        Section {
            VStack(alignment: .leading, spacing: 10) {
                Text(mission.missionTitle)
                    .font(.headline)

                Text(mission.hypothesis)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)

                ReviewPill(
                    title: summary.readinessLabel,
                    systemImage: summary.reviewNeededCount == 0 ? "checkmark.circle" : "exclamationmark.circle",
                    tint: summary.reviewNeededCount == 0 ? .green : .orange
                )
            }
            .padding(.vertical, 4)

            LabeledContent("Resolved", value: "\(summary.resolvedCount)/\(summary.itemCount)")
            LabeledContent("Playback Evidence", value: "\(summary.playbackEvidenceCount)/\(summary.itemCount)")
            LabeledContent("Completed", value: "\(summary.completedCount)")
            LabeledContent("Skipped", value: "\(summary.skippedCount)")
            LabeledContent("Reactions", value: "\(summary.reactionCount)")
            LabeledContent("Exportable Items", value: "\(summary.exportableEvidenceCount)")
            LabeledContent("Review Needed", value: "\(summary.reviewNeededCount)")
        } header: {
            Text("Evidence Summary")
        }
    }
}

private struct MissionReviewRow: View {
    let evidence: MissionReviewItemEvidence

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Text("\(evidence.item.sequence). \(evidence.item.title)")
                    .font(.headline)
                    .lineLimit(2)

                Spacer(minLength: 8)

                if evidence.needsReview {
                    Image(systemName: "exclamationmark.circle.fill")
                        .foregroundStyle(.orange)
                } else if evidence.isExportableEvidenceCandidate {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                }
            }

            Text(evidence.item.artist)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack(spacing: 6) {
                ReviewPill(title: evidence.resolution.status.rawValue, systemImage: "magnifyingglass", tint: .blue)
                ReviewPill(title: evidence.playbackLabel, systemImage: "play.circle", tint: playbackTint)
                ReviewPill(title: evidence.reactionLabel, systemImage: "slider.horizontal.3", tint: reactionTint)
            }

            if !evidence.flags.isEmpty {
                FlowPillRow(flags: evidence.flags)
            }

            if evidence.reaction != nil {
                Text(evidence.selectedTagLabel)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
        }
        .padding(.vertical, 5)
    }

    private var playbackTint: Color {
        switch evidence.playback.status {
        case .played:
            return .green
        case .playing:
            return .blue
        case .skipped:
            return .orange
        case .failed:
            return .red
        case .queued, .notAttempted:
            return .secondary
        }
    }

    private var reactionTint: Color {
        guard let reaction = evidence.reaction?.reactionValue else {
            return .secondary
        }

        switch reaction.operation {
        case .strongPositive:
            return .green
        case .qualifiedPositive:
            return .yellow
        case .keepWaypoint:
            return .orange
        case .negative:
            return .red
        case nil:
            return .secondary
        }
    }
}

private struct MissionReviewItemEditorView: View {
    @EnvironmentObject private var appModel: AppModel

    let itemID: String

    @State private var selectedReaction: ReactionValue?
    @State private var selectedTagIDs: Set<String> = []
    @State private var note = ""

    var body: some View {
        Group {
            if let evidence = appModel.missionReviewEvidence(for: itemID) {
                List {
                    Section("Evidence") {
                        LabeledContent("Track", value: "\(evidence.item.sequence). \(evidence.item.title)")
                        LabeledContent("Artist", value: evidence.item.artist)
                        LabeledContent("Resolution", value: evidence.resolution.status.rawValue)
                        LabeledContent("Playback", value: evidence.playbackLabel)
                        LabeledContent("Reaction", value: evidence.reactionLabel)

                        if !evidence.flags.isEmpty {
                            FlowPillRow(flags: evidence.flags)
                        }
                    }

                    Section("Primary Signal") {
                        SignalGrid(
                            selectedReaction: selectedReaction,
                            selectReaction: { reaction in
                                if selectedReaction != reaction {
                                    selectedTagIDs.removeAll()
                                }
                                selectedReaction = reaction
                            }
                        )

                        Button {
                            selectedReaction = .unresolved
                            selectedTagIDs.removeAll()
                            save(evidence: evidence)
                        } label: {
                            Label("Keep As No Signal", systemImage: "circle.dashed")
                        }
                    }

                    Section("Context Tags") {
                        if let selectedReaction, ReactionValue.primarySignalValues.contains(selectedReaction) {
                            let chips = evidence.item.feedbackChips(for: selectedReaction)
                            if chips.isEmpty {
                                Text("No contextual tags are defined for this signal yet.")
                                    .foregroundStyle(.secondary)
                            } else {
                                ForEach(chips) { chip in
                                    Button {
                                        toggle(chip)
                                    } label: {
                                        HStack {
                                            VStack(alignment: .leading, spacing: 3) {
                                                Text(chip.label)
                                                if let description = chip.description {
                                                    Text(description)
                                                        .font(.caption)
                                                        .foregroundStyle(.secondary)
                                                }
                                            }

                                            Spacer()

                                            if selectedTagIDs.contains(chip.tagID) {
                                                Image(systemName: "checkmark.circle.fill")
                                                    .foregroundStyle(.green)
                                            }
                                        }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        } else {
                            Text("Choose a primary signal before selecting context tags.")
                                .foregroundStyle(.secondary)
                        }
                    }

                    Section("Notes") {
                        TextField("Optional note", text: $note, axis: .vertical)
                            .lineLimit(3...8)
                    }

                    Section {
                        Button {
                            save(evidence: evidence)
                        } label: {
                            Label("Save Review Edits", systemImage: "checkmark.circle")
                        }
                        .disabled(selectedReaction == nil)

                        Button {
                            appModel.selectItem(evidence.item)
                        } label: {
                            Label("Set As Player Item", systemImage: "play.circle")
                        }
                    }
                }
                .navigationTitle(evidence.item.title)
                .navigationBarTitleDisplayMode(.inline)
                .onAppear {
                    hydrate(from: evidence)
                }
                .onChange(of: appModel.reactionRevision) { _, _ in
                    if let refreshed = appModel.missionReviewEvidence(for: itemID) {
                        hydrate(from: refreshed)
                    }
                }
            } else {
                ContentUnavailableView(
                    "Evidence unavailable",
                    systemImage: "questionmark.circle",
                    description: Text("This mission item is no longer available.")
                )
            }
        }
    }

    private func hydrate(from evidence: MissionReviewItemEvidence) {
        selectedReaction = evidence.reaction?.reactionValue
        selectedTagIDs = Set(evidence.reaction?.selectedTags?.map(\.tagID) ?? [])
        note = evidence.noteText
    }

    private func toggle(_ chip: FeedbackChipOption) {
        if selectedTagIDs.contains(chip.tagID) {
            selectedTagIDs.remove(chip.tagID)
        } else {
            selectedTagIDs.insert(chip.tagID)
        }
    }

    private func save(evidence: MissionReviewItemEvidence) {
        let tags: [ReactionTag]
        if let selectedReaction, ReactionValue.primarySignalValues.contains(selectedReaction) {
            tags = evidence.item.feedbackChips(for: selectedReaction)
                .filter { selectedTagIDs.contains($0.tagID) }
                .map { $0.reactionTag(primaryReactionValue: selectedReaction) }
        } else {
            tags = []
        }

        appModel.saveReaction(
            for: evidence.item,
            value: selectedReaction,
            note: note,
            selectedTags: tags
        )
    }
}

private struct SignalGrid: View {
    let selectedReaction: ReactionValue?
    let selectReaction: (ReactionValue) -> Void

    private let columns = [
        GridItem(.flexible(), spacing: 8),
        GridItem(.flexible(), spacing: 8)
    ]

    var body: some View {
        LazyVGrid(columns: columns, spacing: 8) {
            ForEach(ReactionValue.primarySignalValues) { reaction in
                Button {
                    selectReaction(reaction)
                } label: {
                    HStack {
                        Image(systemName: Self.systemImage(for: reaction))
                        Text(reaction.displayName)
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, minHeight: 42)
                    .background(
                        selectedReaction == reaction ? Color.accentColor.opacity(0.22) : Color.secondary.opacity(0.12),
                        in: RoundedRectangle(cornerRadius: 8)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(selectedReaction == reaction ? Color.accentColor : Color.secondary.opacity(0.2), lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
            }
        }
    }

    private static func systemImage(for reaction: ReactionValue) -> String {
        switch reaction {
        case .hit:
            return "star.fill"
        case .partial:
            return "circle.lefthalf.filled"
        case .okShelf:
            return "minus.circle.fill"
        case .miss:
            return "xmark"
        case .slop:
            return "xmark.octagon"
        case .skipped:
            return "forward.end"
        case .unresolved:
            return "circle.dashed"
        }
    }
}

private struct FlowPillRow: View {
    let flags: [MissionReviewFlag]

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            ForEach(flags) { flag in
                ReviewPill(title: flag.label, systemImage: flag.systemImage, tint: .orange)
            }
        }
    }
}

private struct ReviewPill: View {
    let title: String
    let systemImage: String
    let tint: Color

    var body: some View {
        Label(title, systemImage: systemImage)
            .font(.caption.weight(.semibold))
            .lineLimit(1)
            .minimumScaleFactor(0.76)
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .foregroundStyle(tint)
            .background(tint.opacity(0.12), in: Capsule())
    }
}
