import mysql.connector
import datetime


class MysqlConnector():
    def __init__(self):
        self.host = "127.0.0.1"
        self.database = "perco"
        self.port = "49001"
        self.username = "perco"
        self.password = "123"
        self.connection = None
        self.cursor = None

    def establish_connection(self):
        self.connection = mysql.connector.connect(host=self.host,
                                                  database=self.database,
                                                  user=self.username,
                                                  password=self.password,
                                                  port=self.port)
        self.cursor = self.connection.cursor()

    def generate_query_body_for_event(self):
        def _get_time_domain_for_event(delta_hours):
            datetime_now = datetime.datetime.now()
            datetime_start = datetime_now - datetime.timedelta(hours=delta_hours)
            sql_datetime_now = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
            sql_datetime_start = datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            print(sql_datetime_start, sql_datetime_now)
            return " WHERE e.db_time_label >= '%s' AND e.db_time_label <= '%s'" % (sql_datetime_start, sql_datetime_now)

        QUERY = "SELECT u.first_name, u.last_name, e.db_time_label FROM event e" \
                " LEFT JOIN user_card uc USING(identifier)" \
                " LEFT JOIN user u ON e.user_id = u.id"

        return QUERY + _get_time_domain_for_event(3)

    def execute_query(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    # def import_attendance(self, records):
    #     def _get_odoo_data()
