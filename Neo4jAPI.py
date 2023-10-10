def add_node(label, value, driver):
    if label == "Organization":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Organization {value: $value})",
            value=value,
            database_="neo4j",
        )
    elif label == "Time":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Time {value: $value})",
            value=value,
            database_="neo4j",
        )

    elif label == "Product":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Product {value: $value})",
            value=value,
            database_="neo4j",
        )

    elif label == "Promotion":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Promotion {value: $value})",
            value=value,
            database_="neo4j",
        )

    elif label == "Regulation":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Regulation {value: $value})",
            value=value,
            database_="neo4j",
        )

    elif label == "Location":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Location {value: $value})",
            value=value,
            database_="neo4j",
        )

    elif label == "Price":
        records, summary, keys = driver.execute_query(
            "MERGE (p:Price {value: $value})",
            value=value,
            database_="neo4j",
        )


def add_relation(label_1, value_1, relation, label_2, value_2, driver):
    print("Relation: " + label_1 + " - " + relation + " - " + label_2)
    ############### Affiliation ###########################################

    if label_1 == "Time" and label_2 == "Regulation":
        print("Relation: Time - Regulation - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:Affiliation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Promotion":
        print("Relation: Promotion - Promotion - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:Affiliation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Product" and label_2 == "Promotion":
        print("Relation: Product - Promotion - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:Affiliation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Time":
        print("Relation: Promotion - Time - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Time {value: $value_2})
                                MERGE (start)-[:Affiliation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Product" and label_2 == "Time":
        print("Relation: Product - Time - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Time {value: $value_2})
                                MERGE (start)-[:Affiliation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )

    #################### Regulation ##############################################
    elif label_1 == "Product" and label_2 == "Regulation":
        print("Relation: Product - Regulation - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:Regulation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Regulation":
        print("Relation: Promotion - Regulation - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:Regulation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Time" and label_2 == "Product":
        print("Relation: Time - Product - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:Regulation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Time" and label_2 == "Promotion":
        print("Relation: Time - Promotion - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:Regulation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Regulation" and label_2 == "Price":
        print("Relation: Regulation - Price - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Regulation {value: $value_1})
                                MATCH (end:Price {value: $value_2})
                                MERGE (start)-[:Regulation]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )

    ######################## Location ##############################################
    elif label_1 == "Organization" and label_2 == "Location":
        print("Relation: Organization - Location - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Organization {value: $value_1})
                                MATCH (end:Location {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Location":
        print("Relation: Promotion - Location - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Location {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Product" and label_2 == "Location":
        print("Relation: Product - Location - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Location {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Organization" and label_2 == "Promotion":
        print("Relation: Organization - Promotion - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Organization {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Organization" and label_2 == "Product":
        print("Relation: Organization - Product - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Organization {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Location" and label_2 == "Location":
        print("Relation: Location - Location - Location")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Location {value: $value_1})
                                MATCH (end:Location {value: $value_2})
                                MERGE (start)-[:Location]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    ###################### Price #################################################
    elif label_1 == "Price" and label_2 == "Product":
        print("Relation: Price - Product - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Price {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:Price]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Price" and label_2 == "Promotion":
        print("Relation: Price - Promotion - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Price {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:Price]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Product":
        print("Relation: Promotion - Product - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:Price]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    else:
        print("Relation: " + label_1 + " - " + "UNKNOWN" + " - " + label_2)
