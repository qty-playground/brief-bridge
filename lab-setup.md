請建立 2 組 worktree 作為 token 消耗數量的比較專案

1. lab-serena-mcp
2. lab-git-search

## All setup

1. 所以 worktree 都需要建立 venv，並且 enable 環境。
2. source venv/bin/activate 後，使用 `pip install -e ".[test]"` 完成安裝
3. 每組實驗，都會在各自的 worktree 使用這個指令啟動 claude code `claude --model claude-sonnet-4-20250514 --dangerously-skip-permissions`
4. 以 sdk 模式執行，讓它自動結束。

## lab-serena-mcp

啟動 claude code 前，先加入 mcp

```
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

進入 claude code，並使用 @task-for-list-clients.md 的問題作為 benchmark 直到「樓主平安喜樂」結束 claude code 完成實驗

## lab-git-search

啟動 claude code 後，先引用 @git-search-pref.md 作為問題查找的偏好設定。

進入 claude code，並使用 @task-for-list-clients.md 的問題作為 benchmark 直到「樓主平安喜樂」結束 claude code 完成實驗
