def generate_sql(prompt):

    sql_query = "SELECT company_name, company_size FROM customers WHERE company_size = 'medium'"
    
    return sql_query