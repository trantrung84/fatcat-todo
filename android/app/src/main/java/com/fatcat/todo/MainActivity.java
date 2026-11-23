package com.fatcat.todo;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.ContentResolver;
import android.media.AudioAttributes;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    /** Alarm-style reminder channel: 10 s Fat Cat chime at alarm volume + long vibration. */
    public static final String ALARM_CHANNEL = "fatcat_alarm";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(WidgetBridgePlugin.class);
        registerPlugin(BillingPlugin.class);
        super.onCreate(savedInstanceState);
        createAlarmChannel();
    }

    private void createAlarmChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm == null || nm.getNotificationChannel(ALARM_CHANNEL) != null) return; // channel settings are immutable once created
        NotificationChannel ch = new NotificationChannel(ALARM_CHANNEL, getString(R.string.alarm_channel_name), NotificationManager.IMPORTANCE_HIGH);
        ch.setDescription(getString(R.string.alarm_channel_desc));
        Uri sound = Uri.parse(ContentResolver.SCHEME_ANDROID_RESOURCE + "://" + getPackageName() + "/" + R.raw.fatcat_alarm);
        AudioAttributes attrs = new AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .setUsage(AudioAttributes.USAGE_ALARM)
                .build();
        ch.setSound(sound, attrs);
        ch.enableVibration(true);
        // ~9 s of buzz–pause, like an alarm clock
        ch.setVibrationPattern(new long[]{0, 900, 500, 900, 500, 900, 500, 900, 500, 900, 500, 900});
        ch.enableLights(true);
        ch.setLockscreenVisibility(android.app.Notification.VISIBILITY_PUBLIC);
        nm.createNotificationChannel(ch);
    }
}
