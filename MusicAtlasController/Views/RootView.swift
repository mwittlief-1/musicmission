import SwiftUI

enum AppTab: Hashable {
    case survey
    case mission
    case resolve
    case player
    case review
    case export
}

struct RootView: View {
    @State private var selectedTab: AppTab = .survey

    var body: some View {
        TabView(selection: $selectedTab) {
            SurveyView()
                .tabItem {
                    Label("Survey", systemImage: "square.grid.3x3")
                }
                .tag(AppTab.survey)

            MissionListView()
                .tabItem {
                    Label("Mission", systemImage: "music.note.list")
                }
                .tag(AppTab.mission)

            ResolverStatusView()
                .tabItem {
                    Label("Resolve", systemImage: "magnifyingglass")
                }
                .tag(AppTab.resolve)

            NowTestingView(
                openMissionReview: {
                    selectedTab = .review
                },
                openResolveIssue: {
                    selectedTab = .resolve
                }
            )
                .tabItem {
                    Label("Player", systemImage: "play.circle")
                }
                .tag(AppTab.player)

            MissionReviewView()
                .tabItem {
                    Label("Review", systemImage: "list.clipboard")
                }
                .tag(AppTab.review)

            ExportPreviewView()
                .tabItem {
                    Label("Export", systemImage: "square.and.arrow.up")
                }
                .tag(AppTab.export)
        }
    }
}
