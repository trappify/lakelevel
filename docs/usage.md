# Usage

Once configured, the integration exposes a sensor named `<Lake> water level`.

Attributes:
- `river`: River/älv the lake belongs to.
- `timestamp`: Measurement timestamp reported by vattenreglering.se.

Use the sensor in automations or dashboards like any other Home Assistant sensor. For a manual refresh outside the scheduled schedule, use the entity’s **Update** action in the UI; the integration respects the retry settings. Scheduled updates run at the times you configure (up to four per day) without hammering the upstream service.

This integration is provided without warranty and is not endorsed by Vattenregleringsföretagen.
