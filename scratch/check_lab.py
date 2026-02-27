import json, pathlib, sys

p = pathlib.Path(__file__).parent.parent / "lab" / "current_state.json"
if not p.exists():
    print("current_state.json not found"); sys.exit(1)

data = json.loads(p.read_text(encoding="utf-8"))
tasks = data.get("incoming_tasks", [])

completed = [t for t in tasks if t.get("status") == "completed"]
active    = [t for t in tasks if t.get("status") == "active"]
cancelled = [t for t in tasks if t.get("status") == "cancelled"]
pending   = [t for t in tasks if t.get("status") == "pending"]

print(f"Total: {len(tasks)} | Completed: {len(completed)} | Active: {len(active)} | Pending: {len(pending)} | Cancelled: {len(cancelled)}")

print("\n=== ACTIVE ===")
for t in active:
    desc = t.get("description","")[:120].replace("\n"," ")
    model = t.get("assigned_model","?")
    print(f"  [{model}] {desc}")

print("\n=== LAST 10 COMPLETED ===")
for t in completed[-10:]:
    desc = t.get("description","")[:100].replace("\n"," ")
    decision = t.get("decision","?")
    tid = t.get("id","")[:8]
    print(f"  [{tid}] [{decision}] {desc}")

print("\n=== BUDGET ===")
lb = data.get("leaderboard", {})
print(f"  Total:      ${lb.get('total_cost_usd', lb.get('total_cost', 0)):.2f}")
print(f"  Anthropic:  ${lb.get('anthropic_cost', lb.get('claude_cost', 0)):.2f}")
print(f"  OpenAI:     ${lb.get('openai_cost', 0):.2f}")
print(f"  Google:     ${lb.get('google_cost', 0):.2f}")
print(f"  Rounds:     {data.get('total_prompts_executed', '?')}")
