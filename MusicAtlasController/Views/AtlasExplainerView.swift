import SwiftUI

struct AtlasExplainerHomeView: View {
    @ObservedObject var store: AtlasExplainerStore
    @ObservedObject var readoutStore: AtlasHomeReadoutStore
    private let copyDepth = AtlasExplainerRuntimePolicy.alphaCopyDepth

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    header

                    switch store.loadState {
                    case .idle, .loading:
                        ProgressView(AtlasExplainerRuntimePolicy.loadingTitle)
                            .tint(WaymarkTheme.route)
                            .frame(maxWidth: .infinity, minHeight: 120)
                    case .failed:
                        AtlasExplainerNotice(
                            title: AtlasExplainerRuntimePolicy.unavailableTitle,
                            detail: AtlasExplainerRuntimePolicy.unavailableDetail,
                            systemImage: "exclamationmark.triangle",
                            tint: WaymarkTheme.negative
                        )
                    case .loaded:
                        loadedContent
                    }
                }
                .padding(18)
            }
            .background(WaymarkTheme.background.ignoresSafeArea())
        }
        .task {
            store.load()
            readoutStore.load()
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(AtlasExplainerRuntimePolicy.atlasTitle)
                        .font(.largeTitle.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                    Text(AtlasExplainerRuntimePolicy.atlasSubtitle)
                        .font(.callout)
                        .foregroundStyle(WaymarkTheme.mutedText)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer()

                Text("\(store.library.homePackCount) \(AtlasExplainerRuntimePolicy.roadCountSuffix)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(WaymarkTheme.text)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(WaymarkTheme.raisedPanel, in: Capsule())
            }
        }
    }

    @ViewBuilder
    private var loadedContent: some View {
        if let readout = readoutStore.displayModel {
            AtlasHomeReadoutModuleView(readout: readout)
        }

        ForEach(store.library.homeSections) { section in
            AtlasExplainerHomeSectionView(section: section, copyDepth: copyDepth)
        }
    }
}

private struct AtlasExplainerHomeSectionView: View {
    let section: AtlasExplainerHomeSection
    let copyDepth: AtlasExplainerCopyDepth

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            VStack(alignment: .leading, spacing: 4) {
                Text(section.title)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                Text(section.subtitle)
                    .font(.caption)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            ForEach(section.packs) { pack in
                NavigationLink {
                    AtlasExplainerScenePage(pack: pack, copyDepth: copyDepth)
                } label: {
                    AtlasExplainerRegionCard(pack: pack, copyDepth: copyDepth)
                }
                .buttonStyle(.plain)
            }
        }
    }
}

struct AtlasMissionDetailExplainerModule: View {
    let mission: Mission
    let library: AtlasExplainerLibrary
    var copyDepth: AtlasExplainerCopyDepth = AtlasExplainerRuntimePolicy.alphaCopyDepth

    private var matchedPack: AtlasExplainerRenderPack? {
        library.pack(matching: mission)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(AtlasExplainerRuntimePolicy.missionModuleTitle)
                    .font(.title3.weight(.bold))
                    .foregroundStyle(WaymarkTheme.text)
                Spacer()
                Text(AtlasExplainerRuntimePolicy.missionModuleBadge)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(WaymarkTheme.text)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .background(WaymarkTheme.route.opacity(0.16), in: Capsule())
            }

            if let matchedPack {
                Text(matchedPack.displayTitle)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.route)
                    .fixedSize(horizontal: false, vertical: true)

                Text(matchedPack.modules.missionDetailHistoryModule.copy(for: copyDepth))
                    .font(.body)
                    .foregroundStyle(WaymarkTheme.text)
                    .fixedSize(horizontal: false, vertical: true)

                Text(matchedPack.modules.whatToListenForPrompt.compact)
                    .font(.callout.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.signal)
                    .fixedSize(horizontal: false, vertical: true)
            } else {
                Text(AtlasExplainerRuntimePolicy.missingMissionExplainer)
                    .font(.body)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
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

private struct AtlasExplainerScenePage: View {
    let pack: AtlasExplainerRenderPack
    let copyDepth: AtlasExplainerCopyDepth

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(pack.identity.familyName)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(WaymarkTheme.route)
                        .textCase(.uppercase)

                    Text(pack.displayTitle)
                        .font(.largeTitle.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                        .fixedSize(horizontal: false, vertical: true)

                    Text(pack.modules.regionScenePage.copy(for: copyDepth))
                        .font(.body)
                        .foregroundStyle(WaymarkTheme.mutedText)
                        .fixedSize(horizontal: false, vertical: true)
                }

                AtlasExplainerModuleCard(
                    title: AtlasExplainerRuntimePolicy.didYouKnowTitle,
                    systemImage: "lightbulb",
                    bodyText: pack.modules.didYouKnowCard.copy(for: copyDepth)
                )

                AtlasExplainerModuleCard(
                    title: AtlasExplainerRuntimePolicy.listenForTitle,
                    systemImage: "ear",
                    bodyText: pack.modules.whatToListenForPrompt.copy(for: copyDepth),
                    tint: WaymarkTheme.signal
                )

                AtlasExplainerExamplesBlock(pack: pack)

                AtlasExplainerModuleCard(
                    title: AtlasExplainerRuntimePolicy.relatedRoadsTitle,
                    systemImage: "point.3.connected.trianglepath.dotted",
                    bodyText: pack.modules.relatedRoadsLineageModule.copy(for: copyDepth),
                    tint: WaymarkTheme.route
                )

                if !pack.modules.deadEndFalseNearbyCautionModule.standard.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    AtlasExplainerModuleCard(
                        title: AtlasExplainerRuntimePolicy.falseNearbyTitle,
                        systemImage: "signpost.right",
                        bodyText: pack.modules.deadEndFalseNearbyCautionModule.copy(for: copyDepth),
                        tint: WaymarkTheme.waypoint
                    )
                }
            }
            .padding(18)
        }
        .background(WaymarkTheme.background.ignoresSafeArea())
        .navigationTitle(pack.displayTitle)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct AtlasExplainerRegionCard: View {
    let pack: AtlasExplainerRenderPack
    let copyDepth: AtlasExplainerCopyDepth

    var body: some View {
        VStack(alignment: .leading, spacing: 9) {
            HStack(alignment: .firstTextBaseline) {
                Text(pack.displayTitle)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                    .fixedSize(horizontal: false, vertical: true)

                Spacer()
            }

            Text(pack.modules.atlasHomeRegionCard.copy(for: copyDepth))
                .font(.callout)
                .foregroundStyle(WaymarkTheme.mutedText)
                .lineLimit(copyDepth == .deep ? 6 : 4)

            HStack(spacing: 8) {
                Image(systemName: "arrow.right.circle")
                Text(pack.identity.familyName)
                    .lineLimit(1)
            }
            .font(.caption.weight(.semibold))
            .foregroundStyle(WaymarkTheme.route)
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

private struct AtlasExplainerExamplesBlock: View {
    let pack: AtlasExplainerRenderPack

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(AtlasExplainerRuntimePolicy.examplesTitle, systemImage: "rectangle.stack")
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)

            ForEach(sectionedExamples) { section in
                VStack(alignment: .leading, spacing: 8) {
                    Text(section.title)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(WaymarkTheme.route)
                        .textCase(.uppercase)

                    ForEach(section.examples) { example in
                        AtlasExplainerExampleCard(example: example)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var sectionedExamples: [AtlasExplainerExampleSectionModel] {
        let sections: [(id: String, title: String)] = [
            ("start_here", "Start Here"),
            ("next_level", "Next Level"),
            ("go_deep", "Go Deep")
        ]
        let grouped = Dictionary(grouping: pack.canonicalExamples) { example in
            example.ladderSection ?? ""
        }
        let ordered = sections.compactMap { section -> AtlasExplainerExampleSectionModel? in
            guard let examples = grouped[section.id], !examples.isEmpty else {
                return nil
            }
            return AtlasExplainerExampleSectionModel(id: section.id, title: section.title, examples: examples)
        }

        if !ordered.isEmpty {
            return ordered
        }

        return [
            AtlasExplainerExampleSectionModel(
                id: "examples",
                title: "Examples",
                examples: pack.canonicalExamples
            )
        ]
    }
}

private struct AtlasExplainerExampleSectionModel: Identifiable {
    let id: String
    let title: String
    let examples: [AtlasExplainerCanonicalExample]
}

private struct AtlasExplainerExampleCard: View {
    let example: AtlasExplainerCanonicalExample

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            formattedTitle
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text(example.whyThisExampleMatters)
                .font(.caption)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            if !example.whatToListenFor.isEmpty {
                AtlasExplainerTagCloud(tags: example.whatToListenFor)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.raisedPanel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
    }

    private var formattedTitle: Text {
        guard
            let title = example.title,
            let artist = example.artistDisplayName,
            !title.isEmpty,
            !artist.isEmpty
        else {
            return Text(example.displayLabel)
        }

        switch example.exampleType {
        case "album":
            return Text(title).italic() + Text(" – \(artist)")
        case "artist":
            return Text(artist)
        default:
            return Text("“\(title)”") + Text(" – \(artist)")
        }
    }
}

private struct AtlasExplainerTagCloud: View {
    let tags: [String]
    private let columns = [
        GridItem(.adaptive(minimum: 76), spacing: 6, alignment: .leading)
    ]

    var body: some View {
        LazyVGrid(columns: columns, alignment: .leading, spacing: 6) {
            ForEach(tags, id: \.self) { tag in
                Text(tag)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(WaymarkTheme.signal)
                    .lineLimit(1)
                    .minimumScaleFactor(0.78)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .background(WaymarkTheme.signal.opacity(0.13), in: Capsule())
            }
        }
    }
}

private struct AtlasExplainerModuleCard: View {
    let title: String
    let systemImage: String
    let bodyText: String
    var tint: Color = WaymarkTheme.route

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(title, systemImage: systemImage)
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)

            ForEach(bodyParagraphs.indices, id: \.self) { index in
                Text(bodyParagraphs[index])
                    .font(.body)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(tint.opacity(0.35), lineWidth: 1)
        )
    }

    private var bodyParagraphs: [String] {
        let paragraphs = bodyText
            .components(separatedBy: "\n\n")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        return paragraphs.isEmpty ? [bodyText] : paragraphs
    }
}

private struct AtlasExplainerNotice: View {
    let title: String
    let detail: String
    let systemImage: String
    let tint: Color

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: systemImage)
                .foregroundStyle(tint)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                Text(detail)
                    .font(.callout)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(tint.opacity(0.35), lineWidth: 1)
        )
    }
}
