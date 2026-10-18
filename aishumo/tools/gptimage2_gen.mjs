// aishumo 图示生成工具：gpt-image-2 兼容接口
// 用法：
//   node gptimage2_gen.mjs "提示词" [low|medium|high] [1024x1024|1024x1536|1536x1024]
//
// 环境变量：
//   GPTIMAGE_API_KEY   必填
//   GPTIMAGE_BASE_URL  必填，例如 https://your-api.example.com
//   GPTIMAGE_OUT_DIR   可选，默认当前目录下的 图片AI/
//
// 说明：密钥只从环境变量读取，禁止写进仓库。

import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";

const KEY = process.env.GPTIMAGE_API_KEY || "";
const BASE = (process.env.GPTIMAGE_BASE_URL || "").replace(/\/+$/, "");
const MODEL = process.env.GPTIMAGE_MODEL || "gpt-image-2-1k";

if (!KEY) {
  console.error("缺少环境变量 GPTIMAGE_API_KEY；请先设置后再运行。");
  process.exit(1);
}
if (!BASE) {
  console.error("缺少环境变量 GPTIMAGE_BASE_URL；请先设置后再运行。");
  process.exit(1);
}

const PROMPT = process.argv[2] || "一只戴墨镜的柴犬在冲浪，动漫风格，电影感光影";
const QUALITY = process.argv[3] || "low";
const SIZE = process.argv[4] || "1024x1024";
const OUT_DIR = process.env.GPTIMAGE_OUT_DIR || path.join(process.cwd(), "图片AI");

const r = await fetch(BASE + "/v1/images/generations", {
  method: "POST",
  headers: { "Content-Type": "application/json", "Authorization": "Bearer " + KEY },
  body: JSON.stringify({ model: MODEL, prompt: PROMPT, n: 1, size: SIZE, quality: QUALITY }),
  signal: AbortSignal.timeout(120000),
});

const d = await r.json();
if (d.error) {
  console.log("ERROR", JSON.stringify(d.error).slice(0, 400));
  process.exit(1);
}
const item = d.data?.[0];
if (!item) {
  console.log("NO DATA", JSON.stringify(d).slice(0, 300));
  process.exit(1);
}

mkdirSync(OUT_DIR, { recursive: true });
const slug = (PROMPT.replace(/[^\w\u4e00-\u9fa5]+/g, "").slice(0, 12)) || "img";
const out = path.join(OUT_DIR, "gptimage2_" + slug + "_" + Date.now() + ".png");

if (item.b64_json) {
  writeFileSync(out, Buffer.from(item.b64_json, "base64"));
  console.log("SAVED", out, "|", Buffer.byteLength(item.b64_json, "base64"), "bytes | quality", QUALITY, "| size", SIZE);
} else if (item.url) {
  console.log("URL", item.url);
} else {
  console.log("UNKNOWN", JSON.stringify(d).slice(0, 300));
}
