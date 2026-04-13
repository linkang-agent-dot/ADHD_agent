[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
gws sheets +read --spreadsheet 1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY --range "activity_task_QA!A:C" | Out-File -FilePath "C:\ADHD_agent\_tmp_task_abc_utf8.json" -Encoding UTF8
