#!/bin/bash
# Overnight party-size data runs (7-8 Sep 2026). Each step logs to data/raw/overnight_party_size/<step>.log; failures do not stop later steps.
cd "$(dirname "$0")/../.."
export PYTHONIOENCODING=utf-8
L=data/raw/overnight_party_size; mkdir -p $L
ts() { date '+%H:%M:%S'; }
echo "$(ts) start" > $L/status.log

# 0. wait for the first-pass shards (started earlier) to finish
until [ "$(ls data/processed/abnb_party_size_reviews_market_quarter_shard[0-5].csv 2>/dev/null | wc -l)" -ge 6 ]; do sleep 60; done
echo "$(ts) first-pass shards finished" >> $L/status.log

# 1. re-run the markets whose files were re-downloaded after the shards started
py -3.13 analysis/src/abnb_party_size_reviews.py --shard 0 1 bogot pays-basque budapest trentino malaga sevilla stockholm zurich > $L/rerun_fixed.log 2>&1
echo "$(ts) step1 rerun fixed markets: $(grep -c ERR $L/rerun_fixed.log) errors" >> $L/status.log

# 2. aggregate first pass -> global/regional quarterly
py -3.13 analysis/src/abnb_party_size_reviews_aggregate.py > $L/aggregate.log 2>&1
echo "$(ts) step2 aggregate exit $?" >> $L/status.log

# 3. validation vs Hawaii DBEDT
py -3.13 analysis/src/party_size_validate_hawaii.py > $L/validate_hawaii.log 2>&1
echo "$(ts) step3 validate exit $?" >> $L/status.log

# 4. Booking.com comparators (downloads ~2 GB from Hugging Face) and the newsroom crawl, in parallel with the v2 pass
py -3.13 analysis/src/booking_party_composition.py > $L/booking.log 2>&1 &
py -3.13 analysis/src/abnb_newsroom_party_mentions.py > $L/newsroom.log 2>&1 &

# 5. second pass: capacity-bucket x room-type x quarter, market x month, language x year (6 shards)
for i in 0 1 2 3 4 5; do py -3.13 analysis/src/abnb_party_size_reviews_v2.py --shard $i 6 > $L/v2_shard_$i.log 2>&1 & done
wait
echo "$(ts) step4/5 booking, newsroom, v2 shards finished: v2 errors $(cat $L/v2_shard_*.log | grep -c ERR)" >> $L/status.log

# 6. re-run the benchmark table (picks up anything new) and finish
py -3.13 analysis/src/party_size_benchmarks.py > $L/benchmarks.log 2>&1
echo "$(ts) ALL DONE" >> $L/status.log
