# pixelcrash/Sync-Rentals-Calendar sample

What: a 5 KB PHP iCal merger (icalmerger.php) that unions a host's Airbnb/Booking.com/Atraveo availability feeds, plus the one merged calendar the author committed, ics/allservices.ics (single Austrian rental, kuenstlerzimmer.at, 13 all-day VEVENTs Jan-Jun 2019, channel in SUMMARY).
How pulled (2026-09-14): curl of the two raw files from raw.githubusercontent.com/pixelcrash/Sync-Rentals-Calendar/HEAD/; repo metadata via gh api. VEVENTs parsed to allservices_events.csv (uid, channel, dtstart, dtend, nights, dtstamp) with Python.
Caps: 9 KB total, 3 files; vendor/ not pulled; the tool was not run (needs a host's private feed URLs).
This is the whole dataset - nothing larger exists upstream. Full repo: git clone --depth 1 https://github.com/pixelcrash/Sync-Rentals-Calendar (31 KB).
Caveats: no licence; only 4 of 13 events carry a channel label (ATRAVEO), the other 9 have a date as SUMMARY and overlap them, so the ics looks like test output. Value is as a worked example of the iCal route to channel-tagged per-listing occupancy, not as data.
