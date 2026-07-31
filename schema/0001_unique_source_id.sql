-- Required by the ON CONFLICT clause in pipeline/load.py.
-- Apply once per warehouse before deploying the upsert; the pipeline will fail with
-- "there is no unique or exclusion constraint matching the ON CONFLICT specification"
-- until this has run.
--
-- Deduplicate first: rows loaded before the upsert may already contain repeats.

DELETE FROM warehouse.orders a
      USING warehouse.orders b
      WHERE a.ctid < b.ctid
        AND a.source_id = b.source_id;

ALTER TABLE warehouse.orders
        ADD CONSTRAINT orders_source_id_key UNIQUE (source_id);

DELETE FROM warehouse.refunds a
      USING warehouse.refunds b
      WHERE a.ctid < b.ctid
        AND a.source_id = b.source_id;

ALTER TABLE warehouse.refunds
        ADD CONSTRAINT refunds_source_id_key UNIQUE (source_id);
