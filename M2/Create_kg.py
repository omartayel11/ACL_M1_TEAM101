#!/usr/bin/env python3
"""
create_kg.py
Reads CSV files (hotels.csv, reviews.csv, users.csv, visa.csv) from the same directory,
then builds the knowledge graph in Neo4j following the exact schema in the milestone PDF.

Progress prints are included so you can see where the script is during execution.
"""

import os
import sys
import pandas as pd
from neo4j import GraphDatabase
from datetime import datetime

# -------------------------
# Utility: read config.txt
# -------------------------
def read_config(path="config.txt"):
    config = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"config.txt not found in current directory ({os.getcwd()}). Expected file containing: URI, USERNAME, PASSWORD")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                config[k.strip().upper()] = v.strip()
    required = ["URI", "USERNAME", "PASSWORD"]
    for r in required:
        if r not in config:
            raise KeyError(f"Missing {r} in config.txt")
    return config

# -------------------------
# Create session helper
# -------------------------
def get_driver(cfg):
    uri = cfg["URI"]
    user = cfg["USERNAME"]
    pwd = cfg["PASSWORD"]
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    return driver

# -------------------------
# Clear existing DB (optional)
# -------------------------
def clear_db(tx):
    # Remove all nodes and relationships
    tx.run("MATCH (n) DETACH DELETE n")

# -------------------------
# Cypher helper: create constraints
# -------------------------
def create_constraints(tx):
    # Constraints / uniqueness according to schema
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Traveller) REQUIRE t.user_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hotel) REQUIRE h.hotel_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:City) REQUIRE c.name IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (co:Country) REQUIRE co.name IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Review) REQUIRE r.review_id IS UNIQUE")

# -------------------------
# Main KG creation function
# -------------------------
def build_kg(driver, hotels_df, reviews_df, users_df, visa_df):
    with driver.session() as session:
        print("[1/9] Clearing database (will delete existing graph nodes/relationships)...")
        session.execute_write(clear_db)

        print("[2/9] Creating uniqueness constraints...")
        session.execute_write(create_constraints)

        # Create Country nodes (from hotels country and users country and visa from/to)
        all_countries = set(hotels_df['country'].dropna().unique().tolist() +
                            users_df['country'].dropna().unique().tolist() +
                            visa_df['from'].dropna().unique().tolist() +
                            visa_df['to'].dropna().unique().tolist())
        print(f"[3/9] Creating Country nodes: {len(all_countries)} countries found...")
        def create_countries(tx, countries):
            for name in countries:
                tx.run("MERGE (c:Country {name: $name})", name=str(name))
        session.execute_write(create_countries, list(all_countries))

        # Create City nodes and connect City -> Country
        print("[4/9] Creating City nodes and connecting City -> Country...")
        def create_cities(tx, hotels):
            for _, row in hotels.iterrows():
                city = str(row['city'])
                country = str(row['country'])
                tx.run("""
                    MERGE (ci:City {name: $city})
                    MERGE (co:Country {name: $country})
                    MERGE (ci)-[:LOCATED_IN]->(co)
                """, city=city, country=country)
        session.execute_write(create_cities, hotels_df)

        # Create Hotel nodes and connect Hotel -> City
        print("[5/9] Creating Hotel nodes...")
        def create_hotels(tx, hotels):
            for _, row in hotels.iterrows():
                tx.run("""
                    MERGE (h:Hotel {hotel_id: $hotel_id})
                    SET h.name = $name,
                        h.star_rating = toFloat($star_rating),
                        h.cleanliness_base = toFloat($cleanliness_base),
                        h.comfort_base = toFloat($comfort_base),
                        h.facilities_base = toFloat($facilities_base),
                        h.location_base = CASE WHEN $location_base IS NULL THEN null ELSE toFloat($location_base) END,
                        h.staff_base = CASE WHEN $staff_base IS NULL THEN null ELSE toFloat($staff_base) END,
                        h.value_for_money_base = CASE WHEN $value_for_money_base IS NULL THEN null ELSE toFloat($value_for_money_base) END
                    WITH h
                    MATCH (ci:City {name: $city})
                    MERGE (h)-[:LOCATED_IN]->(ci)
                """, hotel_id=str(row['hotel_id']),
                     name=str(row['hotel_name']),
                     star_rating=row.get('star_rating', None),
                     cleanliness_base=row.get('cleanliness_base', None),
                     comfort_base=row.get('comfort_base', None),
                     facilities_base=row.get('facilities_base', None),
                     location_base=row.get('location_base', None),
                     staff_base=row.get('staff_base', None),
                     value_for_money_base=row.get('value_for_money_base', None),
                     city=str(row['city']))
        session.execute_write(create_hotels, hotels_df)

        # Create Traveller nodes and FROM_COUNTRY relationship
        print("[6/9] Creating Traveller nodes and FROM_COUNTRY relationships...")
        def create_travellers(tx, users):
            for _, row in users.iterrows():
                uid = str(row['user_id'])
                gender = row.get('user_gender')  
                age_group = row.get('age_group')
                traveller_type = row.get('traveller_type')
                country = row.get('country')
                join_date = row.get('join_date', None)
                tx.run("""
                    MERGE (t:Traveller {user_id: $uid})
                    SET t.gender = $gender,
                        t.age = $age_group,
                        t.type = $traveller_type,
                        t.join_date = $join_date
                    WITH t
                    MERGE (co:Country {name: $country})
                    MERGE (t)-[:FROM_COUNTRY]->(co)
                """, uid=uid, gender=str(gender) if pd.notna(gender) else None,
                     age_group=str(age_group) if pd.notna(age_group) else None,
                     traveller_type=str(traveller_type) if pd.notna(traveller_type) else None,
                     join_date=str(join_date) if pd.notna(join_date) else None,
                     country=str(country) if pd.notna(country) else None)
        session.execute_write(create_travellers, users_df)

        # Create Review nodes, WROTE and REVIEWED relationships and STAYED_AT relationships
        print("[7/9] Creating Review nodes and connecting Traveller->Review->Hotel and Traveller->STAYED_AT->Hotel...")
        # We'll iterate reviews in chunks for memory safety
        def create_reviews_batch(tx, reviews):
            for _, row in reviews.iterrows():
                rid = str(row['review_id'])
                uid = str(row['user_id'])
                hid = str(row['hotel_id'])
                review_date = row.get('review_date')
                # Some scores might be empty/NaN
                def safe(v):
                    return None if pd.isna(v) else float(v)
                props = {
                    'review_id': rid,
                    'text': str(row['review_text']) if not pd.isna(row.get('review_text')) else None,
                    'date': str(review_date) if not pd.isna(review_date) else None,
                    'score_overall': safe(row.get('score_overall')),
                    'score_cleanliness': safe(row.get('score_cleanliness')),
                    'score_comfort': safe(row.get('score_comfort')),
                    'score_facilities': safe(row.get('score_facilities')),
                    'score_location': safe(row.get('score_location')),
                    'score_staff': safe(row.get('score_staff')),
                    'score_value_for_money': safe(row.get('score_value_for_money')),
                }
                tx.run("""
                    MERGE (r:Review {review_id: $review_id})
                    SET r.text = $text,
                        r.date = $date,
                        r.score_overall = $score_overall,
                        r.score_cleanliness = $score_cleanliness,
                        r.score_comfort = $score_comfort,
                        r.score_facilities = $score_facilities,
                        r.score_location = $score_location,
                        r.score_staff = $score_staff,
                        r.score_value_for_money = $score_value_for_money
                    WITH r
                    MATCH (t:Traveller {user_id: $uid})
                    MERGE (t)-[:WROTE]->(r)
                    WITH r
                    MATCH (h:Hotel {hotel_id: $hid})
                    MERGE (r)-[:REVIEWED]->(h)
                    WITH r
                    MATCH (t2:Traveller {user_id: $uid}), (h2:Hotel {hotel_id: $hid})
                    MERGE (t2)-[:STAYED_AT]->(h2)
                """, **props, uid=uid, hid=hid)
        # Run in chunks
        batch = 5000
        total_reviews = len(reviews_df)
        for start in range(0, total_reviews, batch):
            end = min(start + batch, total_reviews)
            print(f"    - Processing reviews {start+1}..{end} of {total_reviews} ...")
            chunk = reviews_df.iloc[start:end]
            session.execute_write(create_reviews_batch, chunk)

        # Compute average_reviews_score per Hotel and set property on Hotel
        print("[8/9] Computing average_reviews_score for each Hotel and updating Hotel nodes...")
        # We'll compute in pandas then push results
        avg_by_hotel = reviews_df.groupby('hotel_id')['score_overall'].mean().reset_index()
        avg_by_hotel = avg_by_hotel.rename(columns={'score_overall':'avg_score_overall'})
        def set_avg_scores(tx, records):
            for _, row in records.iterrows():
                hid = str(row['hotel_id'])
                avg = float(row['avg_score_overall']) if not pd.isna(row['avg_score_overall']) else None
                tx.run("MATCH (h:Hotel {hotel_id: $hid}) SET h.average_reviews_score = $avg", hid=hid, avg=avg)
        session.execute_write(set_avg_scores, avg_by_hotel)

        # Create visa relationships from visa_df
        print("[9/9] Creating visa relationships between countries (Country)-[:NEEDS_VISA]->(Country) ...")
        def set_visa(tx, visas):
            for _, row in visas.iterrows():
                frm = row['from']
                to = row['to']
                requires = row.get('requires_visa')
                vtype = row.get('visa_type', None)
                # interpret boolean-ish fields
                req_bool = None
                if pd.notna(requires):
                    if isinstance(requires, str):
                        req_lower = requires.strip().lower()
                        req_bool = req_lower in ("1","true","yes","y","t")
                    else:
                        req_bool = bool(requires)
                if req_bool:
                    tx.run("""
                        MERGE (a:Country {name: $frm})
                        MERGE (b:Country {name: $to})
                        MERGE (a)-[r:NEEDS_VISA]->(b)
                        SET r.visa_type = $vtype
                    """, frm=str(frm), to=str(to), vtype=str(vtype) if pd.notna(vtype) else None)
                else:
                    # Optionally create an explicit relationship for requires=false? The schema
                    # requires only Country-[:NEEDS_VISA]->Country with property visa_type,
                    # so we only create relationships where requires=true.
                    pass
        session.execute_write(set_visa, visa_df)

        print("Knowledge graph build completed successfully.")

# -------------------------
# Main guard
# -------------------------
def main():
    print("Starting create_kg.py")
    # Read config
    try:
        cfg = read_config("config.txt")
    except Exception as e:
        print(f"Failed to read config.txt: {e}")
        sys.exit(1)

    # Load CSVs
    required_files = ["hotels.csv", "reviews.csv", "users.csv", "visa.csv"]
    print("Checking CSV files in current directory:", os.getcwd())
    for f in required_files:
        if not os.path.exists(f):
            print(f"ERROR: required CSV file '{f}' not found in current directory.")
            sys.exit(1)

    print("Reading CSVs into pandas dataframes (this may take a few seconds)...")
    hotels_df = pd.read_csv("hotels.csv")
    reviews_df = pd.read_csv("reviews.csv")
    users_df = pd.read_csv("users.csv")
    visa_df = pd.read_csv("visa.csv")

    # Basic validations
    print("Performing basic validation checks...")
    print(f"  hotels.csv rows: {len(hotels_df)}")
    print(f"  reviews.csv rows: {len(reviews_df)}")
    print(f"  users.csv rows: {len(users_df)}")
    print(f"  visa.csv rows: {len(visa_df)}")

    # Connect to Neo4j
    print("Connecting to Neo4j...")
    try:
        driver = get_driver(cfg)
    except Exception as e:
        print(f"Failed to create Neo4j driver: {e}")
        sys.exit(1)

    try:
        build_kg(driver, hotels_df, reviews_df, users_df, visa_df)
    finally:
        driver.close()
        print("Closed Neo4j driver. Script finished.")

if __name__ == "__main__":
    main()
