from neo4j import GraphDatabase

### Entity type:
# • Organization:
# • Time
# • Product
# • Promotion
# • Regulation
# • Location
# • Price
###

### Relation type
# Affiliation
# Regulation
# Location
# Price
###

class Neo:
    def __init__(self, username, pwd):
        self.driver = GraphDatabase.driver(uri="neo4j://localhost:7687", auth=(username, pwd))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_single_node(self, node_name, label):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._CREATE, node_name, label)

    @staticmethod
    def _CREATE(tx, node_name, label):
        neo = Neo("neo4j", "1")
        # print(node_name + " " + label)
        if label == "medical_specality":
            if not neo.MATCH(list(node_name)):
                print("Node exist")
                return
            else:
                # print("Creating")
                cmd = (
                    "CREATE (w:Medical_specality {name: $node_name}) "
                )
                temp = tx.run(cmd, label=label, node_name=node_name)
        elif label == "symptom":
            if not neo.MATCH(list(node_name)):
                print("Node exist")
                return
            else:
                # print("Creating")
                cmd = (
                    "CREATE (n:Symptom {name: $node_name}) "
                )
            temp = tx.run(cmd, label=label, node_name=node_name)

    def create_relation(self, node_1, node_2, relation):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_relation, node_1, node_2, relation)

    @staticmethod
    def _create_relation(tx, node_1, node_2, relation):

        # Check relation type

        cmd = (
            "MATCH "
            "(n:Medical_specality), "
            "(w:Symptom) "
            "where n.name = $node_1 AND w.name = $node_2 "
            "create p = (w)-[r:SYMPTOM]->(n) "
            "return p")
        temp = tx.run(cmd, node_1=node_1, node_2=node_2)

    def CREATE(self, sentence):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self.m_create, sentence)

    @staticmethod
    def m_create(tx, sentence):
        temp = sentence.lower()
        texts = temp.split()
        for i in range(0, len(texts) - 1):
            cmd = (
                "merge (w1:Word{name:$tx}) "
                "on create set w1.count = 1 on match set w1.count = w1.count +1 "
                "merge (w2:Word{name:$tx2}) "
                "on create set w2.count = 1 on match set w2.count = w2.count +1 "
                "merge (w1)-[r:NEXT]->(w2) "
                "on create set r.count =1 "
                "on match set r.count = r.count +1;"
            )
            # print(cmd)
            tx.run(cmd, sz=len(texts) - 2, tx=texts[i], tx2=texts[i + 1])

    def MATCH(self, key):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.m_match, key
            )
            return result

    @staticmethod
    def m_match(tx, key):
        cmd = (
            "MATCH (w:Word) "
            "where w.name = $key "
            "return *;"
        )
        temp = tx.run(cmd, key=key)
        return temp

    def UPDATE(self, new_properties):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.m_update, new_properties
            )

    @staticmethod
    def m_update(tx, new_properties):
        cmd = (
            "match (w:Word {name: $name}) "
            "set w = $new_prop")
        temp = tx.run(cmd, new_prop=new_properties, name=new_properties['name'])

    def DELETE(self, delete):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.m_delete, delete)

    @staticmethod
    def m_delete(tx, delete):
        if delete['cmd'] == 'delete_nodes':
            for node in delete['node']:
                cmd = (
                    "match (w:Word {name: $name})"
                    "detach delete w"
                )
                tx.run(cmd, name=node)
        elif delete['cmd'] == 'delete_all':
            cmd = (
                "match (n)"
                "detach delete n"
            )
            tx.run(cmd)
        elif delete['cmd'] == 'greater':
            cmd = (
                "match (w:Word) "
                "where w.count > $count "
                "detach delete w"
            )
            tx.run(cmd, count=delete['count'])
        elif delete['cmd'] == "equal":
            cmd = (
                "match (w:Word) "
                "where w.count = $count "
                "detach delete w"
            )
            tx.run(cmd, count=delete['count'])
        elif delete['cmd'] == "lesser":
            cmd = (
                "match (w:Word) "
                "where w.count < $count "
                "detach delete w"
            )
            tx.run(cmd, count=delete['count'])

    def match_check(self, key):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.result, key)
        return result

    @staticmethod
    def result(tx, key):
        cmd = (
            "match (w:Symptom {name: $key})-[:SYMPTOM]->(n) return n.name "
        )
        temp = tx.run(cmd, key=key)
        entire_result = []  # Will contain all the items
        for record in temp:
            entire_result.append(record.value())
        if len(entire_result) == 0:
            return False
        else:
            return entire_result
