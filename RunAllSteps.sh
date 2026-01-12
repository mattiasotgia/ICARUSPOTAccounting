#!/bin/bash

# start="2026-01-05"
# end="2026-01-11"

start="2025-10-16"
end="2026-01-12"

python ParseDAQLog.py -i ${start} -f ${end}
python pot_account.py update-daily-pot ${start} ${end} True
python pot_account.py update-daily-runs ${start} ${end} True
python pot_account.py make-daq-plots ${start} ${end}

