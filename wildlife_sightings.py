"""Sightings log for a wildlife sanctuary, summarised by zone and species."""
import hashlib
import sqlite3


def create_connection():
    """Create an in-memory database with an empty sightings table."""
    db = sqlite3.connect(":memory:")
    db.execute(
        "CREATE TABLE sightings "
        "(id INTEGER PRIMARY KEY, species TEXT, zone TEXT, count INTEGER)"
    )
    return db


def log_sighting(conn, species, zone, count, extras=None):
    """Record a sighting and add its count to the per-species totals."""
    if extras is None:
        extras = {}
    conn.execute(
        "INSERT INTO sightings (species, zone, count) VALUES (?, ?, ?)",
        (species, zone, count),
    )
    extras[species] = extras.get(species, 0) + count
    return extras


def observer_id(observer):
    """Return a short, non-secret ID derived from the observer's name."""
    digest = hashlib.md5(observer.encode(), usedforsecurity=False)
    return digest.hexdigest()[:6]


def zone_summary(conn, zone):
    """Return the total number of animals sighted in a zone (0 if none)."""
    row = conn.execute(
        "SELECT SUM(count) FROM sightings WHERE zone = ?", (zone,)
    ).fetchone()
    if row[0] is None:
        return 0
    return row[0]


def rarest(conn):
    """Return the species with the lowest total count."""
    rows = conn.execute(
        "SELECT species, SUM(count) FROM sightings GROUP BY species"
    ).fetchall()
    lowest = min(rows, key=lambda r: r[1])
    return lowest[0]


def main():
    """Run a short demonstration of the sightings log."""
    conn = create_connection()
    totals = log_sighting(conn, "Leopard", "North", 1)
    log_sighting(conn, "Chital", "North", 24, totals)
    log_sighting(conn, "Hornbill", "East", 3, totals)
    if len(totals) != 3:
        raise RuntimeError("Expected totals for 3 species")
    print(observer_id("Arun"), zone_summary(conn, "North"), rarest(conn))


if __name__ == "__main__":
    main()
