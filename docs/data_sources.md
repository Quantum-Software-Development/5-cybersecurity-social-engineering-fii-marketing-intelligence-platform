# Detailed Source Documentation

This document provides a detailed view of the monitored source ecosystem used by the Investor Intelligence Platform for Brazilian Real Estate Investment Funds (FIIs). It complements the main README by documenting source grouping, acquisition strategy, source normalization, and technical ingestion logic in a cleaner and more implementation-oriented format.

## Source normalization

To keep the repository narrative internally consistent, the project adopts the following normalized count:

- **20 official financial and editorial sources**
- **1 official behavioral social source: Reddit**
- **21 total monitored sources**

This formulation avoids ambiguity between editorial publishers and social discussion environments while preserving the methodological distinction used across the platform.

## Source groups

The monitored sources are organized into three official classes:

- **Official Editorial RSS Sources**: editorial and financial portals collected through native RSS feeds whenever stable and relevant feeds are available.
- **Official Editorial Scraping Sources**: portals collected through lightweight HTML extraction when RSS is unavailable, unstable, overly generic, or insufficient for the FII-specific use case.
- **Official Behavioral Social Source**: Reddit, used as a public behavioral discussion layer for sentiment and engagement analysis rather than as an editorial publisher.

## Acquisition strategy

The repository follows an **RSS-first, lightweight-scraping-second, frozen-real-dataset-fallback-third** acquisition policy.

RSS is preferred whenever possible because it is easier to monitor, lighter to maintain, and better suited to reproducible periodic ingestion. When RSS is not available or does not provide sufficient topical precision, the project falls back to controlled extraction from public HTML pages. For behavioral discussion data, especially Reddit, the platform uses API-based collection when appropriate and may also rely on frozen reproducible datasets for demonstrations, academic validation, and operational resilience.

## Acquisition types

The collection layer uses the following acquisition types:

- **RSS ingestion**: structured collection from public XML or feed endpoints.
- **Listing-page HTML scraping**: extraction of article links and metadata from category pages, rankings, hub pages, or portal listings.
- **Article-page structured extraction**: extraction of title, date, URL, source, and cleaned text body from individual article pages after discovery.
- **API-based social collection**: retrieval of public discussion data from behavioral platforms such as Reddit.
- **Frozen dataset fallback**: reproducible stored datasets used when live collection is unavailable, unstable, or unnecessary for demonstration purposes.

## Official sources table

The table below presents the normalized set of monitored sources used by the repository. To preserve internal consistency across the documentation, the project adopts a total of 21 monitored sources: 20 financial/editorial sources and Reddit as the behavioral social source.

| # | Official source name | Official group | Recommended acquisition type |
|---|---|---|---|
| 1 | InfoMoney | Official Editorial RSS Source | RSS ingestion |
| 2 | Valor Investe | Official Editorial RSS Source | RSS ingestion |
| 3 | Money Times | Official Editorial RSS Source | RSS ingestion |
| 4 | Seu Dinheiro | Official Editorial RSS Source | RSS ingestion |
| 5 | Exame | Official Editorial RSS Source | RSS ingestion |
| 6 | CNN Brasil Business | Official Editorial RSS Source | RSS ingestion |
| 7 | Funds Explorer | Official Editorial Scraping Source | Listing-page HTML scraping |
| 8 | Status Invest | Official Editorial Scraping Source | Listing-page HTML scraping |
| 9 | Clube FII | Official Editorial Scraping Source | Listing-page HTML scraping |
| 10 | FIIs.com.br | Official Editorial Scraping Source | Listing-page HTML scraping |
| 11 | The Cap | Official Editorial Scraping Source | Listing-page HTML scraping |
| 12 | Investidor10 | Official Editorial Scraping Source | Listing-page HTML scraping |
| 13 | Eu Quero Investir | Official Editorial Scraping Source | Listing-page HTML scraping |
| 14 | Suno Research | Official Editorial RSS Source | RSS ingestion |
| 15 | Bora Investir | Official Editorial Scraping Source | Listing-page HTML scraping |
| 16 | E-Investidor Estadão | Official Editorial RSS Source | RSS ingestion |
| 17 | NeoFeed | Official Editorial RSS Source | RSS ingestion |
| 18 | TradeMap | Official Editorial Scraping Source | Listing-page HTML scraping |
| 19 | Investing.com Brasil | Official Editorial RSS Source | RSS ingestion |
| 20 | Inteligência Financeira | Official Editorial Scraping Source | Listing-page HTML scraping |
| 21 | Reddit | Official Behavioral Social Source | API-based social collection / frozen dataset fallback |

## Technical interpretation

Not all monitored sources should be treated identically from an ingestion perspective. Some are better suited to feed-based collection, while others are more appropriate for lightweight extraction from listing pages and article pages. The classification is therefore methodological rather than merely descriptive: it exists to preserve consistency, reproducibility, and maintainability across the data pipeline.

This distinction is especially important because the repository is designed as a governed analytical system rather than as a loose collection of scraping scripts. By documenting source classes and preferred acquisition paths explicitly, the project improves traceability, supports future expansion, and makes the architecture easier to evaluate in both academic and production-oriented contexts.

## Reproducibility note

Source availability may change over time because feed endpoints can be modified, HTML structures can evolve, and public platform access conditions may shift. For this reason, the repository includes a frozen real dataset strategy to preserve reproducibility for experiments, presentations, validation workflows, and technical review.


