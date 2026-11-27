import Foundation
import Capacitor
import WidgetKit
import StoreKit

/// Same JS interface as the Android WidgetBridgePlugin:
///   update({ data: string })  – stores the widget payload in the shared App Group and reloads widgets
///   appInfo()                 – { debug: Bool }
@objc(WidgetBridgePlugin)
public class WidgetBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "WidgetBridgePlugin"
    public let jsName = "WidgetBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "update", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "appInfo", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "requestReview", returnType: CAPPluginReturnPromise)
    ]

    static let appGroup = "group.com.fatcat.todo"
    static let key = "data"

    @objc func update(_ call: CAPPluginCall) {
        let data = call.getString("data") ?? "{}"
        UserDefaults(suiteName: WidgetBridgePlugin.appGroup)?.set(data, forKey: WidgetBridgePlugin.key)
        WidgetCenter.shared.reloadAllTimelines()
        call.resolve()
    }

    @objc func appInfo(_ call: CAPPluginCall) {
        #if DEBUG
        let debug = true
        #else
        let debug = false
        #endif
        call.resolve(["debug": debug, "platform": "ios"])
    }

    /// Asks iOS to show the system rating prompt. iOS limits it to 3 times per 365 days.
    @objc func requestReview(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            if let scene = UIApplication.shared.connectedScenes
                .first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene {
                SKStoreReviewController.requestReview(in: scene)
            }
            call.resolve()
        }
    }
}
