export type Stage =
  | 'group'
  | 'round-of-32'
  | 'round-of-16'
  | 'quarter-final'
  | 'semi-final'
  | 'third-place'
  | 'final';

export interface Match {
  id: string;
  stage: Stage;
  group?: string;
  datetime: string;
  teamA: string;
  teamB: string;
  venue: string;
  city: string;
  matchday?: number;
  score?: {
    ft?: [number, number];
    ht?: [number, number];
    et?: [number, number];
    p?: [number, number];
  };
  goalsA?: Array<{ name: string; minute: string; penalty?: boolean; owngoal?: boolean }>;
  goalsB?: Array<{ name: string; minute: string; penalty?: boolean; owngoal?: boolean }>;
}

export const OPENING_MATCH_DATETIME = '2026-06-11T23:00:00Z';

export const matches: Match[] = [

  {
    id: 'm001',
    stage: 'group',
    group: 'A',
    datetime: '2026-06-11T23:00:00Z',
    teamA: 'Mexico',
    teamB: 'South Africa',
    venue: 'Estadio Azteca',
    city: 'Mexico City',
    matchday: 1,
  },
  {
    id: 'm002',
    stage: 'group',
    group: 'A',
    datetime: '2026-06-11T20:00:00Z',
    teamA: 'Korea Republic',
    teamB: 'Czechia',
    venue: 'Estadio Guadalajara',
    city: 'Guadalajara',
    matchday: 1,
  },
  {
    id: 'm003',
    stage: 'group',
    group: 'B',
    datetime: '2026-06-12T01:00:00Z',
    teamA: 'Canada',
    teamB: 'Bosnia and Herzegovina',
    venue: 'BMO Field',
    city: 'Toronto',
    matchday: 1,
  },
  {
    id: 'm004',
    stage: 'group',
    group: 'D',
    datetime: '2026-06-12T02:00:00Z',
    teamA: 'United States',
    teamB: 'Paraguay',
    venue: 'SoFi Stadium',
    city: 'Los Angeles',
    matchday: 1,
  },

  {
    id: 'm005',
    stage: 'group',
    group: 'C',
    datetime: '2026-06-12T23:00:00Z',
    teamA: 'Brazil',
    teamB: 'Morocco',
    venue: 'MetLife Stadium',
    city: 'New York/New Jersey',
    matchday: 1,
  },
  {
    id: 'm006',
    stage: 'group',
    group: 'E',
    datetime: '2026-06-13T01:00:00Z',
    teamA: 'Germany',
    teamB: "Côte d'Ivoire",
    venue: 'AT&T Stadium',
    city: 'Dallas',
    matchday: 1,
  },
  {
    id: 'm007',
    stage: 'group',
    group: 'F',
    datetime: '2026-06-13T20:00:00Z',
    teamA: 'Netherlands',
    teamB: 'Japan',
    venue: 'Estadio Monterrey',
    city: 'Monterrey',
    matchday: 1,
  },
  {
    id: 'm008',
    stage: 'group',
    group: 'G',
    datetime: '2026-06-13T23:00:00Z',
    teamA: 'Belgium',
    teamB: 'Egypt',
    venue: 'Lincoln Financial Field',
    city: 'Philadelphia',
    matchday: 1,
  },

  {
    id: 'm009',
    stage: 'group',
    group: 'A',
    datetime: '2026-06-18T23:00:00Z',
    teamA: 'Mexico',
    teamB: 'Korea Republic',
    venue: 'Estadio Azteca',
    city: 'Mexico City',
    matchday: 2,
  },
  {
    id: 'm010',
    stage: 'group',
    group: 'B',
    datetime: '2026-06-19T01:00:00Z',
    teamA: 'Canada',
    teamB: 'Qatar',
    venue: 'Commonwealth Stadium',
    city: 'Edmonton',
    matchday: 2,
  },
  {
    id: 'm011',
    stage: 'group',
    group: 'D',
    datetime: '2026-06-20T20:00:00Z',
    teamA: 'United States',
    teamB: 'Australia',
    venue: 'Hard Rock Stadium',
    city: 'Miami',
    matchday: 2,
  },

  {
    id: 'm012',
    stage: 'group',
    group: 'A',
    datetime: '2026-06-25T23:00:00Z',
    teamA: 'South Africa',
    teamB: 'Czechia',
    venue: 'Estadio León',
    city: 'León',
    matchday: 3,
  },
  {
    id: 'm013',
    stage: 'group',
    group: 'C',
    datetime: '2026-06-26T20:00:00Z',
    teamA: 'Brazil',
    teamB: 'Scotland',
    venue: 'NRG Stadium',
    city: 'Houston',
    matchday: 3,
  },

  {
    id: 'm014',
    stage: 'round-of-32',
    datetime: '2026-06-28T20:00:00Z',
    teamA: 'Winner Group A',
    teamB: 'Runner-up Group B',
    venue: 'Estadio Azteca',
    city: 'Mexico City',
  },
  {
    id: 'm015',
    stage: 'round-of-32',
    datetime: '2026-06-29T23:00:00Z',
    teamA: 'Winner Group C',
    teamB: 'Runner-up Group D',
    venue: 'SoFi Stadium',
    city: 'Los Angeles',
  },
  {
    id: 'm016',
    stage: 'round-of-32',
    datetime: '2026-06-30T20:00:00Z',
    teamA: 'Winner Group E',
    teamB: 'Runner-up Group F',
    venue: 'AT&T Stadium',
    city: 'Dallas',
  },

  {
    id: 'm017',
    stage: 'round-of-16',
    datetime: '2026-07-04T20:00:00Z',
    teamA: 'Winner R32-1',
    teamB: 'Winner R32-2',
    venue: 'MetLife Stadium',
    city: 'New York/New Jersey',
  },
  {
    id: 'm018',
    stage: 'round-of-16',
    datetime: '2026-07-05T23:00:00Z',
    teamA: 'Winner R32-3',
    teamB: 'Winner R32-4',
    venue: 'BMO Field',
    city: 'Toronto',
  },

  {
    id: 'm019',
    stage: 'quarter-final',
    datetime: '2026-07-09T23:00:00Z',
    teamA: 'Winner R16-1',
    teamB: 'Winner R16-2',
    venue: 'AT&T Stadium',
    city: 'Dallas',
  },
  {
    id: 'm020',
    stage: 'quarter-final',
    datetime: '2026-07-10T20:00:00Z',
    teamA: 'Winner R16-3',
    teamB: 'Winner R16-4',
    venue: 'Lincoln Financial Field',
    city: 'Philadelphia',
  },

  {
    id: 'm021',
    stage: 'semi-final',
    datetime: '2026-07-14T23:00:00Z',
    teamA: 'Winner QF-1',
    teamB: 'Winner QF-2',
    venue: 'AT&T Stadium',
    city: 'Dallas',
  },
  {
    id: 'm022',
    stage: 'semi-final',
    datetime: '2026-07-15T23:00:00Z',
    teamA: 'Winner QF-3',
    teamB: 'Winner QF-4',
    venue: 'Mercedes-Benz Stadium',
    city: 'Atlanta',
  },

  {
    id: 'm023',
    stage: 'third-place',
    datetime: '2026-07-18T20:00:00Z',
    teamA: 'Loser SF-1',
    teamB: 'Loser SF-2',
    venue: 'Hard Rock Stadium',
    city: 'Miami',
  },
  {
    id: 'm024',
    stage: 'final',
    datetime: '2026-07-19T20:00:00Z',
    teamA: 'Winner SF-1',
    teamB: 'Winner SF-2',
    venue: 'MetLife Stadium',
    city: 'New York/New Jersey',
  },
];

export const allStages: Stage[] = [
  'group',
  'round-of-32',
  'round-of-16',
  'quarter-final',
  'semi-final',
  'third-place',
  'final',
];
