import pathlib,sys
root=pathlib.Path("C:/Users/Administrator/Documents/shortdrama-workbench/upstream")
p=root/"jjyb"/"LICENSE"
t=p.read_text(encoding="utf-8",errors="replace")
print("LICENSE chars:",len(t))
print(t[:6000])
print("=== entry candidates ===")
for rel in ["jjyb/frontend/app.py","jjyb/backend/api/commentary_routes_enhanced.py","jjyb/backend/api/jianying_draft_api.py","narratoai/webui.py","narratoai/app/services/SDE/short_drama_explanation.py","narratoai/app/services/SDP/generate_script_short.py"]:
    f=root/rel
    print(rel, "EXISTS" if f.exists() else "MISSING", (f.stat().st_size if f.exists() else ""))
