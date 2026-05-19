import SwiftUI

struct SurveyView: View {
    @EnvironmentObject private var appModel: AppModel
    @StateObject private var surveyStore = SurveyStore()
    @State private var nuanceItem: SurveyItem?
    @State private var freeformDraft = ""

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 9), count: 3)

    var body: some View {
        NavigationStack {
            ZStack {
                SurveyStyle.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    SurveyHeader(
                        step: surveyStore.currentStep,
                        signalCount: surveyStore.makeSummary().visibleSignalCount,
                        canMoveBackward: surveyStore.canMoveBackward,
                        moveBack: surveyStore.goBack
                    )

                    Group {
                        switch surveyStore.currentStep {
                        case .welcome:
                            welcomeView
                        case .connectAppleMusic:
                            connectView
                        case .artistPage1, .artistPage2, .artistPage3, .albumPage1, .songPage1:
                            gridView
                        case .artistPage3Prompt:
                            artistPage3PromptView
                        case .deeperPrompt:
                            deeperPromptView
                        case .advancedSurvey:
                            advancedSurveyView
                        case .readout:
                            readoutView
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .navigationTitle("Survey")
            .navigationBarTitleDisplayMode(.inline)
            .preferredColorScheme(.dark)
            .sheet(item: $nuanceItem) { item in
                SurveyNuanceSheet(item: item, store: surveyStore)
                    .presentationDetents([.medium, .large])
                    .presentationDragIndicator(.visible)
            }
        }
    }

    private var welcomeView: some View {
        VStack(alignment: .leading, spacing: 18) {
            Spacer(minLength: 24)

            Image(systemName: "point.topleft.down.curvedto.point.bottomright.up")
                .font(.system(size: 44, weight: .semibold))
                .foregroundStyle(.blue)

            VStack(alignment: .leading, spacing: 10) {
                Text("Tune the starting map")
                    .font(.largeTitle.weight(.bold))
                    .foregroundStyle(.white)

                Text("Waymark will start with a quick Apple Music-seeded pass, then ask whether you want to go deeper.")
                    .font(.body)
                    .foregroundStyle(SurveyStyle.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            VStack(alignment: .leading, spacing: 12) {
                SurveyWelcomeRow(systemImage: "person.2.crop.square.stack", title: "Artists first", detail: "The strongest first read of known territory.")
                SurveyWelcomeRow(systemImage: "square.stack.3d.up", title: "Albums and songs next", detail: "Object-specific checks catch exceptions and false inferences.")
                SurveyWelcomeRow(systemImage: "slider.horizontal.3", title: "Advanced is optional", detail: "Filters and freeform notes stay available after the simple pass.")
            }
            .padding(.top, 8)

            Spacer()

            Button {
                surveyStore.advance()
            } label: {
                Label("Start Survey", systemImage: "arrow.right")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding(20)
    }

    private var connectView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Connect Apple Music")
                        .font(.title2.weight(.bold))
                        .foregroundStyle(.white)

                    Text("This first build uses seeded fixtures for the grid, but the flow is shaped around Apple Music becoming the primary source for Page 1.")
                        .font(.callout)
                        .foregroundStyle(SurveyStyle.secondaryText)
                        .fixedSize(horizontal: false, vertical: true)
                }

                VStack(alignment: .leading, spacing: 12) {
                    MusicAuthorizationPanel(service: appModel.musicAuthorization)
                }
                .padding(14)
                .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 12))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(SurveyStyle.stroke, lineWidth: 1)
                )

                Button {
                    surveyStore.advance()
                } label: {
                    Label("Continue to Artist Grid", systemImage: "square.grid.3x3")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }
            .padding(20)
        }
    }

    private var gridView: some View {
        VStack(spacing: 0) {
            if let page = surveyStore.currentPage {
                SurveyGridPageSurface(
                    page: page,
                    columns: columns,
                    stateForItem: { surveyStore.state(for: $0) },
                    nuanceCountForItem: { surveyStore.nuances(for: $0).count },
                    hasNoteForItem: { !surveyStore.note(for: $0).isEmpty },
                    tapItem: { surveyStore.cycleState(for: $0) },
                    longPressItem: { nuanceItem = $0 }
                )

                SurveyBottomBar(
                    leadingTitle: "Back",
                    leadingSystemImage: "chevron.left",
                    leadingAction: surveyStore.goBack,
                    trailingTitle: nextButtonTitle(for: page),
                    trailingSystemImage: "arrow.right",
                    trailingAction: surveyStore.advance
                )
            } else {
                ContentUnavailableView("Survey Page Missing", systemImage: "questionmark.app")
                    .foregroundStyle(.white)
            }
        }
    }

    private var artistPage3PromptView: some View {
        VStack(alignment: .leading, spacing: 18) {
            Spacer()

            Image(systemName: surveyStore.shouldSuggestArtistPage3 ? "scope" : "checkmark.circle")
                .font(.system(size: 42, weight: .semibold))
                .foregroundStyle(surveyStore.shouldSuggestArtistPage3 ? .orange : .green)

            Text("One more artist pass?")
                .font(.title.weight(.bold))
                .foregroundStyle(.white)

            Text(surveyStore.shouldSuggestArtistPage3 ? "The early artist answers have enough tension that another page should help avoid obvious bad guesses." : "We have enough to continue, but a third artist page can sharpen the starting map.")
                .font(.body)
                .foregroundStyle(SurveyStyle.secondaryText)
                .fixedSize(horizontal: false, vertical: true)

            Spacer()

            Button {
                surveyStore.goTo(.artistPage3)
            } label: {
                Label("Do One More Artist Page", systemImage: "square.grid.3x3")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Button {
                surveyStore.goTo(.albumPage1)
            } label: {
                Label("Continue to Albums", systemImage: "rectangle.stack")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
        }
        .padding(20)
    }

    private var deeperPromptView: some View {
        VStack(alignment: .leading, spacing: 18) {
            Spacer()

            Image(systemName: "map")
                .font(.system(size: 42, weight: .semibold))
                .foregroundStyle(.blue)

            Text("Want to tune the map more?")
                .font(.title.weight(.bold))
                .foregroundStyle(.white)

            Text("There is enough here for a starting read. Advanced Survey keeps the same grid, but lets you steer by era, genre, country, scene, popularity, dead ends, sleepers, or your own notes.")
                .font(.body)
                .foregroundStyle(SurveyStyle.secondaryText)
                .fixedSize(horizontal: false, vertical: true)

            SurveySignalCountPill(count: surveyStore.makeSummary().visibleSignalCount)

            Spacer()

            Button {
                surveyStore.goTo(.readout)
            } label: {
                Label("Show What We Think So Far", systemImage: "sparkles")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Button {
                surveyStore.goTo(.advancedSurvey)
            } label: {
                Label("Go Deeper", systemImage: "slider.horizontal.3")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
        }
        .padding(20)
    }

    private var advancedSurveyView: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Advanced Survey")
                            .font(.title2.weight(.bold))
                            .foregroundStyle(.white)

                        Text("Pick a lens, then use the same grid rhythm. Freeform notes are captured as user-asserted evidence for later review.")
                            .font(.callout)
                            .foregroundStyle(SurveyStyle.secondaryText)
                    }

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(SurveyAdvancedFilter.allCases) { filter in
                                Button {
                                    surveyStore.setAdvancedFilter(filter)
                                } label: {
                                    Text(filter.label)
                                        .font(.caption.weight(.semibold))
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 8)
                                        .foregroundStyle(surveyStore.advancedFilter == filter ? .black : .white)
                                        .background(surveyStore.advancedFilter == filter ? Color.white : SurveyStyle.panel, in: Capsule())
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }

                    if let page = surveyStore.currentPage {
                        LazyVGrid(columns: columns, spacing: 9) {
                            ForEach(page.items) { item in
                                SurveyGridTile(
                                    item: item,
                                    state: surveyStore.state(for: item),
                                    nuanceCount: surveyStore.nuances(for: item).count,
                                    hasNote: !surveyStore.note(for: item).isEmpty,
                                    tileHeight: 132,
                                    tap: {
                                        surveyStore.cycleState(for: item)
                                    },
                                    longPress: {
                                        nuanceItem = item
                                    }
                                )
                            }
                        }
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        Label("Anything Waymark should know?", systemImage: "text.quote")
                            .font(.headline)
                            .foregroundStyle(.white)

                        TextEditor(text: $freeformDraft)
                            .frame(minHeight: 92)
                            .scrollContentBackground(.hidden)
                            .padding(8)
                            .background(SurveyStyle.elevatedPanel, in: RoundedRectangle(cornerRadius: 10))
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(SurveyStyle.stroke, lineWidth: 1)
                            )

                        Button {
                            surveyStore.addFreeformSignal(freeformDraft)
                            freeformDraft = ""
                        } label: {
                            Label("Add Note", systemImage: "plus.circle")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .disabled(freeformDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    }
                    .padding(14)
                    .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 12))
                }
                .padding(.horizontal, 14)
                .padding(.top, 12)
                .padding(.bottom, 92)
            }

            SurveyBottomBar(
                leadingTitle: "Back",
                leadingSystemImage: "chevron.left",
                leadingAction: surveyStore.goBack,
                trailingTitle: "Readout",
                trailingSystemImage: "sparkles",
                trailingAction: surveyStore.advance
            )
        }
    }

    private var readoutView: some View {
        let summary = surveyStore.makeSummary()

        return ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("What We Think So Far")
                        .font(.title.weight(.bold))
                        .foregroundStyle(.white)

                    Text("This is a starting read from Survey evidence, not a verdict.")
                        .font(.callout)
                        .foregroundStyle(SurveyStyle.secondaryText)
                }

                HStack(spacing: 10) {
                    SurveyStatCard(value: "\(summary.visibleSignalCount)", label: "Signals")
                    SurveyStatCard(value: "\(summary.favorites.count + summary.likes.count)", label: "Positive")
                    SurveyStatCard(value: "\(summary.notForMe.count)", label: "No")
                }

                SurveyReadoutSection(title: "Strongest territory", items: summary.favorites + summary.likes)
                SurveyReadoutSection(title: "Useful waypoints", items: summary.fine)
                SurveyReadoutSection(title: "Likely dead ends", items: summary.notForMe)

                if !summary.freeformSignals.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("User-asserted notes")
                            .font(.headline)
                            .foregroundStyle(.white)

                        ForEach(summary.freeformSignals) { signal in
                            Text(signal.text)
                                .font(.callout)
                                .foregroundStyle(.white.opacity(0.88))
                                .padding(12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 10))
                        }
                    }
                }

                Button {
                    surveyStore.goTo(.advancedSurvey)
                } label: {
                    Label("Add Advanced Signals", systemImage: "slider.horizontal.3")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
            }
            .padding(20)
        }
    }

    private func nextButtonTitle(for page: SurveyGridPage) -> String {
        switch page.kind {
        case .artist where page.pageIndex == 1:
            return "Artist Grid 2"
        case .artist:
            return "Continue"
        case .album:
            return "Song Grid"
        case .song:
            return "Readout"
        }
    }
}

private enum SurveyStyle {
    static let background = Color.black
    static let panel = Color(red: 0.09, green: 0.095, blue: 0.102)
    static let elevatedPanel = Color(red: 0.13, green: 0.135, blue: 0.145)
    static let stroke = Color.white.opacity(0.08)
    static let secondaryText = Color.white.opacity(0.66)
}

private struct SurveyHeader: View {
    let step: SurveyStep
    let signalCount: Int
    let canMoveBackward: Bool
    let moveBack: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(action: moveBack) {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.bold))
                    .frame(width: 34, height: 34)
                    .background(SurveyStyle.panel, in: Circle())
            }
            .buttonStyle(.plain)
            .foregroundStyle(.white)
            .opacity(canMoveBackward ? 1 : 0)
            .disabled(!canMoveBackward)

            VStack(alignment: .leading, spacing: 2) {
                Text(step.headerTitle)
                    .font(.headline)
                    .foregroundStyle(.white)
                    .lineLimit(1)

                Text(step.headerSubtitle)
                    .font(.caption)
                    .foregroundStyle(SurveyStyle.secondaryText)
                    .lineLimit(1)
            }

            Spacer()

            SurveySignalCountPill(count: signalCount)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.black.opacity(0.92))
    }
}

private struct SurveySignalCountPill: View {
    let count: Int

    var body: some View {
        Label("\(count)", systemImage: "waveform.path.ecg")
            .font(.caption.weight(.semibold))
            .foregroundStyle(.white.opacity(0.82))
            .padding(.horizontal, 10)
            .padding(.vertical, 7)
            .background(SurveyStyle.panel, in: Capsule())
    }
}

private struct SurveyPageTitle: View {
    let page: SurveyGridPage

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(page.title)
                .font(.title3.weight(.bold))
                .foregroundStyle(.white)
                .lineLimit(1)

            Text(page.subtitle)
                .font(.caption)
                .foregroundStyle(SurveyStyle.secondaryText)
                .lineLimit(1)
        }
    }
}

private struct SurveyGridPageSurface: View {
    let page: SurveyGridPage
    let columns: [GridItem]
    let stateForItem: (SurveyItem) -> SurveySignalState
    let nuanceCountForItem: (SurveyItem) -> Int
    let hasNoteForItem: (SurveyItem) -> Bool
    let tapItem: (SurveyItem) -> Void
    let longPressItem: (SurveyItem) -> Void

    var body: some View {
        GeometryReader { proxy in
            let gridSpacing: CGFloat = 9
            let verticalPadding: CGFloat = 10
            let titleHeight: CGFloat = 42
            let availableHeight = proxy.size.height - (verticalPadding * 2) - titleHeight - 10
            let rawTileHeight = (availableHeight - (gridSpacing * 3)) / 4
            let tileHeight = min(max(rawTileHeight, 92), 138)

            VStack(alignment: .leading, spacing: 10) {
                SurveyPageTitle(page: page)
                    .frame(height: titleHeight, alignment: .topLeading)

                LazyVGrid(columns: columns, spacing: gridSpacing) {
                    ForEach(page.items) { item in
                        SurveyGridTile(
                            item: item,
                            state: stateForItem(item),
                            nuanceCount: nuanceCountForItem(item),
                            hasNote: hasNoteForItem(item),
                            tileHeight: tileHeight,
                            tap: {
                                tapItem(item)
                            },
                            longPress: {
                                longPressItem(item)
                            }
                        )
                    }
                }

                Spacer(minLength: 0)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, verticalPadding)
            .frame(width: proxy.size.width, height: proxy.size.height, alignment: .top)
        }
    }
}

private struct SurveyGridTile: View {
    let item: SurveyItem
    let state: SurveySignalState
    let nuanceCount: Int
    let hasNote: Bool
    let tileHeight: CGFloat
    let tap: () -> Void
    let longPress: () -> Void

    var body: some View {
        Button(action: tap) {
            VStack(spacing: 6) {
                ZStack(alignment: .topTrailing) {
                    SurveyArtworkView(item: item, gradient: tileGradient, initials: initials)
                        .frame(height: artworkHeight)

                    HStack(spacing: 4) {
                        if nuanceCount > 0 || hasNote {
                            Image(systemName: hasNote ? "text.bubble.fill" : "tag.fill")
                                .font(.caption2.weight(.bold))
                                .foregroundStyle(.white)
                                .frame(width: 21, height: 21)
                                .background(.black.opacity(0.52), in: Circle())
                        }

                        if let systemImage = state.systemImage {
                            Image(systemName: systemImage)
                                .font(.caption2.weight(.black))
                                .foregroundStyle(state.foregroundColor)
                                .frame(width: 21, height: 21)
                                .background(.black.opacity(0.58), in: Circle())
                        }
                    }
                    .padding(5)
                }

                VStack(spacing: 1) {
                    Text(item.title)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.white)
                        .lineLimit(item.subtitle == nil ? 2 : 1)
                        .multilineTextAlignment(.center)
                        .minimumScaleFactor(0.72)

                    if let subtitle = item.subtitle {
                        Text(subtitle)
                            .font(.caption2)
                            .foregroundStyle(SurveyStyle.secondaryText)
                            .lineLimit(1)
                            .minimumScaleFactor(0.72)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            }
            .padding(6)
            .frame(maxWidth: .infinity, minHeight: tileHeight, maxHeight: tileHeight, alignment: .top)
            .background(state.surfaceColor, in: RoundedRectangle(cornerRadius: 10))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(state.tintColor.opacity(state == .dontKnow ? 0.16 : 0.78), lineWidth: state == .dontKnow ? 1 : 1.6)
            )
            .contentShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(.plain)
        .simultaneousGesture(
            LongPressGesture(minimumDuration: 0.45)
                .onEnded { _ in
                    longPress()
                }
        )
        .accessibilityLabel("\(item.title), \(state.displayName)")
    }

    private var artworkHeight: CGFloat {
        max(44, tileHeight * (item.kind == .artist ? 0.48 : 0.52))
    }

    private var initials: String {
        item.title
            .split(separator: " ")
            .prefix(2)
            .compactMap(\.first)
            .map(String.init)
            .joined()
            .uppercased()
    }

    private var tileGradient: LinearGradient {
        let colors: [Color]
        switch item.source {
        case .appleMusicDerived:
            colors = [.blue, .purple]
        case .broadCalibration:
            colors = [.teal, .blue]
        case .responseAdjacent:
            colors = [.green, .blue]
        case .sleeperProbe:
            colors = [.orange, .pink]
        case .rejectionProbe:
            colors = [.red, .orange]
        case .appleMusicLooseEnd:
            colors = [.indigo, .cyan]
        case .objectSpecific:
            colors = [.mint, .indigo]
        case .advancedFilter:
            colors = [.gray, .blue]
        }

        return LinearGradient(colors: colors, startPoint: .topLeading, endPoint: .bottomTrailing)
    }
}

private struct SurveyArtworkView: View {
    let item: SurveyItem
    let gradient: LinearGradient
    let initials: String

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 8)
                .fill(gradient)

            if let artworkURL {
                AsyncImage(url: artworkURL) { phase in
                    switch phase {
                    case .empty:
                        placeholder
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure:
                        placeholder
                    @unknown default:
                        placeholder
                    }
                }
            } else {
                placeholder
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private var artworkURL: URL? {
        guard let url = item.artworkURL,
              let scheme = url.scheme?.lowercased(),
              scheme == "http" || scheme == "https" else {
            return nil
        }
        return url
    }

    @ViewBuilder
    private var placeholder: some View {
        if item.kind == .artist {
            Text(initials)
                .font(.title3.weight(.bold))
                .foregroundStyle(.white)
        } else {
            Image(systemName: item.kind == .album ? "square.stack.fill" : "music.note")
                .font(.title3.weight(.bold))
                .foregroundStyle(.white)
        }
    }
}

private struct SurveyBottomBar: View {
    let leadingTitle: String
    let leadingSystemImage: String
    let leadingAction: () -> Void
    let trailingTitle: String
    let trailingSystemImage: String
    let trailingAction: () -> Void

    var body: some View {
        HStack(spacing: 10) {
            Button(action: leadingAction) {
                Label(leadingTitle, systemImage: leadingSystemImage)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)

            Button(action: trailingAction) {
                Label(trailingTitle, systemImage: trailingSystemImage)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
        }
        .controlSize(.large)
        .padding(.horizontal, 14)
        .padding(.top, 10)
        .padding(.bottom, 12)
        .background(SurveyStyle.background)
    }
}

private struct SurveyNuanceSheet: View {
    let item: SurveyItem
    @ObservedObject var store: SurveyStore
    @Environment(\.dismiss) private var dismiss
    @State private var draftNote = ""

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(item.title)
                            .font(.title2.weight(.bold))
                        if let subtitle = item.subtitle {
                            Text(subtitle)
                                .foregroundStyle(.secondary)
                        }
                    }

                    Picker("Signal", selection: Binding(
                        get: { store.state(for: item) },
                        set: { store.setState($0, for: item) }
                    )) {
                        ForEach(SurveySignalState.allCases) { state in
                            Text(state.displayName).tag(state)
                        }
                    }
                    .pickerStyle(.segmented)

                    VStack(alignment: .leading, spacing: 8) {
                        Text("More specific")
                            .font(.headline)

                        ForEach(SurveyNuance.allCases) { nuance in
                            Button {
                                store.toggleNuance(nuance, for: item)
                            } label: {
                                HStack {
                                    Text(nuance.label)
                                    Spacer()
                                    if store.nuances(for: item).contains(nuance) {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(.blue)
                                    }
                                }
                                .padding(.vertical, 6)
                            }
                            .buttonStyle(.plain)
                        }
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Note")
                            .font(.headline)

                        TextEditor(text: $draftNote)
                            .frame(minHeight: 92)
                            .padding(8)
                            .background(Color(uiColor: .secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))
                    }
                }
                .padding(18)
            }
            .navigationTitle("Survey Detail")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        store.updateNote(draftNote, for: item)
                        dismiss()
                    }
                }
            }
            .onAppear {
                draftNote = store.note(for: item)
            }
        }
    }
}

private struct SurveyWelcomeRow: View {
    let systemImage: String
    let title: String
    let detail: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: systemImage)
                .font(.headline)
                .foregroundStyle(.blue)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.white)
                Text(detail)
                    .font(.callout)
                    .foregroundStyle(SurveyStyle.secondaryText)
            }
        }
    }
}

private struct SurveyStatCard: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title2.weight(.bold))
                .foregroundStyle(.white)
            Text(label)
                .font(.caption)
                .foregroundStyle(SurveyStyle.secondaryText)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 14)
        .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 12))
    }
}

private struct SurveyReadoutSection: View {
    let title: String
    let items: [SurveyItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.headline)
                .foregroundStyle(.white)

            if items.isEmpty {
                Text("No signals yet.")
                    .font(.callout)
                    .foregroundStyle(SurveyStyle.secondaryText)
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 10))
            } else {
                ForEach(items.prefix(8)) { item in
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(item.title)
                                .font(.callout.weight(.semibold))
                                .foregroundStyle(.white)
                            Text(item.rationale)
                                .font(.caption)
                                .foregroundStyle(SurveyStyle.secondaryText)
                                .lineLimit(2)
                        }
                        Spacer()
                    }
                    .padding(12)
                    .background(SurveyStyle.panel, in: RoundedRectangle(cornerRadius: 10))
                }
            }
        }
    }
}

private extension SurveyStep {
    var headerTitle: String {
        switch self {
        case .welcome:
            return "Survey"
        case .connectAppleMusic:
            return "Apple Music"
        case .artistPage1:
            return "Artist Grid 1"
        case .artistPage2:
            return "Artist Grid 2"
        case .artistPage3Prompt:
            return "Optional Pass"
        case .artistPage3:
            return "Artist Grid 3"
        case .albumPage1:
            return "Album Grid"
        case .songPage1:
            return "Song Grid"
        case .deeperPrompt:
            return "Go Deeper?"
        case .advancedSurvey:
            return "Advanced Survey"
        case .readout:
            return "Readout"
        }
    }

    var headerSubtitle: String {
        switch self {
        case .welcome:
            return "A simple first pass, then optional depth"
        case .connectAppleMusic:
            return "Apple Music becomes the primary seed"
        case .artistPage1:
            return "Known territory and calibration"
        case .artistPage2:
            return "Dynamic follow-up from early answers"
        case .artistPage3Prompt:
            return "Sharpen now or keep moving"
        case .artistPage3:
            return "Optional signal sharpening"
        case .albumPage1:
            return "Artist-wide versus object-specific taste"
        case .songPage1:
            return "Exceptions and cultural furniture"
        case .deeperPrompt:
            return "Advanced Survey stays optional"
        case .advancedSurvey:
            return "Filters and freeform evidence"
        case .readout:
            return "Evidence, not verdicts"
        }
    }
}

private extension SurveySignalState {
    var shortLabel: String {
        switch self {
        case .dontKnow:
            return "?"
        case .fine:
            return "Fine"
        case .like:
            return "Like"
        case .favorite:
            return "Fav"
        case .notForMe:
            return "No"
        }
    }

    var systemImage: String? {
        switch self {
        case .dontKnow:
            return nil
        case .fine:
            return "circle.fill"
        case .like:
            return "heart.fill"
        case .favorite:
            return "star.fill"
        case .notForMe:
            return "xmark"
        }
    }

    var tintColor: Color {
        switch self {
        case .dontKnow:
            return .white.opacity(0.42)
        case .fine:
            return .cyan
        case .like:
            return .green
        case .favorite:
            return .yellow
        case .notForMe:
            return .red
        }
    }

    var surfaceColor: Color {
        switch self {
        case .dontKnow:
            return SurveyStyle.panel
        default:
            return tintColor.opacity(0.16)
        }
    }

    var foregroundColor: Color {
        switch self {
        case .dontKnow:
            return .white.opacity(0.72)
        case .fine:
            return .cyan.opacity(0.95)
        case .like:
            return .green.opacity(0.92)
        case .favorite:
            return .yellow.opacity(0.96)
        case .notForMe:
            return .red.opacity(0.92)
        }
    }
}
