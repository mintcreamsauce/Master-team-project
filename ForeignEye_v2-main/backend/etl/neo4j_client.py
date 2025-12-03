import os
import atexit
from neo4j import GraphDatabase, Driver

class Neo4jConnection:
    def __init__(self):
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')
        
        if not all([uri, user, password]):
            print("⚠️ 경고: Neo4j 환경 변수(URI, USERNAME, PASSWORD)가 설정되지 않았습니다.")
            self.driver = None
        else:
            self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=300)

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(self, query):
        if not self.driver:
            print("✗ 오류: Neo4j 드라이버가 초기화되지 않아 쿼리를 실행할 수 없습니다.")
            return None
        
        with self.driver.session() as session:
            result = session.run(query)
            return result

# 전역 Neo4j 연결 인스턴스 생성
neo4j_conn = Neo4jConnection()

# 앱 종료 시 자동으로 연결이 닫히도록 등록
atexit.register(neo4j_conn.close)