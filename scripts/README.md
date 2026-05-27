# Scripts

This directory contains first-class repo support tooling for the Waymark/Cartenza alpha.

## What Belongs Here

- Validators for app resources, Atlas contracts, survey evidence, canonical graph contracts, and generated packets.
- Generators that turn accepted `data/` contracts or fixtures into app resources, packets, review material, or harness inputs.
- Smoke and diagnostic tools for Supabase, live mission generation, Atlas ingestion, and alpha support workflows.
- Reporting utilities that summarize generated outputs into reviewable Markdown or JSON.

## What Does Not Belong Here

- Generated outputs.
- Local API responses.
- Timestamped run directories.
- Secrets, `.env` files, or machine-local cache/build products.

Generated artifacts should land in the documented `data/`, `review_packets/`, harness `outputs/`, or local export paths and then be classified before tracking. Scripts that require live services must read credentials from environment variables and must not print secret values.
