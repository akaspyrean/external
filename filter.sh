export FILTER_BRANCH_SQUELCH_WARNING=1
git filter-branch -f --env-filter 'if [ "$GIT_AUTHOR_NAME" = "fongap" ]; then export GIT_AUTHOR_NAME="akaspyrean"; export GIT_AUTHOR_EMAIL="akaspyrean@users.noreply.github.com"; fi' --all
