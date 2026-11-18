package com.fatcat.todo;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.StrikethroughSpan;
import android.view.View;
import android.widget.RemoteViews;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import org.json.JSONArray;
import org.json.JSONObject;

/** Large (4x2) "today" widget. FatCatWidgetSmall reuses this with a compact layout. */
public class FatCatWidget extends AppWidgetProvider {
    static final String PREFS = "fatcat_widget";
    static final String KEY = "data";
    static final int[] ROWS = {R.id.row0, R.id.row1, R.id.row2, R.id.row3, R.id.row4};
    static final int[] ICONS = {R.id.ic0, R.id.ic1, R.id.ic2, R.id.ic3, R.id.ic4};
    static final int[] TEXTS = {R.id.tx0, R.id.tx1, R.id.tx2, R.id.tx3, R.id.tx4};

    protected int layout() { return R.layout.widget_large; }
    protected int maxRows() { return 5; }

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) render(ctx, mgr, id, layout(), maxRows());
    }

    static void updateAll(Context ctx) {
        AppWidgetManager mgr = AppWidgetManager.getInstance(ctx);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, FatCatWidget.class)))
            render(ctx, mgr, id, R.layout.widget_large, 5);
        for (int id : mgr.getAppWidgetIds(new ComponentName(ctx, FatCatWidgetSmall.class)))
            render(ctx, mgr, id, R.layout.widget_small, 3);
    }

    static void render(Context ctx, AppWidgetManager mgr, int id, int layout, int maxRows) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), layout);
        String raw = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY, "{}");
        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date());
        int ink = Color.parseColor("#4A2C24");
        int accent = Color.parseColor("#B8493A");
        String title = new SimpleDateFormat("EEE, d/M", Locale.getDefault()).format(new Date());
        String count = "";
        String empty = "Fat Cat Todo";
        JSONArray items = new JSONArray();
        try {
            JSONObject all = new JSONObject(raw);
            empty = all.optString("openText", empty);
            if (all.has("accent")) accent = Color.parseColor(all.getString("accent"));
            JSONObject days = all.optJSONObject("days");
            JSONObject day = days == null ? null : days.optJSONObject(today);
            if (day != null) {
                title = day.optString("label", title);
                int total = day.optInt("total", 0), done = day.optInt("done", 0);
                count = total > 0 ? done + "/" + total : "";
                items = day.optJSONArray("items");
                if (items == null) items = new JSONArray();
                empty = all.optString("emptyText", empty);
            }
        } catch (Exception ignored) { }

        v.setTextViewText(R.id.title, title);
        v.setTextColor(R.id.title, ink);
        v.setTextViewText(R.id.count, count);
        v.setTextColor(R.id.count, accent);
        int shown = 0;
        for (int i = 0; i < ROWS.length; i++) {
            JSONObject it = i < maxRows ? items.optJSONObject(i) : null;
            if (it == null) { v.setViewVisibility(ROWS[i], View.GONE); continue; }
            shown++;
            boolean done = it.optBoolean("d", false);
            String text = it.optString("t", "");
            SpannableString sp = new SpannableString(text);
            if (done) sp.setSpan(new StrikethroughSpan(), 0, text.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            v.setViewVisibility(ROWS[i], View.VISIBLE);
            v.setTextViewText(TEXTS[i], sp);
            v.setTextColor(TEXTS[i], done ? Color.parseColor("#9A7F75") : ink);
            v.setImageViewResource(ICONS[i], done ? R.drawable.ic_w_check : R.drawable.ic_w_circle);
        }
        v.setViewVisibility(R.id.empty, shown == 0 ? View.VISIBLE : View.GONE);
        v.setTextViewText(R.id.empty, empty);

        Intent launch = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName());
        if (launch != null) {
            PendingIntent pi = PendingIntent.getActivity(ctx, 0, launch, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            v.setOnClickPendingIntent(R.id.root, pi);
        }
        mgr.updateAppWidget(id, v);
    }
}
