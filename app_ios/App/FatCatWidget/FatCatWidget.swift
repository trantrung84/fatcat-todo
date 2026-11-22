import WidgetKit
import SwiftUI

// Payload written by the app (WidgetBridgePlugin.update) into the shared App Group.
struct WItem: Decodable { let t: String; let d: Bool }
struct WDay: Decodable { let label: String?; let total: Int?; let done: Int?; let items: [WItem]? }
struct WPayload: Decodable { let emptyText: String?; let openText: String?; let accent: String?; let days: [String: WDay]? }

struct CatEntry: TimelineEntry {
    let date: Date
    let payload: WPayload?
}

enum Store {
    static let group = "group.com.fatcat.todo"
    static func load() -> WPayload? {
        guard let raw = UserDefaults(suiteName: group)?.string(forKey: "data"),
              let data = raw.data(using: .utf8) else { return nil }
        return try? JSONDecoder().decode(WPayload.self, from: data)
    }
    static func key(_ d: Date) -> String {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = .current
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: d)
    }
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> CatEntry { CatEntry(date: Date(), payload: Provider.sample) }
    func getSnapshot(in context: Context, completion: @escaping (CatEntry) -> Void) {
        completion(CatEntry(date: Date(), payload: Store.load() ?? Provider.sample))
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<CatEntry>) -> Void) {
        let p = Store.load()
        let cal = Calendar.current
        var entries = [CatEntry(date: Date(), payload: p)]
        // The payload covers 7 days, so pre-schedule one entry per midnight.
        var day = cal.startOfDay(for: Date())
        for _ in 0..<6 {
            day = cal.date(byAdding: .day, value: 1, to: day)!
            entries.append(CatEntry(date: day, payload: p))
        }
        completion(Timeline(entries: entries, policy: .after(day)))
    }
    static let sample = WPayload(emptyText: nil, openText: nil, accent: "#B8493A", days: [
        Store.key(Date()): WDay(label: nil, total: 3, done: 1, items: [
            WItem(t: "Buy milk and fruit", d: false), WItem(t: "Send weekly report", d: false), WItem(t: "Yoga for 20 minutes", d: true)])
    ])
}

extension Color {
    init(hex: String) {
        var s = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if s.hasPrefix("#") { s.removeFirst() }
        var v: UInt64 = 0
        Scanner(string: s).scanHexInt64(&v)
        self.init(.sRGB, red: Double((v >> 16) & 0xFF) / 255, green: Double((v >> 8) & 0xFF) / 255, blue: Double(v & 0xFF) / 255, opacity: 1)
    }
}

struct CatWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: CatEntry

    private let ink = Color(hex: "#4A2C24")
    private let muted = Color(hex: "#9A7F75")
    static let bg = Color(hex: "#FFF6F0")

    var body: some View {
        let day = entry.payload?.days?[Store.key(entry.date)]
        let accent = Color(hex: entry.payload?.accent ?? "#B8493A")
        let items = day?.items ?? []
        let maxRows = family == .systemSmall ? 3 : 5
        let title = day?.label ?? entry.date.formatted(.dateTime.weekday(.abbreviated).day().month(.abbreviated))
        let total = day?.total ?? 0, done = day?.done ?? 0

        ZStack(alignment: .bottomTrailing) {
            VStack(alignment: .leading, spacing: family == .systemSmall ? 4 : 5) {
                HStack {
                    Text(title).font(.system(size: family == .systemSmall ? 13 : 15, weight: .heavy, design: .rounded))
                        .foregroundColor(ink).lineLimit(1)
                    Spacer(minLength: 4)
                    if total > 0 {
                        Text("\(done)/\(total)").font(.system(size: 13, weight: .heavy, design: .rounded)).foregroundColor(accent)
                    }
                }
                if items.isEmpty {
                    Spacer()
                    Text(day == nil ? (entry.payload?.openText ?? "Fat Cat Todo") : (entry.payload?.emptyText ?? ""))
                        .font(.system(size: 13, weight: .semibold, design: .rounded)).foregroundColor(muted)
                        .padding(.trailing, 40)
                    Spacer()
                } else {
                    ForEach(Array(items.prefix(maxRows).enumerated()), id: \.offset) { _, it in
                        HStack(spacing: 6) {
                            Image(systemName: it.d ? "checkmark.circle.fill" : "circle")
                                .font(.system(size: 13, weight: .bold))
                                .foregroundColor(it.d ? Color(hex: "#5DBB8A") : accent)
                            Text(it.t).font(.system(size: 13, weight: .semibold, design: .rounded))
                                .strikethrough(it.d).foregroundColor(it.d ? muted : ink).lineLimit(1)
                        }
                    }
                    Spacer(minLength: 0)
                }
            }
            Image("widget_cat").resizable().scaledToFit()
                .frame(width: family == .systemSmall ? 40 : 54)
                .offset(x: 4, y: 6)
        }
        .widgetBackground(CatWidgetView.bg)
    }
}

extension View {
    @ViewBuilder func widgetBackground(_ color: Color) -> some View {
        if #available(iOS 17.0, *) {
            self.containerBackground(color, for: .widget)
        } else {
            self.padding(14).background(color)
        }
    }
}

struct FatCatTodayWidget: Widget {
    let kind = "FatCatTodayWidget"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            CatWidgetView(entry: entry)
        }
        .configurationDisplayName("Fat Cat Todo")
        .description("Today's tasks at a glance.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main
struct FatCatWidgetBundle: WidgetBundle {
    var body: some Widget { FatCatTodayWidget() }
}
