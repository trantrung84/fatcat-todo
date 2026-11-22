#!/bin/sh
# Capacitor writes absolute-ish node_modules paths when node_modules is a symlink; make them repo-relative.
cd "$(dirname "$0")/.."
sed -i.bak -E 's#path: "(\.\./)+[^"]*node_modules/#path: "../../../node_modules/#' app_ios/App/CapApp-SPM/Package.swift && rm -f app_ios/App/CapApp-SPM/Package.swift.bak
sed -i.bak -E "s#'(\.\./)+fatcat/node_modules/#'../node_modules/#" android/capacitor.settings.gradle && rm -f android/capacitor.settings.gradle.bak
