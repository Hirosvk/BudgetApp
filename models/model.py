import datetime

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
            LEFT OUTER JOIN categories c ON t.category = c._id
            LEFT OUTER JOIN marchants m ON t.marchant = m._id
            JOIN budget_types b ON t.budget_type = b._id
            WHERE t.date >= '{}' AND t.date < '{}' AND b.name = '{}'
        """.format(select_fields, this_month_start, next_month_start, cls.default_budget_type))
        return cls.db.fetchall()

