def add_node(label, value, driver):
    if label == "Organization":
        records, summary, keys = driver.execute_query("""
                MERGE (p:Organization {value: $value})
                """, value=value,
                                                      database_="neo4j",
                                                      )
    elif label == "Time":
        records, summary, keys = driver.execute_query("""
                MERGE (p:Time {value: $value})
                """, value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Product":
        records, summary, keys = driver.execute_query("""
                MERGE (p:Product {value: $value})
                """, value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Promotion":
        records, summary, keys = driver.execute_query("""
               MERGE (p:Promotion {value: $value})
               """, value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Regulation":
        records, summary, keys = driver.execute_query("""
            MERGE (p:Regulation {value: $value})
            """, value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Location":
        records, summary, keys = driver.execute_query("""
                    MERGE (p:Location {value: $value})
                    """, value=value,
                    database_="neo4j",
                    )

    elif label == "Price":
        records, summary, keys = driver.execute_query("""
            MERGE (p:Price {value: $value})
            """, value=value,
                                                      database_="neo4j",
                                                      )


def add_node_2(label, value, driver):
    if label == "Organization":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Organization {value: $init})
                MERGE (p:Organization {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='Organization', value=value,
                                                      database_="neo4j",
                                                      )
    elif label == "Time":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Time {value: $init})
                MERGE (p:Time {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='Time', value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Product":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Product {value: $init})
                MERGE (p:Product {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='Product', value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Promotion":
        records, summary, keys = driver.execute_query("""
               MATCH (init:Promotion {value: $init})
               MERGE (p:Promotion {value: $value})
               MERGE (init)-[:INIT]->(p)
               """, init='Promotion', value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Regulation":
        records, summary, keys = driver.execute_query("""
            MATCH (init:Regulation {value: $init})
            MERGE (p:Regulation {value: $value})
            MERGE (init)-[:INIT]->(p)
            """, init='Regulation', value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Location":
        records, summary, keys = driver.execute_query("""
                    MATCH (init:Location {value: $init})
                    MERGE (p:Location {value: $value})
                    MERGE (init)-[:INIT]->(p)
                    """, init='Location', value=value,
                                                      database_="neo4j",
                                                      )

    elif label == "Price":
        records, summary, keys = driver.execute_query("""
            MATCH (init:Price {value: $init})
            MERGE (p:Price {value: $value})
            MERGE (init)-[:INIT]->(p)
            """, init='Price', value=value,
                                                      database_="neo4j",
                                                      )


def add_relation(label_1, value_1, relation, label_2, value_2, driver):
    # print("Relation: " + label_1 + " - " + relation + " - " + label_2)
    ############### Affiliation ###########################################

    if label_1 == "Time" and label_2 == "Regulation":
        # print("Relation: Time - Regulation - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:AFFILIATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Promotion":
        # print("Relation: Promotion - Promotion - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:AFFILIATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Product" and label_2 == "Promotion":
        # print("Relation: Product - Promotion - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:AFFILIATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Time":
        # print("Relation: Promotion - Time - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Time {value: $value_2})
                                MERGE (start)-[:AFFILIATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Product" and label_2 == "Time":
        # print("Relation: Product - Time - Affiliation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Time {value: $value_2})
                                MERGE (start)-[:AFFILIATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )

    #################### Regulation ##############################################
    elif label_1 == "Product" and label_2 == "Regulation":
        # print("Relation: Product - Regulation - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Product {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:REGULATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Regulation":
        # print("Relation: Promotion - Regulation - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Regulation {value: $value_2})
                                MERGE (start)-[:REGULATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Time" and label_2 == "Product":
        # print("Relation: Time - Product - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:REGULATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Time" and label_2 == "Promotion":
        # print("Relation: Time - Promotion - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Time {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:REGULATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Regulation" and label_2 == "Price":
        # print("Relation: Regulation - Price - Regulation")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Regulation {value: $value_1})
                                MATCH (end:Price {value: $value_2})
                                MERGE (start)-[:REGULATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
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
                                MERGE (start)-[:LOCATION]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )

    ###################### Price #################################################
    elif label_1 == "Price" and label_2 == "Product":
        # print("Relation: Price - Product - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Price {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:PRICE]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Price" and label_2 == "Promotion":
        # print("Relation: Price - Promotion - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Price {value: $value_1})
                                MATCH (end:Promotion {value: $value_2})
                                MERGE (start)-[:PRICE]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    elif label_1 == "Promotion" and label_2 == "Product":
        # print("Relation: Promotion - Product - Price")
        records, summary, keys = driver.execute_query("""
                                MATCH (start:Promotion {value: $value_1})
                                MATCH (end:Product {value: $value_2})
                                MERGE (start)-[:PRICE]->(end)
                                """,
                                                      value_1=value_1,
                                                      value_2=value_2,
                                                      database_="neo4j",
                                                      )
    else:
        print("Relation: " + label_1 + " - " + "UNKNOWN" + " - " + label_2)


def make_sense(driver):
    records, summary, keys = driver.execute_query(
        "MERGE (p:Organization {value: $init})",
        init='Organization',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Time {value: $init})",
        init='Time',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Product {value: $init})",
        init='Product',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Promotion {value: $init})",
        init='Promotion',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Regulation {value: $init})",
        init='Regulation',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='Location',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query(
        "MERGE (p:Price {value: $init})",
        init='Price',
        database_="neo4j",
    )


# TODO: Store name and node name
def add_node_3(label, value, driver, store_name):

    parent = "_" + store_name

    if label == "Organization":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Organization {value: $init})
                MERGE (p:Organization {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='Organization', value=value,
                database_="neo4j",
                )

    elif label == "Time":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Property {value: $init})
                MERGE (p:Time {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='time' + parent, value=value,
                database_="neo4j",
                )

    elif label == "Product":
        records, summary, keys = driver.execute_query("""
                MATCH (init:Property {value: $init})
                MERGE (p:Product {value: $value})
                MERGE (init)-[:INIT]->(p)
                """, init='product' + parent, value=value,
                database_="neo4j",
                )

    elif label == "Promotion":
        records, summary, keys = driver.execute_query("""
               MATCH (init:Property {value: $init})
               MERGE (p:Promotion {value: $value})
               MERGE (init)-[:INIT]->(p)
               """, init='promotion' + parent, value=value,
               database_="neo4j",
            )

    elif label == "Regulation":
        records, summary, keys = driver.execute_query("""
            MATCH (init:Property {value: $init})
            MERGE (p:Regulation {value: $value})
            MERGE (init)-[:INIT]->(p)
            """, init='regulation' + parent, value=value,
            database_="neo4j",
            )

    elif label == "Location":
        records, summary, keys = driver.execute_query("""
                    MERGE (p:Location {value: $value})
                    """, init='Location', value=value,
                    database_="neo4j",
                    )

    elif label == "Price":
        records, summary, keys = driver.execute_query("""
            MATCH (init:Property {value: $init})
            MERGE (p:Price {value: $value})
            MERGE (init)-[:INIT]->(p)
            """, init='price' + parent, value=value,
            database_="neo4j",
            )

def initGraph(driver):
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='LOCATION',
        database_="neo4j",
    )

    # Winmart
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='winmart',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='winmart',
                                                  value2='price_winmart',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='winmart',
                                                  value2='product_winmart',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='winmart',
                                                  value2='promotion_winmart',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='winmart',
                                                  value2='regulation_winmart',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_winmart',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='winmart',
                                                  value2='time_winmart',
                                                  database_="neo4j",
                                                  )

    # 711
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='7-eleven',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='7-eleven',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_711',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='7-eleven',
                                                  value2='price_711',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_711',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='7-eleven',
                                                  value2='product_711',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_711',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='7-eleven',
                                                  value2='promotion_711',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_711',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='7-eleven',
                                                  value2='regulation_711',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_711',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='7-eleven',
                                                  value2='time_711',
                                                  database_="neo4j",
                                                  )

    # circle - k
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='circle-k',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='circle-k',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_ciclek',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='circle-k',
                                                  value2='price_ciclek',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_ciclek',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='circle-k',
                                                  value2='product_ciclek',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_ciclek',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='circle-k',
                                                  value2='promotion_ciclek',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_ciclek',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='circle-k',
                                                  value2='regulation_ciclek',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_ciclek',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='circle-k',
                                                  value2='time_ciclek',
                                                  database_="neo4j",
                                                  )

    # lotte
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='lotte',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='lotte',
                                                  value2='price_lotte',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='lotte',
                                                  value2='product_lotte',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='lotte',
                                                  value2='promotion_lotte',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='lotte',
                                                  value2='regulation_lotte',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_lotte',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='lotte',
                                                  value2='time_lotte',
                                                  database_="neo4j",
                                                  )

    # top market
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='top market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='top market',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_top_market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='top market',
                                                  value2='price_top_market',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_top_market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='top market',
                                                  value2='product_top_market',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_top_market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='top market',
                                                  value2='promotion_top_market',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_top_market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='top market',
                                                  value2='regulation_top_market',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_top_market',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='top market',
                                                  value2='time_top_market',
                                                  database_="neo4j",
                                                  )

    # aeon
    records, summary, keys = driver.execute_query(
        "MERGE (p:Location {value: $init})",
        init='aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Location {value: $value2})
                                    MERGE (start)-[:LOCATION]->(end)
                                    """,
                                                  value1='LOCATION',
                                                  value2='aeon',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='price_aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                    MATCH (start:Location {value: $value1})
                                    MATCH (end:Property {value: $value2})
                                    MERGE (start)-[:PRICE]->(end)
                                    """,
                                                  value1='aeon',
                                                  value2='price_aeon',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='product_aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                        MATCH (start:Location {value: $value1})
                                        MATCH (end:Property {value: $value2})
                                        MERGE (start)-[:PRODUCT]->(end)
                                        """,
                                                  value1='aeon',
                                                  value2='product_aeon',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='promotion_aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                            MATCH (start:Location {value: $value1})
                                            MATCH (end:Property {value: $value2})
                                            MERGE (start)-[:PROMOTION]->(end)
                                            """,
                                                  value1='aeon',
                                                  value2='promotion_aeon',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='regulation_aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                MATCH (start:Location {value: $value1})
                                                MATCH (end:Property {value: $value2})
                                                MERGE (start)-[:REGULATION]->(end)
                                                """,
                                                  value1='aeon',
                                                  value2='regulation_aeon',
                                                  database_="neo4j",
                                                  )

    records, summary, keys = driver.execute_query(
        "MERGE (p:Property {value: $init})",
        init='time_aeon',
        database_="neo4j",
    )
    records, summary, keys = driver.execute_query("""
                                                    MATCH (start:Location {value: $value1})
                                                    MATCH (end:Property {value: $value2})
                                                    MERGE (start)-[:TIME]->(end)
                                                    """,
                                                  value1='aeon',
                                                  value2='time_aeon',
                                                  database_="neo4j",
                                                  )
