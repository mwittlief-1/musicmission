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
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Review Rail")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(WaymarkTheme.route)
                            .textCase(.uppercase)
                        Text("Review the songs Cartenza heard.")
                            .font(.largeTitle.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)
                            .fixedSize(horizontal: false, vertical: true)
                        Text("Edit only the evidence that needs more depth. No-signal and skipped items can remain unresolved.")
                            .font(.callout)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    MissionReviewSummaryPanel(
                        mission: mission,
                        summary: snapshot.summary
                    )

                    Text("Route items")
                        .font(.headline)
                        .foregroundStyle(WaymarkTheme.text)

                    ForEach(snapshot.items) { evidence in
                        NavigationLink {
                            MissionReviewItemEditorView(itemID: evidence.item.itemID)
                        } label: {
                            MissionReviewRow(evidence: evidence)
                        }
                        .buttonStyle(.plain)
                    }

                    if let message = appModel.lastActionMessage {
                        Text(message)
                            .font(.callout)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
                    }
                }
                .padding(18)
            }
            .background(WaymarkTheme.background.ignoresSafeArea())
        } else {
            ContentUnavailableView(
                "No mission loaded",
                systemImage: "music.note.list",
                description: Text("Load a mission before reviewing evidence.")
            )
        }
    }
}

private struct MissionReviewSummaryPanel: View {
    let mission: Mission
    let summary: MissionReviewSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(mission.missionTitle)
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)

            Text(mission.hypothesis)
                .font(.caption)
                .foregroundStyle(WaymarkTheme.mutedText)
                .lineLimit(3)

            ReviewPill(
                title: summary.readinessLabel,
                systemImage: summary.reviewNeededCount == 0 ? "checkmark.circle" : "exclamationmark.circle",
                tint: summary.reviewNeededCount == 0 ? WaymarkTheme.positive : WaymarkTheme.waypoint
            )

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                ReviewMetric(title: "Playable", value: "\(summary.resolvedCount)/\(summary.itemCount)")
                ReviewMetric(title: "Evidence", value: "\(summary.playbackEvidenceCount)/\(summary.itemCount)")
                ReviewMetric(title: "Skipped", value: "\(summary.skippedCount)")
                ReviewMetric(title: "Review Needed", value: "\(summary.reviewNeededCount)")
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

private struct ReviewMetric: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(value)
                .font(.headline.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
            Text(title)
                .font(.caption)
                .foregroundStyle(WaymarkTheme.mutedText)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(WaymarkTheme.raisedPanel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
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
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                .stroke(evidence.needsReview ? WaymarkTheme.waypoint.opacity(0.45) : WaymarkTheme.line, lineWidth: 1)
        )
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
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Edit Evidence")
                                .font(.caption.weight(.bold))
                                .foregroundStyle(WaymarkTheme.route)
                                .textCase(.uppercase)
                            Text(evidence.item.title)
                                .font(.largeTitle.weight(.bold))
                                .foregroundStyle(WaymarkTheme.text)
                                .fixedSize(horizontal: false, vertical: true)
                            Text(evidence.item.artist)
                                .font(.title3)
                                .foregroundStyle(WaymarkTheme.mutedText)
                        }

                        VStack(alignment: .leading, spacing: 10) {
                            EvidenceLine(title: "Track", value: "\(evidence.item.sequence). \(evidence.item.title)")
                            EvidenceLine(title: "Resolution", value: evidence.resolution.status.rawValue)
                            EvidenceLine(title: "Playback", value: evidence.playbackLabel)
                            EvidenceLine(title: "Reaction", value: evidence.reactionLabel)

                            if !evidence.flags.isEmpty {
                                FlowPillRow(flags: evidence.flags)
                            }
                        }
                        .padding(14)
                        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
                        .overlay(
                            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                                .stroke(WaymarkTheme.line, lineWidth: 1)
                        )

                        Text("Primary signal")
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)

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
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)

                        Text("Context tags")
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)

                        if let selectedReaction, ReactionValue.primarySignalValues.contains(selectedReaction) {
                            let chips = evidence.item.feedbackChips(for: selectedReaction)
                            if chips.isEmpty {
                                Text("No contextual tags are defined for this signal yet.")
                                    .foregroundStyle(WaymarkTheme.mutedText)
                            } else {
                                VStack(spacing: 8) {
                                    ForEach(chips) { chip in
                                        Button {
                                            toggle(chip)
                                        } label: {
                                            HStack {
                                                VStack(alignment: .leading, spacing: 3) {
                                                    Text(chip.label)
                                                        .foregroundStyle(WaymarkTheme.text)
                                                    if let description = chip.description {
                                                        Text(description)
                                                            .font(.caption)
                                                            .foregroundStyle(WaymarkTheme.mutedText)
                                                    }
                                                }

                                                Spacer()

                                                if selectedTagIDs.contains(chip.tagID) {
                                                    Image(systemName: "checkmark.circle.fill")
                                                        .foregroundStyle(WaymarkTheme.positive)
                                                }
                                            }
                                            .padding(12)
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                            .background(
                                                selectedTagIDs.contains(chip.tagID) ? WaymarkTheme.route.opacity(0.16) : WaymarkTheme.panel,
                                                in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                                            )
                                            .overlay(
                                                RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                                                    .stroke(selectedTagIDs.contains(chip.tagID) ? WaymarkTheme.route.opacity(0.5) : WaymarkTheme.line, lineWidth: 1)
                                            )
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                            }
                        } else {
                            Text("Choose a primary signal before selecting context tags.")
                                .foregroundStyle(WaymarkTheme.mutedText)
                        }

                        Text("Note")
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)

                        TextField("Optional note", text: $note, axis: .vertical)
                            .lineLimit(3...8)
                            .padding(12)
                            .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
                            .overlay(
                                RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                                    .stroke(WaymarkTheme.line, lineWidth: 1)
                            )

                        Button {
                            save(evidence: evidence)
                        } label: {
                            Label("Save Review Edits", systemImage: "checkmark.circle")
                                .frame(maxWidth: .infinity)
                        }
                        .disabled(selectedReaction == nil)
                        .buttonStyle(.borderedProminent)

                        Button {
                            appModel.selectItem(evidence.item)
                        } label: {
                            Label("Set As Player Item", systemImage: "play.circle")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding(18)
                }
                .background(WaymarkTheme.background.ignoresSafeArea())
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

private struct EvidenceLine: View {
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .firstTextBaseline) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(WaymarkTheme.mutedText)

            Spacer(minLength: 16)

            Text(value)
                .font(.callout.weight(.semibold))
                .foregroundStyle(WaymarkTheme.text)
                .multilineTextAlignment(.trailing)
        }
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
