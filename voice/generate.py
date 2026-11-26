"""Make one Microsoft Tamil voice clip (edge-tts, free, no key) per line in voice/script.json.

Runs on GitHub Actions. Writes voice/out/NN.mp3 plus voice/out/manifest.json.
"""
import asyncio, json, os

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
script = json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8"))
out_dir = os.path.join(HERE, "out")
os.makedirs(out_dir, exist_ok=True)


async def say(text, v, path):
    for attempt in range(4):
        try:
            c = edge_tts.Communicate(text, v["voice"], rate=v.get("rate", "+0%"), pitch=v.get("pitch", "+0Hz"))
            await c.save(path)
            if os.path.getsize(path) > 1000:
                return
        except Exception as e:
            print("retry", attempt, e)
        await asyncio.sleep(3 * (attempt + 1))
    raise SystemExit(f"could not make {path}")


async def main():
    manifest, n = [], 0
    for si, shot in enumerate(script["shots"]):
        for li, line in enumerate(shot["lines"]):
            v = script["voices"][line["spk"]]
            name = f"{n:02d}.mp3"
            await say(line["text"], v, os.path.join(out_dir, name))
            manifest.append({"n": n, "shot": si, "line": li, "spk": line["spk"], "text": line["text"], "file": name})
            print(f"{name}  {line['spk']}: {line['text']}")
            n += 1
    json.dump(manifest, open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done:", n, "clips")


asyncio.run(main())
