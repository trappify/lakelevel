# Configuration

When adding the integration:

1. Select the desired river from the dropdown (fetched live from vattenreglering.se).
2. Choose the lake within that river.
3. Decide how many times per day the integration should fetch data (1–4). Provide the corresponding HH:MM times (defaults are evenly spaced, starting at 06:00).
4. Optionally adjust the retry count (default 3).

The integration schedules fetches at the specified times. If a request fails, it retries up to the configured number of attempts before marking the sensor unavailable until the next scheduled run. You can change the schedule later from **Configure → Options** on the integration card.
