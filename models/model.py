import datetime

from Crypto.Hash import SHA256

from db_connection import DB

class DBBase(object):
    db = DB

    def __init__(self, _id):
        cls = self.__class__
        cls.db.execute("""
            SELECT * FROM {} WHERE _id = {}
        """.format(cls.table_name, _id))
        row = cls.db.fetchone()
        if not row:
            raise TypeError('No record was found with the _id {}'.format(_id))
        
        self.row = row
        self._id = _id

    @classmethod
    def get_by_id(cls, _id):
        return cls(_id)
    
    @classmethod
    def get_by_where(cls, where):
        cls.db.execute("""
            SELECT * FROM {} WHERE {}
        """.format(where))
        return cls.db.fetchall()

    def delete(self):
        cls = self.__class__
        cls.db.execute("""DELETE FROM {} WHERE _id = {}""".format(cls.table_name, self._id))

    @classmethod
    def delete_all(cls):
        cls.db.execute("""DELETE FROM {} WHERE _id > 0 """.format(cls.table_name))
        
    @classmethod
    def select_all(cls):
        cls.db.execute("""SELECT * FROM {}""".format(cls.table_name))
        return cls.db.fetchall()

    @classmethod
    def get_id_by_name(cls, name):
        cls.db.execute("""
            SELECT _id 
            FROM {}
            WHERE name = '{}'    
        """.format(cls.table_name, name))
        row = cls.db.fetchone()
        if row:
            return row[0]
        return None

    @classmethod
    def insert_new(cls, new_name):
        cls.db.execute("""
            INSERT INTO {}
            VALUES (DEFAULT, '{}')
        """.format(cls.table_name, new_name))

class Category(DBBase):
    table_name = 'categories'
    
class BudgetTyep(DBBase):
    table_name = 'budget_types'

class Marchant(DBBase):
    table_name = 'marchants'

class Transaction(DBBase):
    table_name = 'transactions'
    default_budget_type = 'monthly_grocery'

    @classmethod
    def insert(cls, amount, description, date, budget_type=None, category=None, marchant=None):

        if not budget_type:
            budget_type = 'DEFAULT'
        else:
            budget_type = Budget.get_id_by_name(budget_type)
            if not budget_type:
                raise TypeError('Invalid budget_type value')

        if not category:
            category = 'NULL'
        else:
            category  = Category.get_id_by_name(category)
            if not category:
                raise TypeError('Invalid category value')

        if not marchant:
            marchant = 'NULL'
        else:
            marchant = Marchant.get_id_by_name(marchant)
            if not marchant:
                raise TypeError('Invalid marchant value')

        cls.db.execute("""
            INSERT INTO transactions
            VALUES (DEFAULT, {0}, '{1}', {2}, {3}, {4}, CURRENT_TIMESTAMP, '{5}')
        """.format(amount, description, budget_type, category, marchant, date))
    
    @classmethod
    def get_by_month(cls, month, year=None):
        if not year:
            year = datetime.datetime.now().year 

        this_month = datetime.datetime(year=year, month=month, day=1)
        next_month = month + 1
        if next_month > 12:
            next_month = 1
            year += 1
        next_month = datetime.datetime(year=year, month=next_month, day=1)

        this_month_start = this_month.strftime('%m/%d/%Y') 
        next_month_start = next_month.strftime('%m/%d/%Y') 

        columns = [
            't.date',
            't.amount',
            'm.name',
            'c.name'
        ]

        select_fields = ' ,'.join(columns)

        cls.db.execute("""
            SELECT {} 
            FROM transactions t
            LEFT OUTER JOIN categories c ON t.category_id = c._id
            LEFT OUTER JOIN marchants m ON t.marchant_id = m._id
            JOIN budget_types b ON t.budget_type_id = b._id
            WHERE t.date >= '{}' AND t.date < '{}' AND b.name = '{}'
        """.format(select_fields, this_month_start, next_month_start, cls.default_budget_type))
        return cls.db.fetchall()


class User(DBBase):
    table_name = 'users'
    master_user = 'hiro'    

    @classmethod
    def insert_new_user(cls, username, password):
        sha256 = SHA256.new()
        pswd_hash = sha256.new(password).hexdigest()
        
        cls.db.execute("""
            INSERT INTO users (_id, username, password)
            VALUES (DEFAULT, '{}', '{}')
        """.format(username, pswd_hash))
        print cls.db.statusmessage

    @classmethod
    def auth_master_user(cls, password):
        cls.db.execute("""
            SELECT _id, password
            FROM users
            WHERE username = '{}' 
        """.format(cls.master_user))
        (user_id, db_password) = cls.db.fetchone()
        sha256 = SHA256.new()
        pswd_hash = sha256.new(password).hexdigest()

        if db_password == pswd_hash:
            token = generate_session_token()
            cls.db.execute("""
                INSERT INTO session_tokens 
                VALUES (DEFAULT, '{}', {})
            """.format(token, user_id)) 
            return token

        return None

    @classmethod
    def auth_master_user_session_token(cls, token):
        cls.db.execute("""
            SELECT s.token
            FROM session_tokens s
            JOIN users u
            ON u._id = s.user_id
            WHERE u.username = '{}'
        """.format(cls.master_user))
        valid_tokens = [row[0] for row in cls.db.fetchall() if row]
        return token in valid_tokens

# utils
def generate_session_token():
    import string, random
    token = ''
    letters = string.lowercase + string.digits
    for i in range(24):
       token += letters[random.randint(0,35)] 
    return token
