#!/usr/bin/env bash
# Print a require()-able puppeteer path, or exit 1. No installing: this is a
# read-only audit and it should not mutate the machine to run.
for d in "$PWD/node_modules/puppeteer" \
         "$HOME/node_modules/puppeteer" \
         "$(npm root -g 2>/dev/null)/puppeteer"; do
  [ -d "$d" ] && { echo "$d"; exit 0; }
done
echo "no puppeteer found — install one or pass PUPPETEER_PATH" >&2
exit 1
