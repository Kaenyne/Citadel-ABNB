import type { Match } from '@/data/schedule';
import { getFlag } from '@/lib/flags';

const PRODID = '-//world-cup-2026-schedule-calendar//World Cup 2026 Schedule//EN';
const CALNAME = 'World Cup 2026 - Lịch thi đấu';

function formatIcsDate(isoString: string): string {
  let s = isoString.replace(/[-:]/g, '');
  if (s.endsWith('Z')) s = s.slice(0, -1);
  return s.split('.')[0] + 'Z';
}

function escapeIcsText(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;')
    .replace(/\n/g, '\\n');
}

function foldLine(line: string): string {
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  const bytes = encoder.encode(line);

  if (bytes.length <= 75) {
    return line;
  }

  const chunks: string[] = [];
  let start = 0;

  while (start < bytes.length) {
    const maxLen = chunks.length === 0 ? 75 : 74;
    let end = start + maxLen;

    if (end >= bytes.length) {
      const chunkBytes = bytes.slice(start);
      chunks.push((chunks.length > 0 ? ' ' : '') + decoder.decode(chunkBytes));
      break;
    }

    while (end > start && (bytes[end] & 0xC0) === 0x80) {
      end--;
    }

    if (end === start) {
      end = start + maxLen;
    }

    const chunkBytes = bytes.slice(start, end);
    chunks.push((chunks.length > 0 ? ' ' : '') + decoder.decode(chunkBytes));
    start = end;
  }

  return chunks.join('\r\n');
}

function buildEvent(match: Match, baseUrl: string): string {
  const dtStart = formatIcsDate(match.datetime);
  const dtEnd = formatIcsDate(
    new Date(new Date(match.datetime).getTime() + 2 * 60 * 60 * 1000).toISOString()
  );

  const flagA = getFlag(match.teamA);
  const flagB = getFlag(match.teamB);
  const summary = `${flagA} ${match.teamA} vs ${flagB} ${match.teamB}${match.group ? ` - Group ${match.group}` : ''}`;
  const location = match.venue;
  
  const host = baseUrl.replace(/^https?:\/\//, "");
  const webcalUrl = `webcal://${host}/api/calendar`;

  const description = [
    'FIFA World Cup 2026',
    match.group ? `Group ${match.group}` : match.stage.replace(/-/g, ' '),
    '',
    location,
    '',
    'Cập nhật tự động: sau vòng bảng, đội knock-out sẽ thay thế "Winner Group X" trong lịch của bạn.',
    'Flags quốc gia có sẵn trong tiêu đề sự kiện.',
    `Nguồn: ${baseUrl} | Subscribe: ${webcalUrl}`,
  ].join('\n');

  const uid = `wc2026-${match.id}@${host}`;
  const now = formatIcsDate(new Date().toISOString());

  return [
    'BEGIN:VEVENT',
    `UID:${uid}`,
    `DTSTAMP:${now}`,
    `DTSTART:${dtStart}`,
    `DTEND:${dtEnd}`,
    `SUMMARY:${escapeIcsText(summary)}`,
    `DESCRIPTION:${escapeIcsText(description)}`,
    `LOCATION:${escapeIcsText(location)}`,
    `URL:${baseUrl}`,
    'STATUS:CONFIRMED',
    'TRANSP:OPAQUE',
    'CATEGORIES:SPORTS,WORLD CUP',
    'END:VEVENT',
  ].join('\r\n');
}

export function generateIcs(matches: Match[], baseUrl?: string): string {
  const finalBaseUrl = baseUrl ||
    process.env.NEXT_PUBLIC_SITE_URL ||
    (process.env.NEXT_PUBLIC_VERCEL_URL ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}` : 'http://localhost:3000');

  const rawLines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    `PRODID:${PRODID}`,
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    `X-WR-CALNAME:${CALNAME}`,
    'X-WR-TIMEZONE:UTC',
    'X-WR-CALDESC:FIFA World Cup 2026 - Lịch thi đấu đầy đủ. Subscribe 1 lần qua WebCal: tự động cập nhật đội knock-out sau vòng bảng + emoji cờ quốc gia trong mỗi trận.',
    ...matches.map(m => buildEvent(m, finalBaseUrl)).flatMap(eventStr => eventStr.split('\r\n')),
    'END:VCALENDAR',
  ];

  return rawLines.map(foldLine).join('\r\n');
}

