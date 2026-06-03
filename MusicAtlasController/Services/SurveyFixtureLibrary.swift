import Foundation

enum SurveyFixtureLibrary {
    static let gridPageItemLimit = 12

    static func page(for step: SurveyStep, responses: [String: SurveyResponse]) -> SurveyGridPage? {
        switch step {
        case .artistPage1:
            return SurveyGridPage(
                id: "SURVEY_ARTIST_PAGE_1",
                title: "Artist Grid 1",
                subtitle: "Apple Music-heavy seed pass",
                kind: .artist,
                pageIndex: 1,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: artistPage1())
            )
        case .artistPage2:
            return SurveyGridPage(
                id: "SURVEY_ARTIST_PAGE_2",
                title: "Artist Grid 2",
                subtitle: "Built from early likes, misses, and unknowns",
                kind: .artist,
                pageIndex: 2,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: adaptiveArtistPage2(responses: responses))
            )
        case .artistPage3:
            return SurveyGridPage(
                id: "SURVEY_ARTIST_PAGE_3",
                title: "Artist Grid 3",
                subtitle: "Sleeper frontiers and false-nearby risks",
                kind: .artist,
                pageIndex: 3,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: adaptiveArtistPage3(responses: responses))
            )
        case .artistPage4:
            return SurveyGridPage(
                id: "SURVEY_ARTIST_PAGE_4",
                title: "Artist Grid 4",
                subtitle: "Final artist calibration pass",
                kind: .artist,
                pageIndex: 4,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: artistPage4(responses: responses))
            )
        case .albumPage1:
            return SurveyGridPage(
                id: "SURVEY_ALBUM_PAGE_1",
                title: "Album Grid 1",
                subtitle: "Object-specific checks",
                kind: .album,
                pageIndex: 1,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: albumPage(responses: responses))
            )
        case .albumPage2:
            return SurveyGridPage(
                id: "SURVEY_ALBUM_PAGE_2",
                title: "Album Grid 2",
                subtitle: "Object-specific contradictions and boundary checks",
                kind: .album,
                pageIndex: 2,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: albumPage2(responses: responses))
            )
        case .songPage1:
            return SurveyGridPage(
                id: "SURVEY_SONG_PAGE_1",
                title: "Song Grid 1",
                subtitle: "Exceptions, furniture, and false inference checks",
                kind: .song,
                pageIndex: 1,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: songPage(responses: responses, pageIndex: 1))
            )
        case .songPage2:
            return SurveyGridPage(
                id: "SURVEY_SONG_PAGE_2",
                title: "Song Grid 2",
                subtitle: "Known songs, sleepers, and useful negatives",
                kind: .song,
                pageIndex: 2,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: songPage(responses: responses, pageIndex: 2))
            )
        case .songPage3:
            return SurveyGridPage(
                id: "SURVEY_SONG_PAGE_3",
                title: "Song Grid 3",
                subtitle: "Song-only exceptions and cultural furniture",
                kind: .song,
                pageIndex: 3,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: songPage(responses: responses, pageIndex: 3))
            )
        case .songPage4:
            return SurveyGridPage(
                id: "SURVEY_SONG_PAGE_4",
                title: "Song Grid 4",
                subtitle: "Final song calibration pass",
                kind: .song,
                pageIndex: 4,
                isOptional: false,
                items: itemsForStep(step, responses: responses, candidates: songPage(responses: responses, pageIndex: 4))
            )
        default:
            return nil
        }
    }

    static func advancedPage(for filter: SurveyAdvancedFilter, responses: [String: SurveyResponse]) -> SurveyGridPage {
        let title: String
        let subtitle: String
        let items: [SurveyItem]

        switch filter {
        case .era:
            title = "Era Pass"
            subtitle = "90s, 70s, current, and prehistory checks"
            items = advancedEraItems()
        case .genre:
            title = "Genre Pass"
            subtitle = "Broad containers, not final verdicts"
            items = advancedGenreItems()
        case .countryRegion:
            title = "Country Pass"
            subtitle = "Regional frontiers and known territory"
            items = advancedCountryItems()
        case .scene:
            title = "Scene Pass"
            subtitle = "Scenes and microclimates"
            items = advancedSceneItems()
        case .popularity:
            title = "Popularity Pass"
            subtitle = "Mainstream, cult, and deep-cut tolerance"
            items = advancedPopularityItems()
        case .likelyDeadEnds:
            title = "Dead-End Pass"
            subtitle = "Useful negatives for the map"
            items = rejectionPool().prefixItems(gridPageItemLimit)
        case .sleepers:
            title = "Sleeper Pass"
            subtitle = "Possible frontiers worth not missing"
            items = sleeperPool().prefixItems(gridPageItemLimit)
        case .libraryUnrated:
            title = "Unrated Library Pass"
            subtitle = "Apple Music loose ends you have not scored here"
            let answeredIDs = Set(responses.keys)
            items = (artistPage1() + appleMusicLooseEndPool())
                .filter { !answeredIDs.contains($0.id) }
                .prefixItems(gridPageItemLimit)
        }

        return SurveyGridPage(
            id: "SURVEY_ADVANCED_\(filter.rawValue.uppercased())",
            title: title,
            subtitle: subtitle,
            kind: .artist,
            pageIndex: 1,
            isOptional: true,
            items: items.prefixItems(gridPageItemLimit)
        )
    }

    static func itemLookup() -> [String: SurveyItem] {
        let allItems = artistPage1() +
            adjacentArtistPool() +
            sleeperPool() +
            rejectionPool() +
            calibrationPool() +
            appleMusicLooseEndPool() +
            albumBasePool() +
            albumExpansionPool() +
            songBasePool() +
            songExpansionPool() +
            advancedEraItems() +
            advancedGenreItems() +
            advancedCountryItems() +
            advancedSceneItems() +
            advancedPopularityItems()

        return Dictionary(uniqueKeysWithValues: unique(allItems).map { ($0.id, $0) })
    }

    static func shouldOfferArtistPage3(responses: [String: SurveyResponse]) -> Bool {
        let pageResponses = responses.values.filter { $0.itemKind == .artist }
        let unknowns = pageResponses.filter { $0.state == .dontKnow }.count
        let favorites = pageResponses.filter { $0.state == .favorite }.count
        let negatives = pageResponses.filter { $0.state == .notForMe }.count
        let positives = pageResponses.filter { $0.state == .like || $0.state == .favorite }.count

        return unknowns >= 8 || favorites >= 6 || abs(positives - negatives) <= 2
    }

    private static func adaptiveArtistPage2(responses: [String: SurveyResponse]) -> [SurveyItem] {
        let positiveIDs = Set(responses.values.filter { $0.state == .like || $0.state == .favorite }.map(\.itemID))
        let negativeCount = responses.values.filter { $0.state == .notForMe }.count
        var page = [SurveyItem]()

        page.append(contentsOf: appleMusicLooseEndPool().prefixItems(4))
        page.append(contentsOf: adjacentArtistPool(preferNoiseRoad: positiveIDs.contains("SURV_ARTIST_NIRVANA") || positiveIDs.contains("SURV_ARTIST_SONIC_YOUTH")).prefixItems(3))
        page.append(contentsOf: sleeperPool().prefixItems(2))
        page.append(contentsOf: rejectionPool().prefixItems(negativeCount >= 4 ? 2 : 1))
        page.append(contentsOf: calibrationPool().prefixItems(2))

        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func adaptiveArtistPage3(responses: [String: SurveyResponse]) -> [SurveyItem] {
        let favoriteCount = responses.values.filter { $0.state == .favorite }.count
        var page = [SurveyItem]()

        page.append(contentsOf: adjacentArtistPool(preferNoiseRoad: favoriteCount >= 4).dropFirst(4).prefixItems(4))
        page.append(contentsOf: sleeperPool().dropFirst(3).prefixItems(3))
        page.append(contentsOf: rejectionPool().dropFirst(2).prefixItems(2))
        page.append(contentsOf: appleMusicLooseEndPool().dropFirst(5).prefixItems(2))
        page.append(contentsOf: calibrationPool().dropFirst(2).prefixItems(1))

        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func artistPage4(responses: [String: SurveyResponse]) -> [SurveyItem] {
        let negativeCount = responses.values.filter { $0.state == .notForMe }.count
        var page = [SurveyItem]()

        page.append(contentsOf: calibrationPool().prefixItems(3))
        page.append(contentsOf: appleMusicLooseEndPool().dropFirst(3).prefixItems(3))
        page.append(contentsOf: adjacentArtistPool(preferNoiseRoad: negativeCount < 5).dropFirst(2).prefixItems(3))
        page.append(contentsOf: sleeperPool().dropFirst(1).prefixItems(2))
        page.append(contentsOf: rejectionPool().dropFirst(1).prefixItems(2))

        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func albumPage(responses: [String: SurveyResponse]) -> [SurveyItem] {
        let hasNirvanaPositive = responses["SURV_ARTIST_NIRVANA"]?.state == .like || responses["SURV_ARTIST_NIRVANA"]?.state == .favorite
        var page = albumBasePool()
        if hasNirvanaPositive {
            page.insert(item(id: "SURV_ALBUM_WIPERS_OVER_EDGE", kind: .album, title: "Over the Edge", subtitle: "Wipers", source: .responseAdjacent, objective: .separateObjectTaste, rationale: "Album-world test for pre-Nirvana pressure."), at: 0)
        }
        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func albumPage2(responses: [String: SurveyResponse]) -> [SurveyItem] {
        let positiveArtistCount = responses.values.filter { $0.itemKind == .artist && ($0.state == .like || $0.state == .favorite) }.count
        var page = [SurveyItem]()

        page.append(contentsOf: albumExpansionPool().prefixItems(positiveArtistCount >= 6 ? 8 : 6))
        page.append(contentsOf: albumBasePool().dropFirst(gridPageItemLimit).prefixItems(8))

        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func songPage(responses: [String: SurveyResponse], pageIndex: Int) -> [SurveyItem] {
        let notForMeCount = responses.values.filter { $0.state == .notForMe }.count
        let songPool = unique(songBasePool() + songExpansionPool())
        let offset = max(0, pageIndex - 1) * gridPageItemLimit
        var page = rotated(songPool, offset: offset).prefixItems(gridPageItemLimit)
        if notForMeCount >= 5 {
            page.insert(item(id: "SURV_SONG_REJECTION_CONTROL", kind: .song, title: "The Distance", subtitle: "Cake", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Tests ironic sing-talk tolerance after many negatives."), at: 3)
        }
        return unique(page).prefixItems(gridPageItemLimit)
    }

    private static func itemsForStep(
        _ step: SurveyStep,
        responses: [String: SurveyResponse],
        candidates: [SurveyItem]
    ) -> [SurveyItem] {
        let previousIDs = priorRequiredPageIDs(before: step, responses: responses)
        var seen = Set<String>()
        var selected: [SurveyItem] = []

        for item in candidates where !previousIDs.contains(item.id) && !seen.contains(item.id) {
            selected.append(item)
            seen.insert(item.id)
            if selected.count == gridPageItemLimit {
                return selected
            }
        }

        for item in fallbackPool(for: step, responses: responses) where !previousIDs.contains(item.id) && !seen.contains(item.id) {
            selected.append(item)
            seen.insert(item.id)
            if selected.count == gridPageItemLimit {
                return selected
            }
        }

        return selected
    }

    private static func priorRequiredPageIDs(before step: SurveyStep, responses: [String: SurveyResponse]) -> Set<String> {
        let priorItems: [SurveyItem]
        switch step {
        case .artistPage1:
            priorItems = []
        case .artistPage2:
            priorItems = artistPage1().prefixItems(gridPageItemLimit)
        case .artistPage3:
            priorItems = artistPage1().prefixItems(gridPageItemLimit) +
                adaptiveArtistPage2(responses: responses).prefixItems(gridPageItemLimit)
        case .artistPage4:
            priorItems = artistPage1().prefixItems(gridPageItemLimit) +
                adaptiveArtistPage2(responses: responses).prefixItems(gridPageItemLimit) +
                adaptiveArtistPage3(responses: responses).prefixItems(gridPageItemLimit)
        case .albumPage1:
            priorItems = []
        case .albumPage2:
            priorItems = albumPage(responses: responses).prefixItems(gridPageItemLimit)
        case .songPage1:
            priorItems = []
        case .songPage2:
            priorItems = songPage(responses: responses, pageIndex: 1).prefixItems(gridPageItemLimit)
        case .songPage3:
            priorItems = songPage(responses: responses, pageIndex: 1).prefixItems(gridPageItemLimit) +
                songPage(responses: responses, pageIndex: 2).prefixItems(gridPageItemLimit)
        case .songPage4:
            priorItems = songPage(responses: responses, pageIndex: 1).prefixItems(gridPageItemLimit) +
                songPage(responses: responses, pageIndex: 2).prefixItems(gridPageItemLimit) +
                songPage(responses: responses, pageIndex: 3).prefixItems(gridPageItemLimit)
        default:
            priorItems = []
        }

        return Set(priorItems.map(\.id))
    }

    private static func fallbackPool(for step: SurveyStep, responses: [String: SurveyResponse]) -> [SurveyItem] {
        switch step {
        case .artistPage1, .artistPage2, .artistPage3, .artistPage4:
            return unique(
                artistPage1() +
                appleMusicLooseEndPool() +
                adjacentArtistPool() +
                sleeperPool() +
                rejectionPool() +
                calibrationPool()
            )
        case .albumPage1, .albumPage2:
            return unique(albumBasePool() + albumExpansionPool())
        case .songPage1, .songPage2, .songPage3, .songPage4:
            var pool = unique(songBasePool() + songExpansionPool())
            if responses.values.filter({ $0.state == .notForMe }).count >= 5 {
                pool.append(item(id: "SURV_SONG_REJECTION_CONTROL", kind: .song, title: "The Distance", subtitle: "Cake", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Tests ironic sing-talk tolerance after many negatives."))
            }
            return unique(pool)
        default:
            return []
        }
    }

    private static func artistPage1() -> [SurveyItem] {
        [
            item(id: "SURV_ARTIST_NIRVANA", title: "Nirvana", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Known anchor for pressure, hooks, and rupture."),
            item(id: "SURV_ARTIST_RADIOHEAD", title: "Radiohead", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Album-world and modern rock gravity check."),
            item(id: "SURV_ARTIST_FLEETWOOD_MAC", title: "Fleetwood Mac", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Songcraft versus album/artist-wide appetite."),
            item(id: "SURV_ARTIST_THE_BEATLES", title: "The Beatles", source: .appleMusicDerived, objective: .calibrateBroadly, rationale: "Broad canon calibration."),
            item(id: "SURV_ARTIST_PRINCE", title: "Prince", source: .appleMusicDerived, objective: .resolveContradiction, rationale: "Admire-versus-crave separation."),
            item(id: "SURV_ARTIST_TAYLOR_SWIFT", title: "Taylor Swift", source: .appleMusicDerived, objective: .resolveContradiction, rationale: "Songcraft/persona/mainstream pop calibration."),
            item(id: "SURV_ARTIST_SONIC_YOUTH", title: "Sonic Youth", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Noise-road adjacency."),
            item(id: "SURV_ARTIST_THE_CURE", title: "The Cure", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Dark melody and atmosphere calibration."),
            item(id: "SURV_ARTIST_TALKING_HEADS", title: "Talking Heads", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Nervous art-pop calibration."),
            item(id: "SURV_ARTIST_WIPERS", title: "Wipers", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Pre-Nirvana pressure sleeper."),
            item(id: "SURV_ARTIST_GARBANOTAS", title: "Garbanotas", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Baltic psych-pop frontier."),
            item(id: "SURV_ARTIST_DAVE_MATTHEWS_BAND", title: "Dave Matthews Band", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Adult-alternative/mush control."),
            item(id: "SURV_ARTIST_LED_ZEPPELIN", title: "Led Zeppelin", source: .appleMusicDerived, objective: .calibrateBroadly, rationale: "Classic-rock force calibration."),
            item(id: "SURV_ARTIST_PIXIES", title: "Pixies", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Alt source-code hook/violence test."),
            item(id: "SURV_ARTIST_JOY_DIVISION", title: "Joy Division", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Post-punk body/gloom check."),
            item(id: "SURV_ARTIST_LCD_SOUNDSYSTEM", title: "LCD Soundsystem", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Body plus brain alignment check."),
            item(id: "SURV_ARTIST_BILLIE_EILISH", title: "Billie Eilish", source: .appleMusicDerived, objective: .testAdjacentRoad, rationale: "Modern dark pop edge."),
            item(id: "SURV_ARTIST_OLIVIA_RODRIGO", title: "Olivia Rodrigo", source: .appleMusicDerived, objective: .calibrateBroadly, rationale: "Modern pop-rock overlap."),
            item(id: "SURV_ARTIST_BRUCE_SPRINGSTEEN", title: "Bruce Springsteen", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Heartland canon calibration."),
            item(id: "SURV_ARTIST_KATE_BUSH", title: "Kate Bush", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Theatrical art-pop appetite."),
            item(id: "SURV_ARTIST_DAFT_PUNK", title: "Daft Punk", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Electronic/pop body calibration.")
        ]
    }

    private static func adjacentArtistPool(preferNoiseRoad: Bool = false) -> [SurveyItem] {
        let items = [
            item(id: "SURV_ARTIST_HUSKER_DU", title: "Husker Du", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Melodic-noise prehistory."),
            item(id: "SURV_ARTIST_DINOSAUR_JR", title: "Dinosaur Jr.", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Guitar haze and hooks."),
            item(id: "SURV_ARTIST_JESUS_AND_MARY_CHAIN", title: "The Jesus and Mary Chain", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Noise-pop sweetness/abrasion."),
            item(id: "SURV_ARTIST_FUGAZI", title: "Fugazi", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Discipline and pressure."),
            item(id: "SURV_ARTIST_MUDHONEY", title: "Mudhoney", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Crud and proto-grunge tolerance."),
            item(id: "SURV_ARTIST_INTERPOL", title: "Interpol", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Dark modern post-punk lane."),
            item(id: "SURV_ARTIST_IDLES", title: "IDLES", source: .responseAdjacent, objective: .checkDeadEnd, rationale: "Pressure versus sloganeering."),
            item(id: "SURV_ARTIST_MITSKI", title: "Mitski", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Compressed emotional songwriting."),
            item(id: "SURV_ARTIST_YEAH_YEAH_YEAHS", title: "Yeah Yeah Yeahs", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Female rupture and bite."),
            item(id: "SURV_ARTIST_PJ_HARVEY", title: "PJ Harvey", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Hard persona and pressure.")
        ]

        return preferNoiseRoad ? items : Array(items.dropFirst(5)) + Array(items.prefix(5))
    }

    private static func sleeperPool() -> [SurveyItem] {
        [
            item(id: "SURV_ARTIST_SOLO_ANSAMBLIS", title: "Solo Ansamblis", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Lithuanian dark-post-punk lane."),
            item(id: "SURV_ARTIST_SHISHI", title: "shishi", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Female garage/post-punk wildcard."),
            item(id: "SURV_ARTIST_BIG_THIEF", title: "Big Thief", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Modern album-world with folk risk."),
            item(id: "SURV_ARTIST_BLACK_COUNTRY_NEW_ROAD", title: "Black Country, New Road", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Album-world pressure or art-school risk."),
            item(id: "SURV_ARTIST_WET_LEG", title: "Wet Leg", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Fun/novelty edge check."),
            item(id: "SURV_ARTIST_PROTOMARTYR", title: "Protomartyr", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Modern bleak post-punk pressure."),
            item(id: "SURV_ARTIST_JAPANESE_BREAKFAST", title: "Japanese Breakfast", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Melody/softness boundary."),
            item(id: "SURV_ARTIST_WEDNESDAY", title: "Wednesday", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Current guitar-band frontier.")
        ]
    }

    private static func rejectionPool() -> [SurveyItem] {
        [
            item(id: "SURV_ARTIST_COLDPLAY", title: "Coldplay", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Adult-alternative softness control."),
            item(id: "SURV_ARTIST_IMAGINE_DRAGONS", title: "Imagine Dragons", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Fake hard-rock/pop bombast control."),
            item(id: "SURV_ARTIST_MAROON_5", title: "Maroon 5", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Polished pop-rock dead-end check."),
            item(id: "SURV_ARTIST_MUMFORD_AND_SONS", title: "Mumford & Sons", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Soft folk stomp risk."),
            item(id: "SURV_ARTIST_TRAIN", title: "Train", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Mush calibration."),
            item(id: "SURV_ARTIST_THE_LUMINEERS", title: "The Lumineers", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Tasteful folk boundary."),
            item(id: "SURV_ARTIST_NICKELBACK", title: "Nickelback", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Fake hard rock control.")
        ]
    }

    private static func calibrationPool() -> [SurveyItem] {
        [
            item(id: "SURV_ARTIST_BOB_DYLAN", title: "Bob Dylan", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Songwriter/canon calibration."),
            item(id: "SURV_ARTIST_ARETHA_FRANKLIN", title: "Aretha Franklin", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Soul canon calibration."),
            item(id: "SURV_ARTIST_KENDRICK_LAMAR", title: "Kendrick Lamar", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Modern rap/art-world calibration."),
            item(id: "SURV_ARTIST_DAFT_PUNK", title: "Daft Punk", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Electronic/pop body calibration."),
            item(id: "SURV_ARTIST_METALLICA", title: "Metallica", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Heavy music boundary.")
        ]
    }

    private static func appleMusicLooseEndPool() -> [SurveyItem] {
        [
            item(id: "SURV_ARTIST_THE_REPLACEMENTS", title: "The Replacements", source: .appleMusicLooseEnd, objective: .testAdjacentRoad, rationale: "College-rock looseness or useful waypoint."),
            item(id: "SURV_ARTIST_MEAT_PUPPETS", title: "Meat Puppets", source: .appleMusicLooseEnd, objective: .testAdjacentRoad, rationale: "Nirvana-adjacent source-code check."),
            item(id: "SURV_ARTIST_SOCIAL_DISTORTION", title: "Social Distortion", source: .appleMusicLooseEnd, objective: .testAdjacentRoad, rationale: "Song-bearing punk pressure."),
            item(id: "SURV_ARTIST_THE_SMITHS", title: "The Smiths", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Melody, voice, and persona conflict."),
            item(id: "SURV_ARTIST_ARCADE_FIRE", title: "Arcade Fire", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Album-world versus earnestness."),
            item(id: "SURV_ARTIST_ST_VINCENT", title: "St. Vincent", source: .appleMusicLooseEnd, objective: .confirmLikelyRegion, rationale: "Art-pop guitar/persona check."),
            item(id: "SURV_ARTIST_QUEENS_OF_THE_STONE_AGE", title: "Queens of the Stone Age", source: .appleMusicLooseEnd, objective: .confirmLikelyRegion, rationale: "Hard groove and bite."),
            item(id: "SURV_ARTIST_TAME_IMPALA", title: "Tame Impala", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Psych-pop pressure versus softness."),
            item(id: "SURV_ARTIST_THE_NATIONAL", title: "The National", source: .appleMusicLooseEnd, objective: .checkDeadEnd, rationale: "Moody adult-indie boundary.")
        ]
    }

    private static func albumBasePool() -> [SurveyItem] {
        [
            item(id: "SURV_ALBUM_NEVERMIND", kind: .album, title: "Nevermind", subtitle: "Nirvana", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Anchor album-world."),
            item(id: "SURV_ALBUM_OK_COMPUTER", kind: .album, title: "OK Computer", subtitle: "Radiohead", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Album-world gravity."),
            item(id: "SURV_ALBUM_RUMOURS", kind: .album, title: "Rumours", subtitle: "Fleetwood Mac", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Song/album distinction."),
            item(id: "SURV_ALBUM_ZIGGY", kind: .album, title: "Ziggy Stardust", subtitle: "David Bowie", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Theatrical album-world."),
            item(id: "SURV_ALBUM_DUMMY", kind: .album, title: "Dummy", subtitle: "Portishead", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Dark atmosphere with hooks."),
            item(id: "SURV_ALBUM_DISINTEGRATION", kind: .album, title: "Disintegration", subtitle: "The Cure", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Dark melody album-world."),
            item(id: "SURV_ALBUM_DAYDREAM_NATION", kind: .album, title: "Daydream Nation", subtitle: "Sonic Youth", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Noise-rock object specificity."),
            item(id: "SURV_ALBUM_ZEN_ARCADE", kind: .album, title: "Zen Arcade", subtitle: "Husker Du", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Melody-blur album test."),
            item(id: "SURV_ALBUM_LOVE_FOREVER_CHANGES", kind: .album, title: "Forever Changes", subtitle: "Love", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Psych-pop album-world."),
            item(id: "SURV_ALBUM_BLUE", kind: .album, title: "Blue", subtitle: "Joni Mitchell", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Singer-songwriter calibration."),
            item(id: "SURV_ALBUM_FUNERAL", kind: .album, title: "Funeral", subtitle: "Arcade Fire", source: .objectSpecific, objective: .resolveContradiction, rationale: "Earnestness versus album force."),
            item(id: "SURV_ALBUM_1989", kind: .album, title: "1989", subtitle: "Taylor Swift", source: .objectSpecific, objective: .separateObjectTaste, rationale: "Pop songcraft/persona check."),
            item(id: "SURV_ALBUM_CHANNEL_ORANGE", kind: .album, title: "Channel Orange", subtitle: "Frank Ocean", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Modern R&B/songcraft calibration."),
            item(id: "SURV_ALBUM_SONGS_FOR_DEAF", kind: .album, title: "Songs for the Deaf", subtitle: "Queens of the Stone Age", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Hard groove album test."),
            item(id: "SURV_ALBUM_IN_RAINBOWS", kind: .album, title: "In Rainbows", subtitle: "Radiohead", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Warm album-world comparison."),
            item(id: "SURV_ALBUM_AEROPLANE", kind: .album, title: "In the Aeroplane Over the Sea", subtitle: "Neutral Milk Hotel", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Elephant Six sincerity/bite risk."),
            item(id: "SURV_ALBUM_PUNISHER", kind: .album, title: "Punisher", subtitle: "Phoebe Bridgers", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Soft modern songwriting boundary."),
            item(id: "SURV_ALBUM_VIVA_LA_VIDA", kind: .album, title: "Viva la Vida", subtitle: "Coldplay", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Big tasteful pop-rock risk."),
            item(id: "SURV_ALBUM_ROBOXAI", kind: .album, title: "Roboxai", subtitle: "Solo Ansamblis", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Lithuanian dark machine album-world."),
            item(id: "SURV_ALBUM_AFTER_LAUGHTER", kind: .album, title: "After Laughter", subtitle: "Paramore", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Pop shell with emotional pressure.")
        ]
    }

    private static func songBasePool() -> [SurveyItem] {
        [
            item(id: "SURV_SONG_SMELLS_LIKE_TEEN_SPIRIT", kind: .song, title: "Smells Like Teen Spirit", subtitle: "Nirvana", source: .appleMusicDerived, objective: .recognizeKnownTerritory, rationale: "Anchor song."),
            item(id: "SURV_SONG_DREAMS", kind: .song, title: "Dreams", subtitle: "Fleetwood Mac", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Song-specific attachment."),
            item(id: "SURV_SONG_BILLIE_JEAN", kind: .song, title: "Billie Jean", subtitle: "Michael Jackson", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Pop body calibration."),
            item(id: "SURV_SONG_MAPS", kind: .song, title: "Maps", subtitle: "Yeah Yeah Yeahs", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Female rupture plus melody."),
            item(id: "SURV_SONG_LOSER", kind: .song, title: "Loser", subtitle: "Beck", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Novelty versus real appetite."),
            item(id: "SURV_SONG_PINK_TURNS_BLUE", kind: .song, title: "Pink Turns to Blue", subtitle: "Husker Du", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Melodic wound in blur."),
            item(id: "SURV_SONG_JUST_LIKE_HEAVEN", kind: .song, title: "Just Like Heaven", subtitle: "The Cure", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Bright dark melody."),
            item(id: "SURV_SONG_BAD_GUY", kind: .song, title: "bad guy", subtitle: "Billie Eilish", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Modern pop bite."),
            item(id: "SURV_SONG_MR_BRIGHTSIDE", kind: .song, title: "Mr. Brightside", subtitle: "The Killers", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Cultural furniture or craving."),
            item(id: "SURV_SONG_SEVEN_NATION_ARMY", kind: .song, title: "Seven Nation Army", subtitle: "The White Stripes", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Minimal rock force."),
            item(id: "SURV_SONG_FAST_CAR", kind: .song, title: "Fast Car", subtitle: "Tracy Chapman", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Songwriter emotional directness."),
            item(id: "SURV_SONG_TRIPPY_LOVE", kind: .song, title: "Trippy Love", subtitle: "Garbanotas", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Baltic psych-pop check."),
            item(id: "SURV_SONG_NETILDAI", kind: .song, title: "Netildai", subtitle: "Solo Ansamblis", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Dark Baltic machine."),
            item(id: "SURV_SONG_SENTIMENTAI", kind: .song, title: "Sentimentai", subtitle: "Monika Liu", source: .sleeperProbe, objective: .checkDeadEnd, rationale: "Persona-pop/cabaret risk."),
            item(id: "SURV_SONG_YELLOW", kind: .song, title: "Yellow", subtitle: "Coldplay", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Soft anthem boundary."),
            item(id: "SURV_SONG_RADIOACTIVE", kind: .song, title: "Radioactive", subtitle: "Imagine Dragons", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Fake-hard pop control."),
            item(id: "SURV_SONG_HEY_SOUL_SISTER", kind: .song, title: "Hey, Soul Sister", subtitle: "Train", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Mush control."),
            item(id: "SURV_SONG_THIS_IS_THE_DAY", kind: .song, title: "This Is the Day", subtitle: "The The", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "80s emotional pop/post-punk bridge."),
            item(id: "SURV_SONG_SWEET_JANE", kind: .song, title: "Sweet Jane", subtitle: "The Velvet Underground", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Source-code rock appetite."),
            item(id: "SURV_SONG_HARD_TIMES", kind: .song, title: "Hard Times", subtitle: "Paramore", source: .sleeperProbe, objective: .probeSleeperFrontier, rationale: "Pop brightness over hurt.")
        ]
    }

    private static func albumExpansionPool() -> [SurveyItem] {
        [
            item(id: "SURV_ALBUM_EXILE_MAIN_ST", kind: .album, title: "Exile on Main St.", subtitle: "The Rolling Stones", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Loose classic-rock sprawl tolerance."),
            item(id: "SURV_ALBUM_MARQUEE_MOON", kind: .album, title: "Marquee Moon", subtitle: "Television", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Art-rock guitar architecture."),
            item(id: "SURV_ALBUM_PINKERTON", kind: .album, title: "Pinkerton", subtitle: "Weezer", source: .responseAdjacent, objective: .resolveContradiction, rationale: "Crunch, neediness, and songcraft boundary."),
            item(id: "SURV_ALBUM_LONDON_CALLING", kind: .album, title: "London Calling", subtitle: "The Clash", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Punk breadth and canon appetite."),
            item(id: "SURV_ALBUM_IS_THIS_IT", kind: .album, title: "Is This It", subtitle: "The Strokes", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Cool guitar-pop versus active craving."),
            item(id: "SURV_ALBUM_YANKEE_FOXTROT", kind: .album, title: "Yankee Hotel Foxtrot", subtitle: "Wilco", source: .appleMusicLooseEnd, objective: .checkDeadEnd, rationale: "Tasteful alt-Americana boundary."),
            item(id: "SURV_ALBUM_UNKNOWN_PLEASURES", kind: .album, title: "Unknown Pleasures", subtitle: "Joy Division", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Post-punk source-code appetite."),
            item(id: "SURV_ALBUM_THE_BENDS", kind: .album, title: "The Bends", subtitle: "Radiohead", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Rock-song Radiohead versus album-world Radiohead."),
            item(id: "SURV_ALBUM_ELVIS_COSTELLO_MY_AIM", kind: .album, title: "My Aim Is True", subtitle: "Elvis Costello", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Smart hooks and voice boundary."),
            item(id: "SURV_ALBUM_FLEET_FOXES", kind: .album, title: "Fleet Foxes", subtitle: "Fleet Foxes", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Tasteful folk softness boundary.")
        ]
    }

    private static func songExpansionPool() -> [SurveyItem] {
        [
            item(id: "SURV_SONG_ONCE", kind: .song, title: "Once", subtitle: "Pearl Jam", source: .appleMusicLooseEnd, objective: .testAdjacentRoad, rationale: "Grunge force and voice boundary."),
            item(id: "SURV_SONG_DEBASER", kind: .song, title: "Debaser", subtitle: "Pixies", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Alt source-code bite."),
            item(id: "SURV_SONG_DISORDER", kind: .song, title: "Disorder", subtitle: "Joy Division", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Body plus gloom calibration."),
            item(id: "SURV_SONG_ALL_MY_FRIENDS", kind: .song, title: "All My Friends", subtitle: "LCD Soundsystem", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Repetition, ache, and release."),
            item(id: "SURV_SONG_COMMON_PEOPLE", kind: .song, title: "Common People", subtitle: "Pulp", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Theatrical pop bite."),
            item(id: "SURV_SONG_LAST_NITE", kind: .song, title: "Last Nite", subtitle: "The Strokes", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Cool revival rock appetite."),
            item(id: "SURV_SONG_BORN_TO_RUN", kind: .song, title: "Born to Run", subtitle: "Bruce Springsteen", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Heartland grandeur boundary."),
            item(id: "SURV_SONG_RUNNING_UP_THAT_HILL", kind: .song, title: "Running Up That Hill", subtitle: "Kate Bush", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Theatrical synth-pop force."),
            item(id: "SURV_SONG_SABOTAGE", kind: .song, title: "Sabotage", subtitle: "Beastie Boys", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Rap-rock energy without mush."),
            item(id: "SURV_SONG_1979", kind: .song, title: "1979", subtitle: "The Smashing Pumpkins", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Nostalgia, haze, and appetite."),
            item(id: "SURV_SONG_BITTER_SWEET_SYMPHONY", kind: .song, title: "Bitter Sweet Symphony", subtitle: "The Verve", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Cultural furniture versus craving."),
            item(id: "SURV_SONG_CREEP", kind: .song, title: "Creep", subtitle: "Radiohead", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Song exception versus artist appetite."),
            item(id: "SURV_SONG_WHERE_IS_MY_MIND", kind: .song, title: "Where Is My Mind?", subtitle: "Pixies", source: .responseAdjacent, objective: .testAdjacentRoad, rationale: "Melodic surreal source-code."),
            item(id: "SURV_SONG_FAKE_PLASTIC_TREES", kind: .song, title: "Fake Plastic Trees", subtitle: "Radiohead", source: .appleMusicDerived, objective: .separateObjectTaste, rationale: "Softness tolerance inside known artist."),
            item(id: "SURV_SONG_WAKE_UP", kind: .song, title: "Wake Up", subtitle: "Arcade Fire", source: .appleMusicLooseEnd, objective: .resolveContradiction, rationale: "Earnest anthem risk."),
            item(id: "SURV_SONG_NO_ONE_KNOWS", kind: .song, title: "No One Knows", subtitle: "Queens of the Stone Age", source: .responseAdjacent, objective: .confirmLikelyRegion, rationale: "Hard groove and bite."),
            item(id: "SURV_SONG_PAPER_PLANES", kind: .song, title: "Paper Planes", subtitle: "M.I.A.", source: .broadCalibration, objective: .calibrateBroadly, rationale: "Pop edge and novelty boundary."),
            item(id: "SURV_SONG_TEENAGE_DIRTBAG", kind: .song, title: "Teenage Dirtbag", subtitle: "Wheatus", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Novelty and nostalgia control."),
            item(id: "SURV_SONG_HO_HEY", kind: .song, title: "Ho Hey", subtitle: "The Lumineers", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Folk stomp boundary."),
            item(id: "SURV_SONG_SEX_ON_FIRE", kind: .song, title: "Sex on Fire", subtitle: "Kings of Leon", source: .rejectionProbe, objective: .checkDeadEnd, rationale: "Arena-rock heat versus mush.")
        ]
    }

    private static func advancedEraItems() -> [SurveyItem] {
        [
            item(id: "SURV_ADV_ERA_70S_BOWIE", title: "1970s Bowie", source: .advancedFilter, objective: .calibrateBroadly, rationale: "Theatrical rock era appetite."),
            item(id: "SURV_ADV_ERA_80S_POSTPUNK", title: "1980s post-punk", source: .advancedFilter, objective: .confirmLikelyRegion, rationale: "Dark melody era lane."),
            item(id: "SURV_ADV_ERA_90S_ALT", title: "1990s alternative", source: .advancedFilter, objective: .recognizeKnownTerritory, rationale: "Known territory refinement."),
            item(id: "SURV_ADV_ERA_00S_INDIE", title: "2000s indie", source: .advancedFilter, objective: .checkDeadEnd, rationale: "Tasteful indie risk."),
            item(id: "SURV_ADV_ERA_CURRENT_ROCK", title: "Current rock", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Modern frontier desire.")
        ] + adjacentArtistPool().prefixItems(15)
    }

    private static func advancedGenreItems() -> [SurveyItem] {
        [
            item(id: "SURV_ADV_GENRE_POSTPUNK", title: "Post-punk", source: .advancedFilter, objective: .confirmLikelyRegion, rationale: "Dark body/gloom genre."),
            item(id: "SURV_ADV_GENRE_POWER_POP", title: "Power pop", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Hook pressure check."),
            item(id: "SURV_ADV_GENRE_PSYCH_POP", title: "Psych-pop", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Psych bite versus softness."),
            item(id: "SURV_ADV_GENRE_ADULT_ALT", title: "Adult alternative", source: .advancedFilter, objective: .checkDeadEnd, rationale: "Mush boundary."),
            item(id: "SURV_ADV_GENRE_HARD_ROCK", title: "Hard rock", source: .advancedFilter, objective: .resolveContradiction, rationale: "Real force versus fake hard.")
        ] + calibrationPool() + rejectionPool()
    }

    private static func advancedCountryItems() -> [SurveyItem] {
        [
            item(id: "SURV_ADV_COUNTRY_LITHUANIA", title: "Lithuania", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Baltic discovery pocket."),
            item(id: "SURV_ADV_COUNTRY_UK", title: "United Kingdom", source: .advancedFilter, objective: .calibrateBroadly, rationale: "Post-punk and canon density."),
            item(id: "SURV_ADV_COUNTRY_US", title: "United States", source: .advancedFilter, objective: .recognizeKnownTerritory, rationale: "Known home territory."),
            item(id: "SURV_ADV_COUNTRY_AUSTRALIA", title: "Australia", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Modern rock/pop frontier."),
            item(id: "SURV_ADV_COUNTRY_CANADA", title: "Canada", source: .advancedFilter, objective: .resolveContradiction, rationale: "Indie/canon/earnestness boundary.")
        ] + sleeperPool() + appleMusicLooseEndPool()
    }

    private static func advancedSceneItems() -> [SurveyItem] {
        [
            item(id: "SURV_ADV_SCENE_SEATTLE", title: "Seattle source-code", source: .advancedFilter, objective: .recognizeKnownTerritory, rationale: "Nirvana-adjacent scene."),
            item(id: "SURV_ADV_SCENE_DC_HARDCORE", title: "D.C. hardcore", source: .advancedFilter, objective: .testAdjacentRoad, rationale: "Discipline versus too-hard boundary."),
            item(id: "SURV_ADV_SCENE_ELEPHANT6", title: "Elephant 6", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Psych-pop/sincerity risk."),
            item(id: "SURV_ADV_SCENE_BALTIC_DARK", title: "Baltic dark pop", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Regional atmosphere frontier.")
        ] + adjacentArtistPool() + sleeperPool()
    }

    private static func advancedPopularityItems() -> [SurveyItem] {
        [
            item(id: "SURV_ADV_POP_MAINSTREAM", title: "Mainstream hits", source: .advancedFilter, objective: .calibrateBroadly, rationale: "Popularity tolerance."),
            item(id: "SURV_ADV_POP_CULT", title: "Cult favorites", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Cult appetite."),
            item(id: "SURV_ADV_POP_DEEP_CUTS", title: "Deep cuts", source: .advancedFilter, objective: .probeSleeperFrontier, rationale: "Exploration depth."),
            item(id: "SURV_ADV_POP_ALBUM_TRACKS", title: "Album tracks", source: .advancedFilter, objective: .separateObjectTaste, rationale: "Album-world versus singles.")
        ] + calibrationPool() + sleeperPool() + rejectionPool()
    }

    private static func item(
        id: String,
        kind: SurveyItemKind = .artist,
        title: String,
        subtitle: String? = nil,
        artworkURL: URL? = nil,
        source: SurveyItemSource,
        objective: SurveyBatchObjective,
        rationale: String
    ) -> SurveyItem {
        SurveyItem(
            id: id,
            kind: kind,
            title: title,
            subtitle: subtitle,
            artworkURL: artworkURL,
            source: source,
            objective: objective,
            rationale: rationale,
            artworkSeed: title
        )
    }

    private static func unique(_ items: [SurveyItem]) -> [SurveyItem] {
        var seen = Set<String>()
        var output: [SurveyItem] = []
        for item in items where !seen.contains(item.id) {
            seen.insert(item.id)
            output.append(item)
        }
        return output
    }

    private static func rotated(_ items: [SurveyItem], offset: Int) -> [SurveyItem] {
        guard !items.isEmpty else {
            return []
        }

        let normalizedOffset = offset % items.count
        return Array(items.dropFirst(normalizedOffset)) + Array(items.prefix(normalizedOffset))
    }
}

private extension Array where Element == SurveyItem {
    func prefixItems(_ maxLength: Int) -> [SurveyItem] {
        Array(prefix(maxLength))
    }
}

private extension ArraySlice where Element == SurveyItem {
    func prefixItems(_ maxLength: Int) -> [SurveyItem] {
        Array(prefix(maxLength))
    }
}
