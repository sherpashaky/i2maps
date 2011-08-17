import django.contrib.gis.geos as geos
import psycopg2
import psycopg2.extras

import i2maps

psycopg2.extensions.register_adapter(geos.Point, str)
psycopg2.extensions.register_adapter(geos.Polygon, str)
psycopg2.extensions.register_adapter(geos.GeometryCollection, str)
psycopg2.extensions.register_adapter(geos.LineString, str)
psycopg2.extensions.register_adapter(geos.LinearRing, str)
psycopg2.extensions.register_adapter(geos.MultiLineString, str)
psycopg2.extensions.register_adapter(geos.MultiPoint, str)
psycopg2.extensions.register_adapter(geos.MultiPolygon, str)



class Postgres():
    geom_oid = None
    
    def __init__(self, config):
        self.connection = psycopg2.connect(config)
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        global geom_oid        
        if not geom_oid:
            try:
                cur = self.query("select st_point(1.0, 1.0)")
                geom_oid = cur.description[0][1]
                convertor = psycopg2.extensions.new_type((geom_oid,), "GEOMETRY", lambda v, c: geos.GEOSGeometry(v))
                psycopg2.extensions.register_type(convertor)
            except Exception, e:
                print("Warning: This database does not seem to have the PostGIS functions installed")
    
    def query(self, query, params=()):
        try:
            cur = self.cursor
            cur.execute(query, params)
            return cur
        except Exception, e:
            self.connection.rollback()
            raise e
    
    def modify(self, query, params=()):
        try:
            cur = self.cursor
            cur.execute(query, params)
            self.connection.commit()
        except Exception, e:
            self.connection.rollback()
            raise e
    
    def has_table(self, table):
        tables = self.query("select tablename from pg_tables where schemaname='public' and tablename=%s", [table])
        return len(tables) > 0
        
