from db_connection import DB

sql_commands = {
    'creat_t': """
        CREATE TABLE transactions (
                _id SERIAL,
                amount integer,
                description text,
                budget_type integer,
                category integer,
                marchant integer,
                timestamp timestamp,
                date date,

                PRIMARY KEY (_id),
                FOREIGN KEY (budget_type) REFERENCES budget_types (_id),
                FOREIGN KEY (category) REFERENCES categories (_id),
                FOREIGN KEY (marchant) REFERENCES marchants (_id)
        )
        """,

    'default_budget_type': """
        ALTER TABLE transactions
        ALTER budget_type SET DEFAULT 1
    """,

    'create_c': """
        CREATE TABLE categories (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,
    'create_b':  """
        CREATE TABLE budget_types (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,
    'create_m':  """
        CREATE TABLE marchants (
                _id SERIAL,
                name varchar(250),
                PRIMARY KEY(_id)
        )
    """,

    'create_u':"""
        CREATE TABLE users (
            _id SERIAL,
            username varchar(50),
            password varchar(250),
            email_address varchar(250),
            google_auth_credential text,
            session_token varchar(250),
            PRIMARY KEY(_id)
        )
    """,

    'create_l':"""
        CREATE TABLE limits (
            _id SERIAL,
            budget_type integer,
            month integer,
            year integer,
            amount integer,
            result integer,
            PRIMARY KEY(_id),
            FOREIGN KEY (budget_type) REFERENCES budget_types (_id)
        )
    """,

    'seed_1': """
        INSERT INTO budget_types
        VALUES (DEFAULT, 'monthly_grocery')
    """,

    'seed_2': """
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
    'seed_3': """
        INSERT INTO marchants 
        VALUES 
        (DEFAULT, 'Costco'),
        (DEFAULT, 'Trader Joes'),
        (DEFAULT, 'Arco'),
        (DEFAULT, 'Target'),
        (DEFAULT, 'Kaiser')
    """,

    'seed_4': """
        INSERT INTO users (_id, username, password)
        VALUES (DEFAULT, 'hiro', 'f177b636530f8ee2919bd790531ce60e711ab9775a231fc4330e4e21090cc1d9')
    """
}

def main():
    for name, command in sql_commands.iteritems():
        DB.execute(command)
        print DB.statusmessage        

if __name__ == '__main__':
    main()
