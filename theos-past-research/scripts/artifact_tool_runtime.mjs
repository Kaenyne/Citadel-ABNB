/** Resolve the pinned private Artifact Tool without committing a machine path. */

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";


export const REQUIRED_NODE_VERSION = "24.19.0";
export const REQUIRED_ARTIFACT_TOOL_VERSION = "2.8.59";

function candidateRoots() {
  const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  return [
    process.env.ARTIFACT_TOOL_PACKAGE_ROOT,
    path.join(projectRoot, "node_modules", "@oai", "artifact-tool"),
    path.join(
      os.homedir(),
      ".cache",
      "codex-runtimes",
      "codex-primary-runtime",
      "dependencies",
      "node",
      "node_modules",
      "@oai",
      "artifact-tool",
    ),
  ].filter(Boolean);
}

async function packageVersion(packageRoot) {
  try {
    const text = await fs.readFile(path.join(packageRoot, "package.json"), "utf8");
    return JSON.parse(text).version;
  } catch (error) {
    if (error && ["ENOENT", "ENOTDIR"].includes(error.code)) return null;
    throw error;
  }
}

export async function loadArtifactTool() {
  if (process.versions.node !== REQUIRED_NODE_VERSION) {
    throw new Error(
      `Workbook generation requires Node ${REQUIRED_NODE_VERSION}; found ${process.versions.node}. ` +
      "Use the version pinned in .node-version.",
    );
  }
  const inspected = [];
  for (const packageRoot of candidateRoots()) {
    const version = await packageVersion(packageRoot);
    inspected.push(`${packageRoot} (${version ?? "missing"})`);
    if (version === null) continue;
    if (version !== REQUIRED_ARTIFACT_TOOL_VERSION) {
      throw new Error(
        `Artifact Tool ${REQUIRED_ARTIFACT_TOOL_VERSION} is required; found ${version} at ${packageRoot}.`,
      );
    }
    return import(pathToFileURL(path.join(packageRoot, "dist", "artifact_tool.mjs")).href);
  }
  throw new Error(
    `Artifact Tool ${REQUIRED_ARTIFACT_TOOL_VERSION} was not found. ` +
    "Set ARTIFACT_TOOL_PACKAGE_ROOT to the approved package directory. Checked: " +
    inspected.join(", "),
  );
}
