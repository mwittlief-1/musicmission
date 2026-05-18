import Foundation

@MainActor
final class ReactionStore {
    private(set) var reactions: [String: ReactionRecord] = [:]

    func reaction(for itemID: String) -> ReactionRecord? {
        reactions[itemID]
    }

    func allReactions() -> [String: ReactionRecord] {
        reactions
    }

    func replaceAll(with reactions: [String: ReactionRecord]) {
        self.reactions = reactions
    }

    func saveReaction(
        for itemID: String,
        value: ReactionValue,
        note: String,
        selectedTags: [ReactionTag] = [],
        at date: Date
    ) throws {
        let trimmedNote = note.trimmingCharacters(in: .whitespacesAndNewlines)

        reactions[itemID] = ReactionRecord(
            reactionValue: value,
            reactedAt: date,
            selectedTags: selectedTags.isEmpty ? nil : selectedTags,
            notes: ReactionNotes(text: trimmedNote, voiceNoteRefs: nil)
        )
    }

    func reset() {
        reactions.removeAll()
    }
}

enum ReactionStoreError: LocalizedError {
    case emptyNote

    var errorDescription: String? {
        switch self {
        case .emptyNote:
            return "Enter a non-empty note before saving a reaction."
        }
    }
}
