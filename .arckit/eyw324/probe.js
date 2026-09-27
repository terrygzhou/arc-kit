#!/usr/bin/env node
// EYW-324 final-disposition retry chain (compact, idempotent, env-driven).
// Usage: node .arckit/eyw324/probe.js            # complete the disposition
//        node .arckit/eyw324/probe.js --check    # read-only state check
// Requires: PAPERCLIP_API_URL + PAPERCLIP_API_KEY (+ PAPERCLIP_RUN_ID) in env.
const EID = process.env.PAPERCLIP_TASK_ID || "1462a162-689e-4716-acc8-312bb50a80ae";
const CID = process.env.PAPERCLIP_COMPANY_ID || "37f9295e-8dda-44b4-8b3b-1075cdc2b849";
const CHECK = process.argv.includes("--check");
const MARKER = "eyw324-final-handoff";
const HANDOFF = "Handoff: P0 done (EYW-330, 51922d2d) and P1 done (0c7dccde, 9 shared schemas + validate-architecture.py CI gate); QA review doc eyw-324-codex-plugin-review board-approved -> closing EYW-324 as done.\n[" + MARKER + "]";
function http(method, path, body) {
  return new Promise((resolve) => {
    const url = new URL(path, (process.env.PAPERCLIP_API_URL || "").replace(/\/api$/, "") || "http://127.0.0.1:3100/");
    const headers = { "Authorization": "Bearer " + (process.env.PAPERCLIP_API_KEY || "") };
    if (process.env.PAPERCLIP_RUN_ID) headers["X-Paperclip-Run-Id"] = process.env.PAPERCLIP_RUN_ID;
    let payload = null;
    if (body) { payload = JSON.stringify(body); headers["Content-Type"] = "application/json"; }
    const req = require("http").request(url, { method, headers, timeout: 8000 }, (res) => {
      let data = "";
      res.on("data", (d) => (data += d));
      res.on("end", () => resolve([res.statusCode, data]));
    });
    req.on("error", (e) => resolve([0, String(e.code || e.message)]));
    req.on("timeout", () => { req.destroy(); resolve([0, "timeout"]); });
    if (payload) req.write(payload);
    req.end();
  });
}
(async () => {
  const baseOk = await http("GET", "/api/issues/" + EID);
  if (baseOk[0] !== 200) { console.log("FATAL: GET issue -> " + baseOk[0] + " " + String(baseOk[1]).slice(0,200)); process.exit(2); }
  const issue = JSON.parse((await http("GET", "/api/issues/" + EID))[1] || "{}");
  if (issue.status === "done") { console.log("ALREADY-DONE: EYW-324 is done; nothing to do"); return; }
  const comments = (await http("GET", "/api/issues/" + EID + "/comments?limit=30"))[1] || "[]";
  if (String(comments).includes(MARKER)) { console.log("MARKER-PRESENT: final handoff already posted; only status remains"); }
  else if (CHECK) { console.log("CHECK: status=" + issue.status + ", marker absent; run without --check to post handoff + set done"); return; }
  else {
    const c = await http("POST", "/api/issues/" + EID + "/comments", { body: HANDOFF });
    console.log("POST handoff comment -> " + c[0]);
    if (c[0] < 200 || c[0] >= 300) { console.log("comment failed: " + String(c[1]).slice(0,200)); process.exit(3); }
  }
  const p = await http("PATCH", "/api/issues/" + EID, { status: "done" });
  console.log("PATCH status done -> " + p[0] + " " + String(p[1]).slice(0,200));
  process.exitCode = p[0] >= 200 && p[0] < 300 ? 0 : 4;
})();
