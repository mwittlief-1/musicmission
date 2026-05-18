import SwiftUI

struct NowTestingView: View {
    @EnvironmentObject private var appModel: AppModel
    @State private var selectedReaction: ReactionValue?
    @State private var selectedTagIDs = Set<String>()
    @State private var note = ""
    @State private var showsNotes = false
    @FocusState private var isNoteFieldFocused: Bool

    let openMissionReview: () -> Void
    let openResolveIssue: () -> Void

    init(
        openMissionReview: @escaping () -> Void = {},
        openResolveIssue: @escaping () -> Void = {}
    ) {
        self.openMissionReview = openMissionReview
        self.openResolveIssue = openResolveIssue
    }

    var body: some View {
        NavigationStack {
            GeometryReader { geometry in
                ScrollView(.vertical, showsIndicators: showsNotes) {
                    if let mission = appModel.mission, let item = appModel.selectedItem {
                        let resolution = appModel.resolution(for: item)
                        let playback = appModel.playback(for: item)
                        let playbackSnapshot = appModel.playbackSnapshot(for: item)
                        let savedReaction = appModel.reaction(for: item)
                        let activeReaction = savedReaction?.reactionValue ?? selectedReaction

                        VStack(spacing: 10) {
                            MissionRailBanner(
                                mission: mission,
                                progress: appModel.missionProgress,
                                openMissionReview: openMissionReview
                            )

                            if appModel.musicServiceMode == .developmentStub {
                                PlaybackNoticeBanner(
                                    title: "Stub mode",
                                    message: "Track navigation and evidence capture work here, but audio only plays in Live MusicKit.",
                                    systemImage: "wrench.and.screwdriver",
                                    actionTitle: "Use Live",
                                    action: {
                                        Task {
                                            await appModel.switchToLiveMusicKitForPlayback()
                                        }
                                    }
                                )
                            } else if let message = appModel.lastActionMessage,
                                      Self.isPlaybackBlockingMessage(message) {
                                PlaybackNoticeBanner(
                                    title: "Playback needs attention",
                                    message: message,
                                    systemImage: "exclamationmark.triangle",
                                    actionTitle: nil,
                                    action: nil
                                )
                            }

                            CompactPlayerSurface(
                                item: item,
                                resolution: resolution,
                                playback: playback,
                                playbackSnapshot: playbackSnapshot,
                                previousAction: appModel.selectPreviousItem,
                                primaryPlaybackAction: {
                                    Task {
                                        if playbackSnapshot.isPlaying {
                                            await appModel.pauseSelectedPlayback()
                                        } else if playback.status == .playing {
                                            await appModel.resumeSelectedPlayback()
                                        } else {
                                            await appModel.playSelectedItemResolvingIfNeeded()
                                        }
                                    }
                                },
                                nextAction: {
                                    Task {
                                        await appModel.playNextItem()
                                    }
                                }
                            )

                            FeedbackPanel(
                                item: item,
                                selectedReaction: activeReaction,
                                selectedTagIDs: $selectedTagIDs,
                                saveReaction: { reaction, tagIDs in
                                    saveReaction(reaction, tagIDs: tagIDs, item: item)
                                }
                            )

                            if showsNotes {
                                NotesPanel(
                                    note: $note,
                                    noteFocus: $isNoteFieldFocused,
                                    attachNote: {
                                        let reaction = activeReaction ?? .hit
                                        saveReaction(reaction, tagIDs: selectedTagIDs, item: item)
                                        isNoteFieldFocused = false
                                    }
                                )
                                .transition(.opacity.combined(with: .move(edge: .bottom)))
                            }
                        }
                        .frame(minHeight: geometry.size.height - 88, alignment: .top)
                        .padding(.horizontal, 14)
                        .padding(.top, 12)
                        .padding(.bottom, showsNotes ? 94 : 8)
                        .onAppear {
                            hydrateFeedbackState(from: savedReaction)
                        }
                        .onChange(of: appModel.selectedItemID) { _, _ in
                            hydrateFeedbackState(from: appModel.selectedItem.flatMap { appModel.reaction(for: $0) })
                        }
                    } else {
                        ContentUnavailableView(
                            "No Item Selected",
                            systemImage: "music.note.list",
                            description: Text("Choose a mission item before playback.")
                        )
                        .foregroundStyle(.white)
                        .padding()
                    }
                }
                .scrollDisabled(!showsNotes)
            }
            .background(PlayerSurfaceStyle.background.ignoresSafeArea())
            .safeAreaInset(edge: .bottom) {
                PlayerActionBar(
                    openVoiceNote: {
                        withAnimation(.snappy) {
                            showsNotes = true
                        }
                        isNoteFieldFocused = true
                    },
                    openMissionReview: openMissionReview,
                    openResolveIssue: openResolveIssue
                )
                .padding(.horizontal, 14)
                .padding(.top, 8)
                .padding(.bottom, 8)
                .background(PlayerSurfaceStyle.background)
            }
            .preferredColorScheme(.dark)
            .toolbar(.hidden, for: .navigationBar)
            .toolbar(.hidden, for: .tabBar)
            .scrollDismissesKeyboard(.interactively)
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") {
                        isNoteFieldFocused = false
                    }
                }
            }
        }
    }

    private func saveReaction(_ reaction: ReactionValue, tagIDs: Set<String>, item: MissionItem) {
        selectedReaction = reaction
        let selectedTags = item.feedbackChips(for: reaction)
            .filter { tagIDs.contains($0.tagID) }
            .map { $0.reactionTag(primaryReactionValue: reaction) }

        appModel.saveReactionForSelectedItem(
            value: reaction,
            note: note,
            selectedTags: selectedTags
        )
    }

    private func hydrateFeedbackState(from reaction: ReactionRecord?) {
        note = reaction?.notes.text ?? ""
        selectedReaction = reaction?.reactionValue
        selectedTagIDs = Set(reaction?.selectedTags?.map(\.tagID) ?? [])
        showsNotes = !(reaction?.notes.text.isEmpty ?? true)
    }

    private static func isPlaybackBlockingMessage(_ message: String) -> Bool {
        let lowercased = message.lowercased()
        return lowercased.contains("failed") ||
        lowercased.contains("authorization") ||
        lowercased.contains("requires") ||
        lowercased.contains("unresolved") ||
        lowercased.contains("ambiguous") ||
        lowercased.contains("not found")
    }
}

private enum PlayerSurfaceStyle {
    static let background = Color.black
    static let panel = Color(red: 0.075, green: 0.078, blue: 0.082)
    static let elevatedPanel = Color(red: 0.105, green: 0.108, blue: 0.114)
    static let tile = Color(red: 0.13, green: 0.135, blue: 0.142)
    static let mutedText = Color.white.opacity(0.62)
    static let faintStroke = Color.white.opacity(0.08)
}

private struct MissionRailBanner: View {
    let mission: Mission
    let progress: MissionProgress
    let openMissionReview: () -> Void

    var body: some View {
        Button(action: openMissionReview) {
            HStack(spacing: 10) {
                Image(systemName: "flag.fill")
                    .foregroundStyle(.orange)
                    .font(.subheadline.weight(.semibold))
                    .frame(width: 22)

                VStack(alignment: .leading, spacing: 2) {
                    Text(shortMissionTitle)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)
                        .lineLimit(1)

                    Text(missionSubtitle)
                        .font(.caption)
                        .foregroundStyle(PlayerSurfaceStyle.mutedText)
                        .lineLimit(1)
                }

                Spacer(minLength: 8)

                Text(progress.selectedDisplay)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.white.opacity(0.78))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .background(.white.opacity(0.08), in: Capsule())

                Image(systemName: "chevron.right")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.white.opacity(0.58))
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .frame(maxWidth: .infinity, minHeight: 58)
            .background(PlayerSurfaceStyle.elevatedPanel, in: RoundedRectangle(cornerRadius: 10))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(PlayerSurfaceStyle.faintStroke, lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }

    private var shortMissionTitle: String {
        let title = mission.missionTitle
        if title.contains(":") {
            return String(title.split(separator: ":").first ?? Substring(title))
        }
        return title
    }

    private var missionSubtitle: String {
        let title = mission.missionTitle
        if let separator = title.firstIndex(of: ":") {
            let subtitleStart = title.index(after: separator)
            return String(title[subtitleStart...]).trimmingCharacters(in: .whitespacesAndNewlines)
        }

        return mission.hypothesis
    }
}

private struct PlaybackNoticeBanner: View {
    let title: String
    let message: String
    let systemImage: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: systemImage)
                .font(.headline.weight(.semibold))
                .foregroundStyle(.orange.opacity(0.95))
                .frame(width: 32, height: 32)
                .background(.orange.opacity(0.14), in: Circle())

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)

                Text(message)
                    .font(.caption)
                    .foregroundStyle(PlayerSurfaceStyle.mutedText)
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 8)

            if let actionTitle, let action {
                Button(action: action) {
                    Text(actionTitle)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(.black)
                        .padding(.horizontal, 11)
                        .padding(.vertical, 8)
                        .background(.white, in: Capsule())
                }
                .buttonStyle(.plain)
            }
        }
        .padding(12)
        .background(PlayerSurfaceStyle.panel, in: RoundedRectangle(cornerRadius: 10))
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(.orange.opacity(0.22), lineWidth: 1)
        )
    }
}

private struct CompactPlayerSurface: View {
    let item: MissionItem
    let resolution: AppleMusicResolution
    let playback: PlaybackRecord
    let playbackSnapshot: PlaybackSnapshot
    let previousAction: () -> Void
    let primaryPlaybackAction: () -> Void
    let nextAction: () -> Void

    var body: some View {
        HStack(alignment: .center, spacing: 16) {
            ArtworkFlipCard(item: item, resolution: resolution)
                .id(item.itemID)

            VStack(alignment: .leading, spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(resolution.resolvedTitle ?? item.title)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(.white)
                        .lineLimit(3)
                        .minimumScaleFactor(0.78)

                    Text(resolution.resolvedArtist ?? item.artist)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(PlayerSurfaceStyle.mutedText)
                        .lineLimit(1)

                    if let album = resolution.resolvedAlbum ?? item.album {
                        Text(album)
                            .font(.caption)
                            .foregroundStyle(.white.opacity(0.42))
                            .lineLimit(1)
                    }
                }

                PlaybackMeter(playback: playback, snapshot: playbackSnapshot)

                HStack(spacing: 18) {
                    TransportButton(systemImage: "backward.fill", size: 36, action: previousAction)

                    Button(action: primaryPlaybackAction) {
                        Image(systemName: playbackSnapshot.isPlaying ? "pause.fill" : "play.fill")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundStyle(.black)
                            .frame(width: 58, height: 58)
                            .background(Circle().fill(Color.white))
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel(playbackSnapshot.isPlaying ? "Pause" : "Play")

                    TransportButton(systemImage: "forward.fill", size: 36, action: nextAction)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.horizontal, 10)
        .padding(.top, 18)
        .padding(.bottom, 14)
        .frame(maxWidth: .infinity)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.035), Color.white.opacity(0.015)],
                startPoint: .top,
                endPoint: .bottom
            ),
            in: RoundedRectangle(cornerRadius: 10)
        )
    }
}

private struct PlaybackMeter: View {
    let playback: PlaybackRecord
    let snapshot: PlaybackSnapshot

    var body: some View {
        VStack(spacing: 4) {
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(Color.white.opacity(0.18))
                        .frame(height: 4)

                    Capsule()
                        .fill(Color.white.opacity(0.88))
                        .frame(width: geometry.size.width * progress, height: 4)

                    Circle()
                        .fill(Color.white)
                        .frame(width: 8, height: 8)
                        .offset(x: max(0, geometry.size.width * progress - 4))
                }
            }
            .frame(height: 8)

            HStack {
                Text(leftTime)
                Spacer()
                Text(rightTime)
            }
            .font(.caption2.monospacedDigit())
            .foregroundStyle(PlayerSurfaceStyle.mutedText)
        }
    }

    private var progress: Double {
        max(snapshot.progress, playback.status == .notAttempted ? 0 : 0.04)
    }

    private var leftTime: String {
        if snapshot.elapsedSeconds > 0 {
            return format(snapshot.elapsedSeconds)
        }

        if playback.status == .played || playback.status == .skipped,
           let durationSeconds = playback.durationSeconds {
            return format(durationSeconds)
        }

        return "0:00"
    }

    private var rightTime: String {
        if let remainingSeconds = snapshot.remainingSeconds {
            return "-\(format(remainingSeconds))"
        }

        if playback.status == .played {
            return "-0:00"
        }

        return "-:--"
    }

    private func format(_ seconds: TimeInterval) -> String {
        let totalSeconds = max(0, Int(seconds.rounded()))
        return "\(totalSeconds / 60):\(String(format: "%02d", totalSeconds % 60))"
    }
}

private struct ArtworkFlipCard: View {
    let item: MissionItem
    let resolution: AppleMusicResolution
    @State private var showsMissionSide = false

    var body: some View {
        Button {
            guard item.playerCard?.flipSide != nil else {
                return
            }

            withAnimation(.spring(response: 0.34, dampingFraction: 0.82)) {
                showsMissionSide.toggle()
            }
        } label: {
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(PlayerSurfaceStyle.tile)

                if showsMissionSide, let flipSide = item.playerCard?.flipSide {
                    hypothesisSide(flipSide)
                } else {
                    artworkSide
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .overlay(alignment: .topLeading) {
                Text(String(format: "%02d", item.sequence))
                    .font(.caption.weight(.bold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .foregroundStyle(.white)
                    .background(.black.opacity(0.34), in: RoundedRectangle(cornerRadius: 7))
                    .padding(9)
            }
            .overlay(alignment: .bottomTrailing) {
                if item.playerCard?.flipSide != nil {
                    Image(systemName: "arrow.trianglehead.2.clockwise.rotate.90")
                        .font(.caption.weight(.bold))
                        .padding(8)
                        .foregroundStyle(.white)
                        .background(.black.opacity(0.34), in: Circle())
                        .padding(8)
                }
            }
        }
        .buttonStyle(.plain)
        .frame(width: 164, height: 164)
    }

    @ViewBuilder
    private var artworkSide: some View {
        if let artworkURL = resolution.artworkURL {
            AsyncImage(url: artworkURL) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFill()
                default:
                    fallbackArtwork
                }
            }
        } else {
            fallbackArtwork
        }
    }

    private var fallbackArtwork: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.10, green: 0.13, blue: 0.18),
                    Color(red: 0.27, green: 0.34, blue: 0.86),
                    Color(red: 0.18, green: 0.60, blue: 0.40)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            VStack(spacing: 10) {
                Image(systemName: "music.note")
                    .font(.system(size: 42, weight: .semibold))
                Text(item.artist)
                    .font(.headline)
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)
            }
            .foregroundStyle(.white)
            .padding()
        }
    }

    private func hypothesisSide(_ flipSide: MissionPlayerCardFlipSide) -> some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.05, green: 0.07, blue: 0.08),
                    Color(red: 0.14, green: 0.22, blue: 0.18),
                    Color(red: 0.18, green: 0.08, blue: 0.14)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            VStack(alignment: .leading, spacing: 8) {
                Text("Hypothesis")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.white.opacity(0.68))
                    .textCase(.uppercase)

                Text(flipSide.songHypothesis ?? item.expectedTestSignal ?? item.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                    .lineLimit(5)
                    .fixedSize(horizontal: false, vertical: true)

                if let detail = flipSide.detail {
                    Text(detail)
                        .font(.caption2)
                        .foregroundStyle(.white.opacity(0.74))
                        .lineLimit(5)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer(minLength: 0)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
        }
    }
}

private struct TransportButton: View {
    let systemImage: String
    let size: CGFloat
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Image(systemName: systemImage)
                .font(.system(size: 19, weight: .semibold))
                .foregroundStyle(.white)
                .frame(width: size, height: size)
        }
        .buttonStyle(.plain)
    }
}

private struct FeedbackPanel: View {
    let item: MissionItem
    let selectedReaction: ReactionValue?
    @Binding var selectedTagIDs: Set<String>
    let saveReaction: (ReactionValue, Set<String>) -> Void

    var body: some View {
        VStack(spacing: 0) {
            ReactionTileRow(
                item: item,
                selectedReaction: selectedReaction,
                selectReaction: { reaction in
                    if selectedReaction != reaction {
                        selectedTagIDs.removeAll()
                    }
                    saveReaction(reaction, selectedTagIDs)
                }
            )

            Divider()
                .overlay(Color.white.opacity(0.06))
                .padding(.top, 10)

            ContextChipRail(
                item: item,
                selectedReaction: selectedReaction,
                selectedTagIDs: $selectedTagIDs,
                toggleChip: { chip in
                    guard let selectedReaction else {
                        return
                    }

                    if selectedTagIDs.contains(chip.tagID) {
                        selectedTagIDs.remove(chip.tagID)
                    } else {
                        selectedTagIDs.insert(chip.tagID)
                    }

                    saveReaction(selectedReaction, selectedTagIDs)
                }
            )
        }
        .padding(.top, 12)
        .padding(.bottom, 10)
        .background(PlayerSurfaceStyle.panel, in: RoundedRectangle(cornerRadius: 10))
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(PlayerSurfaceStyle.faintStroke, lineWidth: 1)
        )
    }
}

private struct ReactionTileRow: View {
    let item: MissionItem
    let selectedReaction: ReactionValue?
    let selectReaction: (ReactionValue) -> Void

    var body: some View {
        HStack(spacing: 8) {
            ForEach(FeedbackCardSpec.cards(for: item)) { card in
                ReactionTile(
                    card: card,
                    isSelected: selectedReaction == card.reaction,
                    action: {
                        selectReaction(card.reaction)
                    }
                )
            }
        }
        .padding(.horizontal, 10)
    }
}

private struct ReactionTile: View {
    let card: FeedbackCardSpec
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 9) {
                Image(systemName: card.systemImage)
                    .font(.system(size: 23, weight: .semibold))
                    .foregroundStyle(isSelected ? .white : card.tint.opacity(0.92))

                Text(card.title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.92))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity, minHeight: 78)
            .background(
                LinearGradient(
                    colors: [
                        card.tint.opacity(isSelected ? 0.68 : 0.36),
                        card.tint.opacity(isSelected ? 0.42 : 0.22)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ),
                in: RoundedRectangle(cornerRadius: 8)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? card.tint.opacity(0.95) : .white.opacity(0.06), lineWidth: isSelected ? 1.5 : 1)
            )
        }
        .buttonStyle(.plain)
    }
}

private struct ContextChipRail: View {
    let item: MissionItem
    let selectedReaction: ReactionValue?
    @Binding var selectedTagIDs: Set<String>
    let toggleChip: (FeedbackChipOption) -> Void

    var body: some View {
        VStack(spacing: 8) {
            if let selectedReaction {
                let chips = Array(item.feedbackChips(for: selectedReaction).prefix(6))
                if chips.isEmpty {
                    EmptyChipState(text: "No secondary signals for this reaction yet.")
                } else {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(chips) { chip in
                                ContextChipTile(
                                    chip: chip,
                                    tint: FeedbackCardSpec.tint(for: selectedReaction),
                                    isSelected: selectedTagIDs.contains(chip.tagID),
                                    action: {
                                        toggleChip(chip)
                                    }
                                )
                            }
                        }
                        .padding(.horizontal, 10)
                        .padding(.top, 10)
                        .padding(.bottom, 2)
                    }

                    if chips.count > 3 {
                        HStack(spacing: 5) {
                            Circle()
                                .fill(.white.opacity(0.86))
                                .frame(width: 6, height: 6)
                            Circle()
                                .fill(.white.opacity(0.28))
                                .frame(width: 6, height: 6)
                        }
                        .padding(.top, 2)
                    }
                }
            } else {
                EmptyChipState(text: "Choose a primary signal to open the matching signal rail.")
                    .padding(.top, 10)
            }
        }
        .frame(minHeight: 138)
    }
}

private struct ContextChipTile: View {
    let chip: FeedbackChipOption
    let tint: Color
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 10) {
                ZStack(alignment: .topTrailing) {
                    Image(systemName: iconName)
                        .font(.system(size: 30, weight: .medium))
                        .foregroundStyle(isSelected ? tint : .white.opacity(0.82))
                        .frame(maxWidth: .infinity)

                    if isSelected {
                        Circle()
                            .fill(tint)
                            .frame(width: 8, height: 8)
                            .offset(x: 8, y: -5)
                    }
                }

                Text(chip.label)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.78)
            }
            .padding(.horizontal, 10)
            .frame(width: 110, height: 124)
            .background(PlayerSurfaceStyle.tile, in: RoundedRectangle(cornerRadius: 9))
            .overlay(
                RoundedRectangle(cornerRadius: 9)
                    .stroke(isSelected ? tint : .white.opacity(0.07), lineWidth: isSelected ? 1.6 : 1)
            )
        }
        .buttonStyle(.plain)
    }

    private var iconName: String {
        let key = (chip.tagID + " " + chip.label).lowercased()

        if key.contains("bite") || key.contains("pressure") {
            return "flame"
        }
        if key.contains("soft") || key.contains("gentle") {
            return "cloud"
        }
        if key.contains("wrong") || key.contains("version") {
            return "shuffle"
        }
        if key.contains("resolve") || key.contains("ambiguous") {
            return "questionmark.diamond"
        }
        if key.contains("dark") || key.contains("ache") {
            return "moon.stars"
        }
        if key.contains("body") || key.contains("dance") {
            return "waveform"
        }
        if key.contains("voice") {
            return "waveform.and.mic"
        }
        if key.contains("album") || key.contains("world") {
            return "record.circle"
        }
        if key.contains("novelty") || key.contains("slop") {
            return "xmark"
        }

        return "sparkle"
    }
}

private struct EmptyChipState: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.caption)
            .foregroundStyle(PlayerSurfaceStyle.mutedText)
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity, minHeight: 92)
            .padding(.horizontal, 22)
    }
}

private struct NotesPanel: View {
    @Binding var note: String
    let noteFocus: FocusState<Bool>.Binding
    let attachNote: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            TextField("Optional note", text: $note, axis: .vertical)
                .lineLimit(2...4)
                .focused(noteFocus)
                .padding(12)
                .background(PlayerSurfaceStyle.tile, in: RoundedRectangle(cornerRadius: 10))
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(PlayerSurfaceStyle.faintStroke, lineWidth: 1)
                )

            Button(action: attachNote) {
                Label("Attach Note", systemImage: "checkmark")
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(12)
        .background(PlayerSurfaceStyle.panel, in: RoundedRectangle(cornerRadius: 10))
    }
}

private struct PlayerActionBar: View {
    let openVoiceNote: () -> Void
    let openMissionReview: () -> Void
    let openResolveIssue: () -> Void

    var body: some View {
        HStack(spacing: 10) {
            Button(action: openVoiceNote) {
                Image(systemName: "mic")
                    .font(.headline.weight(.semibold))
                    .frame(width: 48, height: 48)
                    .background(PlayerSurfaceStyle.elevatedPanel, in: RoundedRectangle(cornerRadius: 10))
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Add voice note")

            Button(action: openMissionReview) {
                Label("Mission Review", systemImage: "list.clipboard")
                    .font(.subheadline.weight(.semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.84)
                    .frame(maxWidth: .infinity, minHeight: 48)
                    .background(PlayerSurfaceStyle.elevatedPanel, in: RoundedRectangle(cornerRadius: 10))
            }
            .buttonStyle(.plain)

            Button(action: openResolveIssue) {
                Label("Resolve Issue", systemImage: "exclamationmark.triangle")
                    .font(.subheadline.weight(.semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.84)
                    .foregroundStyle(.orange.opacity(0.95))
                    .frame(maxWidth: .infinity, minHeight: 48)
                    .background(PlayerSurfaceStyle.elevatedPanel, in: RoundedRectangle(cornerRadius: 10))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(.orange.opacity(0.28), lineWidth: 1)
                    )
            }
            .buttonStyle(.plain)
        }
    }
}

private struct FeedbackCardSpec: Identifiable {
    let reaction: ReactionValue
    let title: String
    let systemImage: String
    let tint: Color

    var id: ReactionValue {
        reaction
    }

    static func cards(for item: MissionItem) -> [FeedbackCardSpec] {
        ReactionValue.primarySignalValues.map { reaction in
            FeedbackCardSpec(
                reaction: reaction,
                title: ReactionDisplayConfiguration.current.label(for: reaction),
                systemImage: systemImage(for: reaction),
                tint: tint(for: reaction)
            )
        }
    }

    static func systemImage(for reaction: ReactionValue) -> String {
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

    static func tint(for reaction: ReactionValue) -> Color {
        switch reaction {
        case .hit:
            return Color(red: 0.38, green: 0.74, blue: 0.34)
        case .partial:
            return Color(red: 0.86, green: 0.68, blue: 0.24)
        case .okShelf:
            return Color(red: 0.95, green: 0.47, blue: 0.22)
        case .miss, .slop, .skipped, .unresolved:
            return Color(red: 0.86, green: 0.27, blue: 0.27)
        }
    }
}
