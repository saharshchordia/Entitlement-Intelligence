# Research Methodology

This folder contains reusable methodology for municipal entitlement intelligence.

Files:

- `municipal_entitlement_hardening_playbook.md` - AI-executable workflow for hardening and refreshing a municipality or market packet, including meeting-media transcription.
- `data_model_and_diagrams.md` - database-oriented data model, ERD, data lineage, refresh model, transcript model, and confidence ladder.
- `schema_reference.sql` - Postgres/Supabase-style relational schema reference.

Recommended use:

1. Start with the playbook.
2. Use the data model to keep case, parcel, action, source, meeting recording, transcript, evidence, participant, refresh, and gap records separate.
3. Use the SQL schema as the target structure when the CSV/workbook workflow is migrated into a real database.
