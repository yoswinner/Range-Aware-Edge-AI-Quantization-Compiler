"""Source locations, compiler errors and per-value diagnostic reports.

Deliberately does not import ``report`` here: ``report`` depends on the analysis
and quantization stages, while the low-level modules (``location``, ``errors``)
are imported by every stage. Importing ``report`` eagerly would create cycles.
"""
