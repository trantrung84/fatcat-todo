#!/usr/bin/env ruby
# Idempotent: wires Fat Cat Todo's native iOS sources into app_ios/App/App.xcodeproj
#  - app target: MainViewController / BillingPlugin / WidgetBridgePlugin + App Group entitlements
#  - WidgetKit extension target "FatCatWidget" embedded in the app
# Run on macOS (needs the xcodeproj gem):  gem install xcodeproj && ruby tools/ios_setup.rb
require 'xcodeproj'

ROOT = File.expand_path('../app_ios/App', __dir__)
proj = Xcodeproj::Project.open(File.join(ROOT, 'App.xcodeproj'))
app = proj.targets.find { |t| t.name == 'App' } or abort 'App target missing'
VERSION = ENV['MARKETING_VERSION'] || '1.4.2'
APP_ID = 'com.fatcat.todo'
WIDGET_ID = "#{APP_ID}.FatCatWidget"

# ---------- app target ----------
app_group = proj.main_group.find_subpath('App', false) or abort 'App group missing'
%w[MainViewController.swift BillingPlugin.swift WidgetBridgePlugin.swift].each do |f|
  next if app_group.files.any? { |r| r.path == f }
  ref = app_group.new_reference(f)
  app.source_build_phase.add_file_reference(ref)
  puts "added #{f} to App"
end
unless app_group.files.any? { |r| r.path == 'GoogleService-Info.plist' }
  app.resources_build_phase.add_file_reference(app_group.new_reference('GoogleService-Info.plist'))
  puts 'added GoogleService-Info.plist'
end
app_group.new_reference('App.entitlements') unless app_group.files.any? { |r| r.path == 'App.entitlements' }
app.build_configurations.each do |c|
  s = c.build_settings
  s['CODE_SIGN_ENTITLEMENTS'] = 'App/App.entitlements'
  s['MARKETING_VERSION'] = VERSION
  s['CURRENT_PROJECT_VERSION'] ||= '1'
  s['CODE_SIGN_STYLE'] = 'Automatic'
  s['IPHONEOS_DEPLOYMENT_TARGET'] = '15.0'
end

# ---------- widget extension ----------
widget = proj.targets.find { |t| t.name == 'FatCatWidget' }
unless widget
  widget = proj.new_target(:app_extension, 'FatCatWidget', :ios, '15.0', proj.products_group, :swift)
  grp = proj.main_group.find_subpath('FatCatWidget', true)
  grp.set_source_tree('<group>'); grp.set_path('FatCatWidget')
  widget.source_build_phase.add_file_reference(grp.new_reference('FatCatWidget.swift'))
  widget.resources_build_phase.add_file_reference(grp.new_reference('Assets.xcassets'))
  grp.new_reference('Info.plist')
  grp.new_reference('FatCatWidget.entitlements')
  %w[WidgetKit SwiftUI].each do |fw|
    ref = proj.frameworks_group.new_file("System/Library/Frameworks/#{fw}.framework", :sdk_root)
    widget.frameworks_build_phase.add_file_reference(ref)
  end
  # embed .appex into the app
  app.add_dependency(widget)
  embed = app.copy_files_build_phases.find { |p| p.name == 'Embed Foundation Extensions' } ||
          app.new_copy_files_build_phase('Embed Foundation Extensions')
  embed.dst_subfolder_spec = '13' # PlugIns
  bf = embed.add_file_reference(widget.product_reference, true)
  bf.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
  puts 'created FatCatWidget extension target'
end
widget.build_configurations.each do |c|
  s = c.build_settings
  s['PRODUCT_BUNDLE_IDENTIFIER'] = WIDGET_ID
  s['PRODUCT_NAME'] = '$(TARGET_NAME)'
  s['INFOPLIST_FILE'] = 'FatCatWidget/Info.plist'
  s['GENERATE_INFOPLIST_FILE'] = 'NO'
  s['CODE_SIGN_ENTITLEMENTS'] = 'FatCatWidget/FatCatWidget.entitlements'
  s['CODE_SIGN_STYLE'] = 'Automatic'
  s['SWIFT_VERSION'] = '5.0'
  s['IPHONEOS_DEPLOYMENT_TARGET'] = '15.0'
  s['TARGETED_DEVICE_FAMILY'] = '1,2'
  s['MARKETING_VERSION'] = VERSION
  s['CURRENT_PROJECT_VERSION'] = app.build_configurations.first.build_settings['CURRENT_PROJECT_VERSION'] || '1'
  s['SKIP_INSTALL'] = 'YES'
  s['ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME'] = ''
  s['ASSETCATALOG_COMPILER_WIDGET_BACKGROUND_COLOR_NAME'] = ''
  s['LD_RUNPATH_SEARCH_PATHS'] = ['$(inherited)', '@executable_path/Frameworks', '@executable_path/../../Frameworks']
  s['APPLICATION_EXTENSION_API_ONLY'] = 'YES'
end

# shared scheme for xcodebuild
proj.save
scheme = Xcodeproj::XCScheme.new
scheme.configure_with_targets(app, nil, launch_target: true)
scheme.save_as(File.join(ROOT, 'App.xcodeproj'), 'App', true)
puts 'project saved'
