import Foundation
import XCTest
@testable import MusicAtlasController

@MainActor
final class AtlasHomeReadoutTests: XCTestCase {
    func testLoadsApprovedAtlasHomeReadoutFixture() throws {
        let fixture = try loadFixture()
        let readout = fixture.displayModel

        XCTAssertEqual(fixture.schemaVersion, AtlasHomeReadoutStore.supportedSchemaVersion)
        XCTAssertEqual(readout.moduleName, "What We're Seeing So Far")
        XCTAssertEqual(readout.insightCards.count, 5)
        XCTAssertNil(readout.setupLine)
        XCTAssertEqual(readout.insightCards.map(\.signalRole), [
            .strongestCenter,
            .soundShape,
            .secondaryBranch,
            .sparseCleanSignal,
            .openQuestionBoundary
        ])
    }

    func testFixtureAuditMatchesRenderedCopyLimits() throws {
        let fixture = try loadFixture()
        let readout = fixture.displayModel
        let audit = fixture.acceptanceAudit

        XCTAssertEqual(audit.moduleWordCount, wordCount(renderedModuleText(readout)))
        XCTAssertEqual(audit.openingWordCount, wordCount(readout.openingInsight))
        XCTAssertEqual(audit.cardCount, readout.insightCards.count)
        XCTAssertEqual(audit.cardRoles, readout.insightCards.map(\.signalRole))
        XCTAssertEqual(audit.cardTitleWordCounts, readout.insightCards.map { wordCount($0.title) })
        XCTAssertEqual(audit.cardBodyWordCounts, readout.insightCards.map { wordCount($0.body) })
        XCTAssertEqual(audit.evidenceExamplesPerCard, readout.insightCards.map { $0.evidenceExamples.count })

        XCTAssertGreaterThanOrEqual(audit.moduleWordCount, 220)
        XCTAssertLessThanOrEqual(audit.moduleWordCount, 425)
        XCTAssertLessThanOrEqual(audit.openingWordCount, 35)
        XCTAssertTrue(audit.cardTitleWordCounts.allSatisfy { $0 <= 8 })
        XCTAssertTrue(audit.cardBodyWordCounts.allSatisfy { $0 <= 45 })
        XCTAssertTrue(audit.evidenceExamplesPerCard.allSatisfy { $0 <= 3 })
    }

    func testSparseCleanClassicHeavyRockPocketIsEligibleAndSurfaced() throws {
        let fixture = try loadFixture()
        let candidate = try XCTUnwrap(fixture.sparseSignalDebug.candidates.first { $0.label == "classic/heavy rock" })
        let card = try XCTUnwrap(fixture.displayModel.insightCards.first { $0.signalRole == .sparseCleanSignal })

        XCTAssertGreaterThanOrEqual(candidate.positiveExamples.count, 2)
        XCTAssertTrue(candidate.negativeExamples.isEmpty)
        XCTAssertTrue(candidate.neutralExamples.isEmpty)
        XCTAssertTrue(candidate.hasMeaningfulGraphCoherence)
        XCTAssertTrue(candidate.hasFutureTestValue)
        XCTAssertTrue(candidate.satisfiesSparseCleanRule)
        XCTAssertTrue(candidate.eligible)
        XCTAssertEqual(candidate.decision, "surface")
        XCTAssertEqual(candidate.surfacedCardTitle, card.title)
        XCTAssertEqual(card.title, "Small but clean heavy-rock signal")
        XCTAssertEqual(card.evidenceExamples, ["Led Zeppelin", "The Who", "Black Sabbath"])
        XCTAssertFalse(card.body.localizedCaseInsensitiveContains("major region"))
    }

    func testReadoutCopyCompliance() throws {
        let fixture = try loadFixture()
        let readout = fixture.displayModel
        let displayText = displayStrings(readout).joined(separator: "\n")
        let lowercasedDisplayText = displayText.lowercased()

        let forbiddenPhrases = [
            "out of 84 survey responses",
            "you selected",
            "you clicked",
            "your responses included",
            "the cluster is backed by",
            "final map",
            "final truth",
            "we know",
            "you love",
            "cartenza learned",
            "permanent rejection",
            "sonic_texture:guitar_forward",
            "rhythm_body:driving_eighths",
            "emotion_theme:alienation",
            "matt",
            "founder",
            "openai",
            "gpt"
        ]

        for phrase in forbiddenPhrases {
            XCTAssertFalse(lowercasedDisplayText.contains(phrase), "Forbidden phrase found: \(phrase)")
        }

        XCTAssertFalse(containsRawTag(in: displayText))
        XCTAssertTrue(displayText.contains("Unknowns stay open"))
        XCTAssertTrue(displayText.contains("negative evidence stays cautious"))
        XCTAssertEqual(readout.insightCards.filter { $0.signalRole == .strongestCenter }.count, 1)
        XCTAssertLessThanOrEqual(readout.insightCards.filter { $0.signalRole == .strongestCenter }.count, 2)
        XCTAssertTrue(fixture.acceptanceAudit.usesSyntheticFixtureStateOnly)
        XCTAssertFalse(fixture.acceptanceAudit.runtimeGenerationRequired)
    }

    private func loadFixture() throws -> AtlasHomeReadoutFixture {
        try AtlasHomeReadoutStore.loadFixture(bundle: Bundle(for: AtlasHomeReadoutTests.self))
    }

    private func displayStrings(_ readout: AtlasHomeReadoutDisplayModel) -> [String] {
        var strings = [
            readout.moduleName,
            readout.openingInsight
        ]

        for card in readout.insightCards {
            strings.append(card.title)
            strings.append(card.body)
            strings.append(contentsOf: card.evidenceExamples)
        }

        if let setupLine = readout.setupLine {
            strings.append(setupLine)
        }

        return strings
    }

    private func renderedModuleText(_ readout: AtlasHomeReadoutDisplayModel) -> String {
        displayStrings(readout).joined(separator: " ")
    }

    private func wordCount(_ text: String) -> Int {
        let pattern = #"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?"#
        let regex = try! NSRegularExpression(pattern: pattern)
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.numberOfMatches(in: text, range: range)
    }

    private func containsRawTag(in text: String) -> Bool {
        let pattern = #"\b[a-z]+(?:_[a-z]+)+:[a-z0-9_]+\b"#
        let regex = try! NSRegularExpression(pattern: pattern)
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.firstMatch(in: text, range: range) != nil
    }
}
