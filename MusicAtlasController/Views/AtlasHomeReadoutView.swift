import SwiftUI

struct AtlasHomeReadoutModuleView: View {
    let readout: AtlasHomeReadoutDisplayModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 8) {
                Text(readout.moduleName)
                    .font(.title2.weight(.bold))
                    .foregroundStyle(WaymarkTheme.text)
                    .fixedSize(horizontal: false, vertical: true)

                Text(readout.openingInsight)
                    .font(.callout)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            ForEach(readout.insightCards) { card in
                AtlasHomeReadoutCardView(card: card)
            }

            if let setupLine = readout.setupLine?.trimmingCharacters(in: .whitespacesAndNewlines),
               !setupLine.isEmpty {
                Label(setupLine, systemImage: "arrow.triangle.branch")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.signal)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.top, 2)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .contain)
    }
}

private struct AtlasHomeReadoutCardView: View {
    let card: AtlasHomeReadoutCard

    var body: some View {
        VStack(alignment: .leading, spacing: 9) {
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Label(card.signalRole.displayLabel, systemImage: card.signalRole.systemImage)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(tint)
                    .labelStyle(.titleAndIcon)

                Spacer(minLength: 8)
            }

            Text(card.title)
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text(card.body)
                .font(.callout)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            if !card.evidenceExamples.isEmpty {
                Text("Evidence: \(card.evidenceExamples.joined(separator: ", "))")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.text.opacity(0.74))
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

    private var tint: Color {
        switch card.signalRole {
        case .strongestCenter:
            return WaymarkTheme.signal
        case .soundShape:
            return WaymarkTheme.route
        case .secondaryBranch:
            return WaymarkTheme.positive
        case .sparseCleanSignal:
            return WaymarkTheme.waypoint
        case .openQuestionBoundary:
            return WaymarkTheme.mutedText
        }
    }
}
