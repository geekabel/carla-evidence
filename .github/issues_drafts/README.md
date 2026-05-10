# GitHub issue drafts

These markdown files are the source of truth for the issues we want filed
on GitHub but haven't created yet. Once the repo is pushed, file them with:

```bash
gh issue create \
    --title "$(head -1 001-cautious-bold-v0.2.1.md | sed 's/^# //')" \
    --body "$(tail -n +2 001-cautious-bold-v0.2.1.md)" \
    --label tracking,enhancement
```

(Adjust labels per the GitHub label set you've configured. The drafts list
suggested labels at the top of each file.)

After filing, **delete the corresponding draft file** and link the issue
URL from any RFC, PR description, or CHANGELOG entry that references it.
