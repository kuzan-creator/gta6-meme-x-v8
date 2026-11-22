import { cpSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const root = fileURLToPath(new URL(".", import.meta.url));
const out = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(out, { recursive: true });

const files = [
  "meme.png",
  "meme.jpg",
  "main.ts",
  "draw_meme.py",
  "README.md",
  "LICENSE",
  "POST.json",
];
for (const f of files) {
  cpSync(join(root, f), join(out, f));
}
