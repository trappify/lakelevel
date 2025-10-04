# Configuration

When adding the integration:

1. Select the desired river from the dropdown (fetched live from vattenreglering.se).
2. Choose the lake within that river.
3. Optionally adjust the daily fetch time (default 06:00) and the number of retries (default 3).

The integration schedules a single fetch per day at the configured time. If the request fails, it retries up to the configured number of times before marking the sensor unavailable for that day.
