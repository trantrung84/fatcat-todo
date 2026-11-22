import UIKit
import Capacitor

/// Bridge view controller that registers Fat Cat Todo's own native plugins
/// (they live in the app target, so Capacitor does not discover them automatically).
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(BillingPlugin())
        bridge?.registerPluginInstance(WidgetBridgePlugin())
    }
}
