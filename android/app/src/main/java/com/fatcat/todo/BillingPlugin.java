package com.fatcat.todo;

import android.util.Log;
import androidx.annotation.NonNull;
import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.PurchasesUpdatedListener;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Google Play Billing for Fat Cat Pro.
 * Products (create them in Play Console with exactly these IDs):
 *   fatcat_pro_monthly  – subscription (base plan, auto-renewing monthly)
 *   fatcat_pro_yearly   – subscription (base plan, auto-renewing yearly)
 *   fatcat_pro_lifetime – one-time in-app product (non-consumable)
 */
@CapacitorPlugin(name = "Billing")
public class BillingPlugin extends Plugin implements PurchasesUpdatedListener {
    private static final String TAG = "FatCatBilling";
    static final String MONTHLY = "fatcat_pro_monthly";
    static final String YEARLY = "fatcat_pro_yearly";
    static final String LIFETIME = "fatcat_pro_lifetime";

    private BillingClient client;
    private final Map<String, ProductDetails> details = new HashMap<>();
    private PluginCall pendingPurchase;

    @Override
    public void load() {
        client = BillingClient.newBuilder(getContext())
            .setListener(this)
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .enableAutoServiceReconnection()
            .build();
    }

    private interface Ready { void run(); }

    private void ensureConnected(PluginCall call, Ready r) {
        if (client.isReady()) { r.run(); return; }
        client.startConnection(new BillingClientStateListener() {
            @Override public void onBillingSetupFinished(@NonNull BillingResult res) {
                if (res.getResponseCode() == BillingClient.BillingResponseCode.OK) r.run();
                else call.reject("Billing unavailable: " + res.getDebugMessage(), String.valueOf(res.getResponseCode()));
            }
            @Override public void onBillingServiceDisconnected() { Log.w(TAG, "disconnected"); }
        });
    }

    /** Returns localized prices for the three Pro products. */
    @PluginMethod
    public void getProducts(PluginCall call) {
        ensureConnected(call, () -> {
            final JSObject out = new JSObject();
            final int[] pending = {2};
            Runnable done = () -> { synchronized (pending) { if (--pending[0] == 0) call.resolve(out); } };
            query(BillingClient.ProductType.SUBS, java.util.Arrays.asList(MONTHLY, YEARLY), out, done);
            query(BillingClient.ProductType.INAPP, Collections.singletonList(LIFETIME), out, done);
        });
    }

    private void query(String type, List<String> ids, JSObject out, Runnable done) {
        List<QueryProductDetailsParams.Product> list = new ArrayList<>();
        for (String id : ids) list.add(QueryProductDetailsParams.Product.newBuilder().setProductId(id).setProductType(type).build());
        client.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(list).build(), (res, result) -> {
            List<ProductDetails> pds = result.getProductDetailsList();
            if (pds != null) for (ProductDetails pd : pds) {
                details.put(pd.getProductId(), pd);
                JSObject p = new JSObject();
                p.put("id", pd.getProductId());
                p.put("title", pd.getName());
                if (BillingClient.ProductType.SUBS.equals(pd.getProductType())) {
                    List<ProductDetails.SubscriptionOfferDetails> offers = pd.getSubscriptionOfferDetails();
                    if (offers != null && !offers.isEmpty()) {
                        List<ProductDetails.PricingPhase> phases = offers.get(0).getPricingPhases().getPricingPhaseList();
                        ProductDetails.PricingPhase base = phases.get(phases.size() - 1);
                        p.put("price", base.getFormattedPrice());
                        p.put("micros", base.getPriceAmountMicros());
                        p.put("currency", base.getPriceCurrencyCode());
                    }
                } else if (pd.getOneTimePurchaseOfferDetails() != null) {
                    p.put("price", pd.getOneTimePurchaseOfferDetails().getFormattedPrice());
                    p.put("micros", pd.getOneTimePurchaseOfferDetails().getPriceAmountMicros());
                    p.put("currency", pd.getOneTimePurchaseOfferDetails().getPriceCurrencyCode());
                }
                out.put(pd.getProductId(), p);
            }
            done.run();
        });
    }

    @PluginMethod
    public void purchase(PluginCall call) {
        String id = call.getString("productId");
        ensureConnected(call, () -> {
            ProductDetails pd = details.get(id);
            if (pd == null) { call.reject("Product not loaded: " + id); return; }
            BillingFlowParams.ProductDetailsParams.Builder b = BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(pd);
            if (BillingClient.ProductType.SUBS.equals(pd.getProductType())) {
                List<ProductDetails.SubscriptionOfferDetails> offers = pd.getSubscriptionOfferDetails();
                if (offers == null || offers.isEmpty()) { call.reject("No offer for " + id); return; }
                b.setOfferToken(offers.get(0).getOfferToken());
            }
            BillingFlowParams flow = BillingFlowParams.newBuilder().setProductDetailsParamsList(Collections.singletonList(b.build())).build();
            pendingPurchase = call;
            call.setKeepAlive(true);
            getActivity().runOnUiThread(() -> {
                BillingResult r = client.launchBillingFlow(getActivity(), flow);
                if (r.getResponseCode() != BillingClient.BillingResponseCode.OK) finishPurchase(null, "error", r.getDebugMessage());
            });
        });
    }

    @Override
    public void onPurchasesUpdated(@NonNull BillingResult res, List<Purchase> purchases) {
        int code = res.getResponseCode();
        if (code == BillingClient.BillingResponseCode.OK && purchases != null) {
            String state = "pending";
            String product = null;
            for (Purchase p : purchases) {
                if (p.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                    acknowledge(p);
                    state = "purchased";
                    product = p.getProducts().isEmpty() ? null : p.getProducts().get(0);
                }
            }
            finishPurchase(product, state, null);
        } else if (code == BillingClient.BillingResponseCode.USER_CANCELED) {
            finishPurchase(null, "cancelled", null);
        } else if (code == BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED) {
            finishPurchase(null, "owned", null);
        } else {
            finishPurchase(null, "error", res.getDebugMessage());
        }
    }

    private void finishPurchase(String product, String state, String message) {
        JSObject o = new JSObject();
        o.put("status", state);
        if (product != null) o.put("productId", product);
        if (message != null) o.put("message", message);
        notifyListeners("purchaseUpdated", o);
        if (pendingPurchase != null) {
            pendingPurchase.resolve(o);
            pendingPurchase.setKeepAlive(false);
            getBridge().releaseCall(pendingPurchase);
            pendingPurchase = null;
        }
    }

    private void acknowledge(Purchase p) {
        if (p.isAcknowledged()) return;
        client.acknowledgePurchase(AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.getPurchaseToken()).build(),
            r -> Log.i(TAG, "acknowledge " + r.getResponseCode()));
    }

    /** Checks active subscriptions and the lifetime purchase. Use for app start and "Restore purchases". */
    @PluginMethod
    public void getEntitlement(PluginCall call) {
        ensureConnected(call, () -> {
            final JSArray owned = new JSArray();
            final int[] pending = {2};
            final boolean[] pro = {false};
            Runnable done = () -> { synchronized (pending) { if (--pending[0] == 0) {
                JSObject o = new JSObject(); o.put("pro", pro[0]); o.put("products", owned); call.resolve(o); } } };
            for (String type : new String[]{BillingClient.ProductType.SUBS, BillingClient.ProductType.INAPP}) {
                client.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(type).build(), (res, list) -> {
                    if (list != null) for (Purchase p : list) {
                        if (p.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                            acknowledge(p);
                            for (String id : p.getProducts()) {
                                if (id.equals(MONTHLY) || id.equals(YEARLY) || id.equals(LIFETIME)) { pro[0] = true; owned.put(id); }
                            }
                        }
                    }
                    done.run();
                });
            }
        });
    }
}
