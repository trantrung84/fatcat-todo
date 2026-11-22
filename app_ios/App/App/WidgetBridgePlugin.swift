import Foundation
import Capacitor
import WidgetKit

/// Same JS interface as the Android WidgetBridgePlugin:
///   update({ data: string })  – stores the widget payload in the shared App Group and reloads widgets
///   appInfo()                 – { debug: Bool }
@objc(WidgetBridgePlugin)
public class WidgetBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "WidgetBridgePlugin"
    public let jsName = "WidgetBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "update", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "appInfo", returnType: CAPPluginReturnPromise)
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
}
