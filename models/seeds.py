from db_connection import DB, conn

sql_commands = [ 

    """
        CREATE TABLE categories (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,
     """
        CREATE TABLE budget_types (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,
    """
        CREATE TABLE marchants (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,

    """
        CREATE TABLE users (
            _id SERIAL,
            username varchar(50),
            password varchar(250),
            email_address varchar(250),
            google_auth_credential text,
            PRIMARY KEY(_id)
        )
    """,
    """
        CREATE TABLE transactions (
                _id SERIAL,
                amount integer,
                description text,
                budget_type_id integer,
                category_id integer,
                marchant_id integer,
                timestamp timestamp,
                date date,

                PRIMARY KEY (_id),
                FOREIGN KEY (budget_type_id) REFERENCES budget_types (_id),
                FOREIGN KEY (category_id) REFERENCES categories (_id),
                FOREIGN KEY (marchant_id) REFERENCES marchants (_id)
        )
    """,

    """
        ALTER TABLE transactions
        ALTER budget_type_id SET DEFAULT 1
    """,

    """
        CREATE TABLE limits (
            _id SERIAL,
            budget_type_id integer,
            month integer,
            year integer,
            amount integer,
            result integer,
            PRIMARY KEY(_id),
            FOREIGN KEY (budget_type_id) REFERENCES budget_types (_id)
        )
    """,

    """
        ALTER TABLE limits 
        ALTER budget_type_id SET DEFAULT 1
    """,

    """
        CREATE TABLE session_tokens (
            _id SERIAL,
            token varchar(50),
            user_id integer,
            PRIMARY KEY(_id),
            FOREIGN KEY(user_id) REFERENCES users (_id)
        )

    """,

    """
        INSERT INTO budget_types
        VALUES (DEFAULT, 'monthly_grocery')
    """,

    """
        INSERT INTO categories 
        VALUES 
        (DEFAULT, 'grocery'),
        (DEFAULT, 'gas'),
        (DEFAULT, 'home_improvement'),
        (DEFAULT, 'fun'),
        (DEFAULT, 'kids'),
        (DEFAULT, 'medical'),
        (DEFAULT, 'car_maintenance'),
        (DEFAULT, 'generosity')
    """,
    """
        INSERT INTO marchants 
        VALUES 
        (DEFAULT, 'Costco'),
        (DEFAULT, 'Trader Joes'),
        (DEFAULT, 'Arco'),
        (DEFAULT, 'Target'),
        (DEFAULT, 'Kaiser')
    """,

    """
        INSERT INTO users (_id, username, password)
        VALUES (DEFAULT, 'hiro', 'f177b636530f8ee2919bd790531ce60e711ab9775a231fc4330e4e21090cc1d9')
    """,

    """
        INSERT INTO limits
        VALUES (DEFAULT, DEFAULT, 6, 2017, 700, NULL)
    """
]

def main():
    conn.autocommit = False
    for command in sql_commands:
        try:
            DB.execute(command)
        except:
            print 'rolling back...'
            conn.rollback()
            raise
        else:
            print DB.statusmessage        
   
    print 'commiting...'
    conn.commit() 

if __name__ == '__main__':
    main()
