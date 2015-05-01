from repository import Repository

__author__ = 'Haim'


class ChatMessageRepository(Repository):
    def __init__(self):
        Repository.__init__(self, 'mysql_chat_db')

    def insert_message_execute(self, **kwargs):
        sql_query = "INSERT INTO MESSAGE(message_col,user_id,send_date ) VALUES('%s','%s','%s')", [
            kwargs['message_col'], kwargs['user_id'], kwargs['send_date']]
        self.execute_query(sql_query)

    def read_message_execute(self, limit_num):
        sql_query = "select * from message ORDER BY message_id DESC Limit %d ", [limit_num]
        return self.execute_select_generator(sql_query)

    def delete_previous_message_execute(self, under_num_days):
        # sql_query = "DELETE from MESSAGE where MESSAGE.send_date < ADDDATE(NOW(),-%d)" , under_num_days
        self.execute_query("DELETE from MESSAGE where MESSAGE.send_date < SUBDATE(NOW(),%s)", [under_num_days])


class ChatUserRepository(Repository):
    def __init__(self):
        Repository.__init__(self, 'mysql_chat_db')

    def insert_user_execute(self, **kwargs):
        sql_query = "INSERT INTO USER(user_name ) VALUES('%s')", [kwargs['user_name']]
        self.execute_query(sql_query)

    def read_user_execute(self, user_name):
        sql_query = "SELECT user_id FROM USER WHERE user_name='%s'", [user_name]
        return self.execute_select_generator(sql_query)
