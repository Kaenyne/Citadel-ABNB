import type { Match, Stage } from "@/data/schedule";
import { normalizeTeamName } from "@/data/teams/index";

export const WORLDCUP_JSON_URL =
  "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json";

export interface RawMatch {
  round: string;
  date: string;
  time: string;
  team1: string;
  team2: string;
  group?: string;
  ground?: string;
  score?: {
    ft?: [number, number];
    ht?: [number, number];
    et?: [number, number];
    p?: [number, number];
  };
  goals1?: Array<{ name: string; minute: string; penalty?: boolean; owngoal?: boolean }>;
  goals2?: Array<{ name: string; minute: string; penalty?: boolean; owngoal?: boolean }>;
}

function parseTimeToUTC(dateStr: string, timeStr: string): string {
  const match = timeStr.match(/(\d{1,2}):(\d{2})\s*UTC([+-]\d+)/);
  if (!match) {
    return `${dateStr}T00:00:00Z`;
  }

  const [, hh, mm, offsetStr] = match;
  const offsetHours = parseInt(offsetStr, 10);
  const wallH = parseInt(hh, 10);
  const wallM = parseInt(mm, 10);

  let utcH = wallH - offsetHours;
  let dayOffset = 0;

  while (utcH >= 24) { utcH -= 24; dayOffset += 1; }
  while (utcH < 0) { utcH += 24; dayOffset -= 1; }

  const [y, m, d] = dateStr.split("-").map(Number);
  const utcDate = new Date(Date.UTC(y, m - 1, d + dayOffset, utcH, wallM, 0));

  return utcDate.toISOString();
}

export function mapRoundToStage(round: string): Stage {
  const lower = round.toLowerCase();

  if (lower.includes("matchday") || lower.includes("group")) return "group";
  if (lower.includes("round of 32") || lower.includes("1/16")) return "round-of-32";
  if (lower.includes("round of 16") || lower.includes("1/8")) return "round-of-16";
  if (lower.includes("quarter")) return "quarter-final";
  if (lower.includes("semi")) return "semi-final";
  if (lower.includes("third")) return "third-place";
  if (lower.includes("final")) return "final";

  return "group";
}

function extractCity(ground?: string): string {
  if (!ground) return "";
  return ground.replace(/\s*\(.*?\)\s*$/, "").trim();
}

export function mapRawMatchToMatch(m: RawMatch, index: number): Match {
  const datetime = parseTimeToUTC(m.date, m.time);
  const stage = mapRoundToStage(m.round);
  const group = m.group ? m.group.replace("Group ", "") : undefined;

  return {
    id: `wc26-${index + 1}`,
    stage,
    group,
    datetime,
    teamA: normalizeTeamName(m.team1),
    teamB: normalizeTeamName(m.team2),
    venue: m.ground || "",
    city: extractCity(m.ground),
    score: m.score,
    goalsA: m.goals1,
    goalsB: m.goals2,
  };
}

export async function getWorldCupMatches(): Promise<Match[]> {
  const res = await fetch(WORLDCUP_JSON_URL, {
    next: { revalidate: 3600 },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch World Cup data");
  }

  const data = await res.json();
  const rawMatches: RawMatch[] = data.matches || [];

  return rawMatches.map((m, index) => mapRawMatchToMatch(m, index));
}
