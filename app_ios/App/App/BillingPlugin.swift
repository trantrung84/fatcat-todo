import Foundation
import Capacitor
import StoreKit

/// StoreKit 2 implementation of Fat Cat Pro with the same JS interface as the Android BillingPlugin.
/// Products (create them in App Store Connect with exactly these IDs):
///   fatcat_pro_monthly  – auto-renewable subscription (group "Fat Cat Pro"), 1 month
///   fatcat_pro_yearly   – auto-renewable subscription (same group), 1 year
///   fatcat_pro_lifetime – non-consumable
@objc(BillingPlugin)
public class BillingPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "BillingPlugin"
    public let jsName = "Billing"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "getProducts", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "purchase", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getEntitlement", returnType: CAPPluginReturnPromise)
    ]

    static let productIds = ["fatcat_pro_monthly", "fatcat_pro_yearly", "fatcat_pro_lifetime"]
    private var products: [String: Product] = [:]
    private var updates: Task<Void, Never>?

    override public func load() {
        // Finish transactions that arrive outside a purchase call (renewals, Ask to Buy, purchases on other devices).
        updates = Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let tx) = result { await tx.finish() }
                self?.notifyListeners("entitlementChanged", data: [:])
            }
        }
    }

    deinit { updates?.cancel() }

    private func loadProducts() async throws -> [Product] {
        let list = try await Product.products(for: BillingPlugin.productIds)
        for p in list { products[p.id] = p }
        return list
    }

    @objc func getProducts(_ call: CAPPluginCall) {
        Task {
            do {
                var out: [String: Any] = [:]
                for p in try await loadProducts() {
                    let micros = (p.price as NSDecimalNumber).multiplying(byPowerOf10: 6).int64Value
                    out[p.id] = [
                        "id": p.id,
                        "title": p.displayName,
                        "price": p.displayPrice,
                        "micros": micros,
                        "currency": p.priceFormatStyle.currencyCode
                    ]
                }
                call.resolve(out)
            } catch {
                call.reject("StoreKit products unavailable: \(error.localizedDescription)")
            }
        }
    }

    @objc func purchase(_ call: CAPPluginCall) {
        guard let id = call.getString("productId") else { call.reject("productId required"); return }
        Task {
            do {
                if products[id] == nil { _ = try await loadProducts() }
                guard let product = products[id] else { call.resolve(["status": "error", "message": "Product not found: \(id)"]); return }
                let result = try await product.purchase()
                switch result {
                case .success(let verification):
                    switch verification {
                    case .verified(let tx):
                        await tx.finish()
                        call.resolve(["status": "purchased", "product": tx.productID])
                    case .unverified(_, let err):
                        call.resolve(["status": "error", "message": "Unverified transaction: \(err.localizedDescription)"])
                    }
                case .userCancelled:
                    call.resolve(["status": "cancelled"])
                case .pending:
                    call.resolve(["status": "pending"])
                @unknown default:
                    call.resolve(["status": "error", "message": "Unknown purchase result"])
                }
            } catch {
                call.resolve(["status": "error", "message": error.localizedDescription])
            }
        }
    }

    /// getEntitlement({ sync?: boolean }) -> { pro: boolean, product?: string }
    /// sync = true is used by "Restore purchases" and asks the App Store to refresh (may prompt for Apple ID).
    @objc func getEntitlement(_ call: CAPPluginCall) {
        let sync = call.getBool("sync") ?? false
        Task {
            if sync { try? await AppStore.sync() }
            var active: String? = nil
            for await result in Transaction.currentEntitlements {
                guard case .verified(let tx) = result,
                      BillingPlugin.productIds.contains(tx.productID),
                      tx.revocationDate == nil else { continue }
                if let exp = tx.expirationDate, exp < Date() { continue }
                active = tx.productID
                if tx.productID == "fatcat_pro_lifetime" { break }
            }
            var out: [String: Any] = ["pro": active != nil]
            if let a = active { out["product"] = a }
            call.resolve(out)
        }
    }
}
