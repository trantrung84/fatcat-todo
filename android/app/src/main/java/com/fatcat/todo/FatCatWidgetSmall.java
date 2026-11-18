package com.fatcat.todo;

/** Compact (2x2) variant of the today widget. */
public class FatCatWidgetSmall extends FatCatWidget {
    @Override protected int layout() { return R.layout.widget_small; }
    @Override protected int maxRows() { return 3; }
}
