#!/usr/bin/env node
// paranoid-agent single entry point.
//   npx paranoid-agent-skill --dir <path>   install the skill files
//   npx paranoid-agent-skill mcp            start the MCP server (stdio)
const [sub] = process.argv.slice(2);
if (sub === "mcp") {
  await import("./mcp.mjs");
} else {
  await import("./install.mjs");
}
