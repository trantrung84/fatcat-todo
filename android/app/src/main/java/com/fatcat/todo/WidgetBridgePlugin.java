package com.fatcat.todo;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;

/** Receives the next days' task snapshot from the web app and refreshes the home-screen widgets. */
@CapacitorPlugin(name = "WidgetBridge")
public class WidgetBridgePlugin extends Plugin {
    @PluginMethod
    public void update(PluginCall call) {
        String data = call.getString("data", "{}");
        Context ctx = getContext();
        ctx.getSharedPreferences(FatCatWidget.PREFS, Context.MODE_PRIVATE).edit().putString(FatCatWidget.KEY, data).apply();
        FatCatWidget.updateAll(ctx);
        call.resolve();
    }

    /** Lets the web layer know whether this is a debug (test) build. */
    @PluginMethod
    public void appInfo(PluginCall call) {
        JSObject o = new JSObject();
        o.put("debug", (getContext().getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);
        call.resolve(o);
    }

    /** Shows Google Play's in-app review sheet. Google decides whether it actually appears (quota). */
    @PluginMethod
    public void requestReview(PluginCall call) {
        if (getActivity() == null) { call.resolve(); return; }
        ReviewManager rm = ReviewManagerFactory.create(getContext());
        rm.requestReviewFlow().addOnCompleteListener(task -> {
            if (!task.isSuccessful()) { call.resolve(); return; }
            ReviewInfo info = task.getResult();
            rm.launchReviewFlow(getActivity(), info).addOnCompleteListener(t -> call.resolve());
        });
    }
}
