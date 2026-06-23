# Legacy Topic Accuracy Evaluation

The old two-step `TopicExtractor` evaluation script was removed from the
production test/runtime path as part of feature
`026-simplify-metadata-pipeline`.

Production topic extraction now uses the flat `TaggingService` path only. If a
historical comparison is needed, recover the old script from git history and run
it outside the `archivatorium/` package and `tests/` tree so it cannot define or
assert production behaviour.
