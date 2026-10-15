# Security & responsible use

This repository is a **self-contained public laboratory** built from fictional names and generated data. It does not contain customer source code, infrastructure references, real credentials, private datasets, employment documents or production database exports.

The CLI does **not** connect to SQL Server or Oracle. Any SQL file under `sql/` is illustrative and must be reviewed before execution, even in test environments. Do not execute examples against production systems.

## Responsible testing

- Use only authorized, disposable sandbox schemas.
- Never paste credentials into source control or issue reports.
- Treat static assessment findings as advisory, not a security certification.
- Validate database privilege requirements and rollback paths before manual SQL tests.
- Do not upload real customer data to reproduce bugs; produce a minimized synthetic case.

## Reporting concerns

If you identify a security issue in this demonstration, do not include secrets or identifying logs in a public issue. Contact the repository maintainer using an appropriate private channel.
