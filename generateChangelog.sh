# This command will output a html file changelog.
git --no-pager log --color=always --oneline  v1...v2 | aha --stylesheet --word-wrap > dist/v2/changelog.html
