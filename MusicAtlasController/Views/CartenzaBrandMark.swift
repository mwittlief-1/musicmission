import SwiftUI

enum CartenzaBrand {
    static let name = "Cartenza"
    static let tagline = "Your music. Mapped."

    static let obsidian = Color(red: 0.027, green: 0.031, blue: 0.039)
    static let charcoal = Color(red: 0.055, green: 0.059, blue: 0.071)
    static let graphite = Color(red: 0.090, green: 0.102, blue: 0.118)
    static let slate = Color(red: 0.137, green: 0.153, blue: 0.169)
    static let ash = Color(red: 0.486, green: 0.510, blue: 0.541)
    static let silver = Color(red: 0.749, green: 0.765, blue: 0.788)
    static let warmSilver = Color(red: 0.831, green: 0.816, blue: 0.780)
    static let antiqueGold = Color(red: 0.710, green: 0.604, blue: 0.380)
    static let dimGold = Color(red: 0.561, green: 0.459, blue: 0.275)
    static let mutedTeal = Color(red: 0.247, green: 0.412, blue: 0.400)
    static let tealMist = Color(red: 0.561, green: 0.647, blue: 0.604)
    static let dangerLow = Color(red: 0.478, green: 0.306, blue: 0.282)
}

enum CartenzaTheme {
    static let background = CartenzaBrand.obsidian
    static let panel = CartenzaBrand.graphite
    static let raisedPanel = CartenzaBrand.slate
    static let line = Color(red: 0.169, green: 0.188, blue: 0.208).opacity(0.86)
    static let text = CartenzaBrand.warmSilver
    static let mutedText = CartenzaBrand.silver.opacity(0.72)
    static let route = CartenzaBrand.mutedTeal
    static let signal = CartenzaBrand.antiqueGold
    static let waypoint = CartenzaBrand.dimGold
    static let positive = Color(red: 0.486, green: 0.650, blue: 0.427)
    static let negative = CartenzaBrand.dangerLow
    static let radius: CGFloat = 18
    static let smallRadius: CGFloat = 10
}

typealias WaymarkTheme = CartenzaTheme

struct CartenzaBrandLockup: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            CartenzaCompassMark(size: 78)

            VStack(alignment: .leading, spacing: 3) {
                Text(CartenzaBrand.name)
                    .font(.system(size: 38, weight: .semibold, design: .serif))
                    .foregroundStyle(CartenzaTheme.text)
                    .fixedSize(horizontal: false, vertical: true)

                Text(CartenzaBrand.tagline)
                    .font(.caption.weight(.semibold))
                    .tracking(1.1)
                    .foregroundStyle(CartenzaTheme.signal)
                    .textCase(.uppercase)
            }
        }
        .accessibilityElement(children: .combine)
    }
}

struct CartenzaCompassMark: View {
    var size: CGFloat = 68
    var systemImage: String?
    var tint: Color = CartenzaTheme.signal

    var body: some View {
        ZStack {
            Circle()
                .fill(CartenzaBrand.charcoal)
            Circle()
                .stroke(CartenzaTheme.line, lineWidth: 1)

            if let systemImage {
                CartenzaSealGrid(size: size, tint: tint)
                Image(systemName: systemImage)
                    .font(.system(size: size * 0.34, weight: .semibold))
                    .foregroundStyle(tint)
            } else {
                CartenzaCartographicCut(size: size)
            }
        }
        .frame(width: size, height: size)
        .shadow(color: tint.opacity(0.16), radius: 18, x: 0, y: 8)
    }
}

private struct CartenzaSealGrid: View {
    let size: CGFloat
    let tint: Color

    var body: some View {
        ZStack {
            Circle()
                .stroke(tint.opacity(0.32), lineWidth: 1)
                .padding(size * 0.14)

            Path { path in
                let center = CGPoint(x: size / 2, y: size / 2)
                path.move(to: CGPoint(x: center.x, y: size * 0.16))
                path.addLine(to: CGPoint(x: center.x, y: size * 0.84))
                path.move(to: CGPoint(x: size * 0.16, y: center.y))
                path.addLine(to: CGPoint(x: size * 0.84, y: center.y))
            }
            .stroke(tint.opacity(0.20), lineWidth: 1)
        }
    }
}

private struct CartenzaCartographicCut: View {
    let size: CGFloat

    var body: some View {
        ZStack {
            Circle()
                .stroke(CartenzaBrand.slate.opacity(0.9), lineWidth: max(1, size * 0.055))
                .padding(size * 0.10)

            Circle()
                .stroke(CartenzaBrand.mutedTeal.opacity(0.58), lineWidth: max(1, size * 0.018))
                .padding(size * 0.22)

            Path { path in
                let center = CGPoint(x: size / 2, y: size / 2)
                path.move(to: CGPoint(x: center.x, y: size * 0.18))
                path.addLine(to: CGPoint(x: center.x, y: size * 0.82))
                path.move(to: CGPoint(x: size * 0.18, y: center.y))
                path.addLine(to: CGPoint(x: size * 0.82, y: center.y))
            }
            .stroke(CartenzaTheme.text.opacity(0.14), lineWidth: 1)

            Circle()
                .trim(from: 0.13, to: 0.87)
                .stroke(
                    LinearGradient(
                        colors: [CartenzaBrand.warmSilver, CartenzaBrand.silver, CartenzaBrand.ash],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    style: StrokeStyle(lineWidth: max(5, size * 0.18), lineCap: .round)
                )
                .rotationEffect(.degrees(92))
                .padding(size * 0.17)

            CartenzaContourCuts(size: size)

            CartenzaWaypointDot(size: size, x: 0.67, y: 0.28)
            CartenzaWaypointDot(size: size, x: 0.67, y: 0.72, opacity: 0.72)

            CartenzaSignalStar(size: size)
        }
    }
}

private struct CartenzaContourCuts: View {
    let size: CGFloat

    var body: some View {
        ZStack {
            Path { path in
                path.move(to: CGPoint(x: size * 0.24, y: size * 0.35))
                path.addCurve(
                    to: CGPoint(x: size * 0.63, y: size * 0.32),
                    control1: CGPoint(x: size * 0.36, y: size * 0.28),
                    control2: CGPoint(x: size * 0.50, y: size * 0.30)
                )
            }
            .stroke(CartenzaTheme.text.opacity(0.20), style: StrokeStyle(lineWidth: max(1, size * 0.025), lineCap: .round))

            Path { path in
                path.move(to: CGPoint(x: size * 0.24, y: size * 0.66))
                path.addCurve(
                    to: CGPoint(x: size * 0.66, y: size * 0.63),
                    control1: CGPoint(x: size * 0.38, y: size * 0.74),
                    control2: CGPoint(x: size * 0.52, y: size * 0.74)
                )
            }
            .stroke(CartenzaBrand.silver.opacity(0.18), style: StrokeStyle(lineWidth: max(1, size * 0.022), lineCap: .round))
        }
    }
}

private struct CartenzaWaypointDot: View {
    let size: CGFloat
    let x: CGFloat
    let y: CGFloat
    var opacity: Double = 1

    var body: some View {
        Circle()
            .fill(CartenzaBrand.antiqueGold.opacity(opacity))
            .frame(width: max(3, size * 0.10), height: max(3, size * 0.10))
            .position(x: size * x, y: size * y)
    }
}

private struct CartenzaSignalStar: View {
    let size: CGFloat

    var body: some View {
        Path { path in
            let center = CGPoint(x: size / 2, y: size / 2)
            let long = size * 0.15
            let short = size * 0.055

            path.move(to: CGPoint(x: center.x, y: center.y - long))
            path.addLine(to: CGPoint(x: center.x + short, y: center.y - short))
            path.addLine(to: CGPoint(x: center.x + long, y: center.y))
            path.addLine(to: CGPoint(x: center.x + short, y: center.y + short))
            path.addLine(to: CGPoint(x: center.x, y: center.y + long))
            path.addLine(to: CGPoint(x: center.x - short, y: center.y + short))
            path.addLine(to: CGPoint(x: center.x - long, y: center.y))
            path.addLine(to: CGPoint(x: center.x - short, y: center.y - short))
            path.closeSubpath()
        }
        .fill(CartenzaBrand.antiqueGold)
        .overlay(
            Circle()
                .fill(Color(red: 0.941, green: 0.835, blue: 0.541))
                .frame(width: max(2, size * 0.038), height: max(2, size * 0.038))
        )
    }
}
