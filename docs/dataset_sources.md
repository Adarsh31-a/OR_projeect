# Dataset source and provenance

The included `data/grant_applications.csv` is a reproducible **synthetic demonstration dataset**, generated with seed `20261102`. It was not downloaded from OECD, World Bank, data.gov.in, or ForeignAssistance.gov. The records do not identify actual proposals and the scores are simulated analyst-style estimates, not observed effects. Therefore, no external data licence applies to these generated records.

The project brief suggested the following sources as possible starting points for a future real-data adaptation:

- OECD Data Explorer: <https://data-explorer.oecd.org/>
- World Bank Open Data: <https://data.worldbank.org/>
- Government of India Open Government Data Platform: <https://www.data.gov.in/>
- ForeignAssistance.gov: <https://foreignassistance.gov/data>

Before importing real data, the project team must record the exact endpoint, download date, licence, geographic coverage, time period, units, and transformations. A source with programme-level funding may not contain application-level socioeconomic impact measures. When these measures are estimated by evaluators, they must remain labelled as estimates. Map cleaned fields to the included CSV schema, preserve the 1--10 rubric, and validate the CSV before ranking.
