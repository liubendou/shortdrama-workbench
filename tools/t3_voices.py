import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    zh = sorted(v["ShortName"] for v in voices if v["ShortName"].startswith("zh-CN"))
    print("zh-CN count", len(zh))
    print(" ".join(zh))

asyncio.run(main())
