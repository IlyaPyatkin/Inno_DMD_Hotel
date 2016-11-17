from app.model.DBQuery import DBQuery


class Performance:
    @staticmethod
    def get_io_cache_performance():
        return DBQuery("""SELECT relname,
                          sum(idx_blks_read) as idx_read,
                          sum(idx_blks_hit)  as idx_hit,
                          round((sum(idx_blks_hit) - sum(idx_blks_read)) / (sum(idx_blks_hit)+1), 2) as idx_ratio
                          FROM pg_statio_user_tables
                          GROUP BY relname
                          ORDER BY relname;""")

    @staticmethod
    def get_io_index_performance():
        return DBQuery("""SELECT relname,
                          sum(heap_blks_read) as heap_read,
                          sum(heap_blks_hit)  as heap_hit,
                          round(sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read) + 1),2) as heap_ratio
                          FROM pg_statio_user_tables
                          GROUP BY relname
                          ORDER BY relname;""")

    @staticmethod
    def get_disk_performance():
        return DBQuery("""SELECT TABLE_NAME,
                          pg_size_pretty(index_bytes) AS INDEX,
                          pg_size_pretty(table_bytes) AS TABLE,
                          pg_size_pretty(total_bytes) AS total
                          FROM (
                               SELECT
                                 *, total_bytes - index_bytes - COALESCE(toast_bytes, 0) AS table_bytes
                               FROM (   SELECT
                                        relname                               AS TABLE_NAME,
                                        pg_total_relation_size(c.oid)         AS total_bytes,
                                        pg_indexes_size(c.oid)                AS index_bytes,
                                        pg_total_relation_size(reltoastrelid) AS toast_bytes
                                      FROM pg_class c
                                        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                                      WHERE relkind = 'r' AND nspname = 'public'
                                    ) a
                             ) a
                            ORDER BY TABLE_NAME;""")
