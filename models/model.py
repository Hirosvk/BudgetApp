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
    def delete_by_id(cls, _id):
        cls.db.execute("""DELETE FROM {} WHERE _id = {} """.format(cls.table_name, _id))

    @classmethod
    def delete_all(cls):
        cls.db.execute("""DELETE FROM {} WHERE _id > 0 """.format(cls.table_name))
        
    @classmethod
    def select_all(cls):
        cls.db.execute("""SELECT * FROM {}""".format(cls.table_name))
        return cls.db.fetchall()


    @classmethod
    def get_all_names(cls):
        cls.db.execute("""SELECT name FROM {}""".format(cls.table_name))
        return [row[0] for row in cls.db.fetchall()]

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
    
class BudgetType(DBBase):
    table_name = 'budget_types'

class Marchant(DBBase):
    table_name = 'marchants'

class Transaction(DBBase):
    table_name = 'transactions'
    default_budget_type = 'monthly_grocery'
    base_columns = [
        't.date',
        't.amount',
        'm.name',
        'c.name',
        'b.name',
        't.description',
        't._id'
    ]

    @classmethod
    def insert(cls, date=None, description=None, amount=None, budget_type=None, category=None, marchant=None):
        c = cls.get_fk_ids(budget_type, category, marchant)
        cls.db.execute("""
            INSERT INTO transactions
            VALUES (DEFAULT, {0}, '{1}', {2}, {3}, {4}, CURRENT_TIMESTAMP, '{5}')
        """.format(amount, description, c['budget_type_id'], c['category_id'], c['marchant_id'], date))
    
    @classmethod
    def get_by_month(cls, month, year=None, as_dict=True):
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

        select_fields = ' ,'.join(cls.base_columns)

        cls.db.execute("""
            SELECT {} 
            FROM transactions t
            LEFT OUTER JOIN categories c ON t.category_id = c._id
            LEFT OUTER JOIN marchants m ON t.marchant_id = m._id
            JOIN budget_types b ON t.budget_type_id = b._id
            WHERE t.date >= '{}' AND t.date < '{}'
        """.format(select_fields, this_month_start, next_month_start))
        result = cls.db.fetchall()
        if as_dict:
            return [cls.parse_row(row) for row in result]

        return result

    @classmethod
    def update_by_id(cls, _id, date=None, description=None, amount=None, budget_type=None, category=None, marchant=None):
        command = """
            UPDATE transactions
            SET"""
        columns_to_update = cls.get_fk_ids(budget_type, category, marchant)
        columns_to_update['amount'] = amount
        columns_to_update['date'] = date
        columns_to_update['description'] = description 
        
        columns = []
        for name, value in columns_to_update.iteritems():
            new_line = ''
            if isinstance(value, int) or value in ['NULL', 'DEFAULT']:
                new_line = name + " = " + str(value)
            elif isinstance(value, str) or isinstance(value, unicode):
                new_line = name + " = '" + value +"'"

            if value and new_line:
                columns.append(new_line)

        command += " " + ",".join(columns)
        command += "\nWHERE _id = {}".format(_id)
        cls.db.execute(command)
        print cls.db.statusmessage
        

    @classmethod
    def get_row_by_id(cls, _id, as_dict=True):
        select_fields = ' ,'.join(cls.base_columns)

        cls.db.execute("""
            SELECT {} 
            FROM transactions t
            LEFT OUTER JOIN budget_types b ON t.budget_type_id = b._id
            LEFT OUTER JOIN categories c ON t.category_id = c._id
            LEFT OUTER JOIN marchants m ON t.marchant_id = m._id
            WHERE t._id = {}
        """.format(select_fields, _id))
        result = cls.db.fetchone()

        if as_dict:
            return cls.parse_row(result)
        
        return result
            
    @classmethod
    def parse_row(cls, result=None):
        if not result:
            # for new row
            result = [None, None, None, None, None, None, None]

        result_dict = {}
       
        result_dict['_id'] = result[6] 
        result_dict['date'] = result[0].strftime('%Y-%m-%d') if isinstance(result[0], datetime.date) else ''
        result_dict['amount'] = result[1] or 0
        result_dict['marchant'] = result[2] or ''
        result_dict['category'] = result[3] or ''
        result_dict['budget_type'] = result[4] or ''
        result_dict['description'] = result[5] or ''
        
        return result_dict
        


    @classmethod
    def get_fk_ids(cls, budget_type_name, category_name, marchant_name):
        (budget_type_id, category_id, marchant_id) = (None, None, None)

        if not budget_type_name:
            budget_type_id = 'DEFAULT'
        else:
            budget_type_id = BudgetType.get_id_by_name(budget_type_name)
            if not budget_type_id:
                raise TypeError('Invalid budget_type value')

        if not category_name:
            category_id = 'NULL'
        else:
            category_id  = Category.get_id_by_name(category_name)
            if not category_id:
                raise TypeError('Invalid category value')

        if not marchant_name:
            marchant_id = 'NULL'
        else:
            marchant_id = Marchant.get_id_by_name(marchant_name)
            if not marchant_id:
                Marchant.insert_new(marchant_name)
                marchant_id = Marchant.get_id_by_name(marchant_name)
                
        
        return {
            'budget_type_id': budget_type_id,
            'category_id': category_id,
            'marchant_id': marchant_id
        }

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

class Limit(DBBase):
    table_name = "limits"
    default_b_type_name = 'monthly_grocery'

    @classmethod
    def get_amount_by_month(cls, month, year, budget_type_name=None):
        budget_type_name = budget_type_name or cls.default_b_type_name

        cls.db.execute("""
            SELECT l.amount 
            FROM limits l
            JOIN budget_types b ON l.budget_type_id = b._id
            WHERE l.month = {} AND l.year = {} AND b.name = '{}'
        """.format(month, year, budget_type_name))
        result = cls.db.fetchone()
        return result[0] if result else None
    
    @classmethod
    def get_id_by_month(cls, month, year, budget_type_name=None):   
        budget_type_name = budget_type_name or cls.default_b_type_name

        cls.db.execute("""
            SELECT l._id 
            FROM limits l
            JOIN budget_types b ON l.budget_type_id = b._id
            WHERE l.month = {} AND l.year = {} AND b.name = '{}'
        """.format(month, year, budget_type_name))
        result = cls.db.fetchone()
        return result[0] if result else None
 
    @classmethod
    def change_limit(cls, month, year, new_amount, budget_type_name=None):
        _id = cls.get_id_by_month(month, year, budget_type_name) 
        
        if not _id:
            cls.create_new_monthly_limit(month, year, new_amount, budget_type_name)
        else:
            cls.db.execute("""
                UPDATE limits
                SET amount = {}
                WHERE _id = {}
            """.format(new_amount, _id))

    @classmethod
    def create_new_monthly_limit(cls, month, year, amount, budget_type_name=None):
        budget_type_name = budget_type_name or cls.default_b_type_name
        budget_type_id = BudgetType.get_id_by_name(budget_type_name)

        cls.db.execute("""
            INSERT INTO limits
            VALUES (DEFAULT, {}, {}, {}, {}, NULL)
        """.format(budget_type_id, month, year, amount))
        

# utils
def generate_session_token():
    import string, random
    token = ''
    letters = string.lowercase + string.digits
    for i in range(24):
       token += letters[random.randint(0,35)] 
    return token


